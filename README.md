| **`Documentation`** |
|-----------------|

# PrimeChallenge
PrimeChallenge is a REST service that will calculate all the prime number between two integer values asynchronously. The caller can the poll the server for the results. If some caller has already made a request for a give start/end integer pair then future callers will get their answers very quickly since the results are cached in a redis server.

## Requirements
This server was initially developed on Windows. But it should support Linux equally well. The instructions include information on both OSes.

It is perhaps easiest to use this on Linux where it is easy to run redis and the PrimeChallenge server locally on a single box.

Flask must be installed to run the web service. See http://flask.pocoo.org/docs/1.0/installation/.

A redis server must also be available. Installation instructions are below if needed.

## Installation
These instructions assume you've cloned the git repo to C:\git\PrimeChallenge on Windows or ~/git/PrimeChallenge on Linux. 

Create a Python virtual environment so the based python install isn't altered.

On a Windows machine:

    cd C:\temp
    python -m venv PrimeChallenge
    PrimeChallenge\scripts\activate.bat
    pip install Flask
    pip install redis

Or Linux:

    cd ~/temp
    python -m venv PrimeChallenge
    source PrimeChallenge/bin/activate
    pip install Flask
    pip install redis


Install redis since it is required by this project. On a Linux machine follow the instructions at https://redis.io/topics/quickstart:

**CAUTION: The insructions below will run redis so that it listens on all external NICs, not just the loopback address. This has security ramifications but was safe for me to do on my private home network.**

    wget http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    cd redis-stable
    make
    redis-server
    make test
    ./src/redis-server --protected-mode no

## Starting the PrimeChallenge server
The server listens on port 8080 by default to avoid conflicts in case a server is already running on port 80.

On the Windows machine:

    cd C:\git\PrimeChallenge
    StartSever.bat --redisServerIP <<IP address of redis server>>

Or to have the server accessible from the non-loopback address:

    StartSever.bat --redisServerIP <<IP address of redis server>> --listenerAddress 0.0.0.0

Linux:

    cd ~/git/PrimeChallenge
    ./StartSever.sh --redisServerIP <<IP address of redis server>> --listenerAddress 127.0.0.1


## Using the PrimeChallenge server

Examples using bash. Be sure and update the PRIME_SERVER variable to point to the IP address of the server. I used cygwin on the same Windows machine that was running the server. But this should also work from a remote Linux machine if the IP address is updated accordingly.

Here's an example script that shows that fetching results from a pre-warmed cache works. Run this script and look at the last line. It should show that the second similar request was processed much faster than the first because the results were cached in redis by the first request already.

_Be sure and use the appropriate IP address for the prime challenge server as the argument to the script._

    ./RunColdVsWarmCache_test.sh 127.0.0.1

Here's another script that gives a good idea that multiple requests are being handled in parallel.

    ./ProveParallelismTest.sh 127.0.0.1


## Running The Unit Tests
The unit tests require a running redis server or else several unit tests will fail. (Perhaps calling these "unit tests" is not quite accurate but I haven't invested in solving the inherent difficulties of trying to provide thread safe fakes that unit tests can use.)
From the project's directory on the Windows machine:

    RunUnitTests.bat <IP address of redis server>

Or for Linux:

    ./RunUnitTests.sh <IP address of redis server>

## Security Considerations
The server does not support SSL. And no authentication is being done. So Client1 can see Client2's jobs and vice versa.

In the examples above the server listens on port 8080 by default on the loopback address (127.0.0.1). If the user needs to use a non-loopback address to enable access from other machines then beware that port 8080 is open to attackers. And there are undoubtedly security vulnerabilities that are exposed by this minimal HTTP server implementation.

The instructions above also start a redis server that listens on port 6379 by default *and makes that redis server available to other machines on the network*. By default this redis server is not hardened against attacks.

For unexpected conditions, especially 500 internal server errors, the server emits the entire stack trace of the exception. This was done to aid in troubleshooting. Production servers should not spit out such juicy fodder that could be leveraged by attackers.

Each new successful '/Start' request returns a random number as the 'job ID' that can be used in later '/Query' requests. It is theoretically possible that Client1 could issue a request that gets a job ID that just happens to be the same as another client's previously posted job ID. Thus Client1 could overwrite the other client's results. This is, of course, solvable given time.


## Notable Implementation Details, Design Choices
If client requests status of a job while that job is running we return 204 "No Content" instead of returning the prime numbers generated for the job so far. Changing this behavior could be easily accomplished by periodically saving the accumulated results in PrimeGenerator.py::_approach3().

The way parameters are passed in the URLs used by the '/Start' endpoint is a bit atypical. Chalk that up to me not diving deeper into flask to get this working better.


## Known Problems


## TODO


## Credits
Portions of this project used code from sources on the internet. They are listed here:

The function used to generate prime numbers was obtained from:
 - https://hackernoon.com/prime-numbers-using-python-824ff4b3ea19
I could have used http://www.sympy.org/en/index.html instead but found the former first.
