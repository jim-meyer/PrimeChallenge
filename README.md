| **`Documentation`** |
|-----------------|

**PrimeChallenge** is a REST service that TODO.

## Requirements
This server was developed on Windows and hence the instructions for installing it and its prerequisites are tailoered to Windows. Getting this to run on Linux should be straightforward though since it's written in Python and relies on just a few Python pip modules that readily work on Linux as well as Windows.

Flask must be installed to run the web service. See http://flask.pocoo.org/docs/1.0/installation/.


## Installation
Create a Python virtual environment so the based python install isn't altered.

On a Windows machine:

`cd C:\temp
python -m venv PrimeChallenge
PrimeChallenge\scripts\activate.bat
pip install Flask
pip install redis
`
Install redis since it is required by this project. On a Linux machine follow the instructions at https://redis.io/topics/quickstart:

**CAUTION: The insructions below will run redis so that it listens on all external NICs, not just the loopback address. This has security ramifications but was safe for me to do on my private home network.**

`wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
redis-server
make test
./src/redis-server --protected-mode no
`

## Starting the PrimeChallenge server
The server listens on port 8080 by default to avoid conflicts in case a server is already running on port 80.

On the Windows machine:

`cd C:\temp\PrimeChallenge\StartSever.bat`


## Using the PrimeChallenge server

Examples using bash:

`set +x
PRIME_SERVER=127.0.0.1
jobid=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,3")
echo ${jobid}
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}"

STARTTIME=$(date +%s)
jobid=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,1234567")
echo ${jobid}
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}"
ENDTIME=$(date +%s)
echo "It took $(($ENDTIME - $STARTTIME)) seconds get the prime numbers from a cold cache state"

STARTTIME=$(date +%s)
jobid=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,1234567")
echo ${jobid}
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}"
ENDTIME=$(date +%s)
echo "It took $(($ENDTIME - $STARTTIME)) seconds get the prime numbers from a warm cache state"

`

## Errors


## Running The Unit Tests
From the project's directory on the Windows machine:

`python -m unittest discover -p "*Test.py"`

You may see errors like the following. These are benign.

`ResourceWarning: unclosed <socket.socket fd=688, family=AddressFamily.AF_INET
`


## Security Considerations
The server does not support SSL. And no authentication is being done. So Client1 and see Client2's jobs and vice versa.

The server listens on port 8080 by default on all available NICs. So port 8080 is open to requests from other machines. This allows easily testing this server from other (non-Windows) machines if the user so chooses.

The server also starts a redis server that listens on port 6379 by default. However this server listens only on the server's loopback address and thus should not be open to (ab)use from other machines.

For unexpected conditions, especially 500 internal server errors, the server emits the entire stack trace of the exception. This was done to aid in troubleshooting. Production servers should not spit out such juicy fodder that could be leveraged by attackers.

Each new successful '/Start' request returns a random number as the 'job ID' that can be used in later '/Query' requests. It is theoretically possible that Client1 could issue a request that gets a job ID that just happens to be the same as another client's previously posted job ID. Thus Client1 could overwrite the other client's results. This is, of course, solvable given time.

## Notable Implementation Details, Design Choices
If client requests status of a job while that job is running we return 204 "No Content" instead of returning the prime numbers generated for the job so far. Changing this behavior could be easily accomplished by periodically saving the accumulated results in PrimeGenerator.py::_approach3().

The way parameters are passed in the URLs used by the '/Start' endpoint is a bit atypical. Chalk that up to me not diving deeper into flask to get this working better.

## TODO
Handle requests asynchronously

Move unit tests into their own directory.

## Credits
Portions of this project used code from sources on the internet. They are listed here:

The function used to generate prime numbers was obtained from:
 - https://hackernoon.com/prime-numbers-using-python-824ff4b3ea19
I could have used http://www.sympy.org/en/index.html instead but found the former first.
