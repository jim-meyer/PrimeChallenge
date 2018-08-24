| **`Documentation`** |
|-----------------|

**PrimeChalleng** is a REST service that TODO.

## Requirements
This server was developed on Windows and hence the instructions for installing it and its prerequisites are tailoered to Windows. Getting this to run on Linux should be straightforward though since it's written in Python and relies on just a few Python pip modules that readily work on Linux as well as Windows.

Flask must be installed to run the web service. See http://flask.pocoo.org/docs/1.0/installation/.


## Installation
Create a Python virtual environment so the based python install isn't altered.

cd C:\temp
python -m venv PrimeChallenge
PrimeChallenge\scripts\activate.bat
pip install Flask
pip install redis


## Starting the PrimeChallenge server
The server listens on port 8080 by default to avoid conflicts in case a server is already running on port 80.
cd C:\temp\PrimeChallenge\StartSever.bat


## Using the PrimeChallenge server
Examples using bash:
jobid=$(curl --request POST "http://127.0.0.1:8080/Start/1,3")
curl --request GET "http://127.0.0.1:8080/Query/${jobid}"


## Errors


## Running Uhe Unit Tests
From the project's directory:

python -m unittest discover -p "*Test.py"

## Security Considerations
The server does not support SSL. And no authentication is being done. So Client1 and see Client2's jobs and vice versa.

The server listens on port 8080 by default on all available NICs. So port 8080 is open to requests from other machines. This allows easily testing this server from other (non-Windows) machines if the user so chooses.

The server also starts a redis server that listens on port 6379 by default. However this server listens only on the server's loopback address and thus should not be open to (ab)use from other machines.

For unexpected conditions, especially 500 internal server errors, the server emits the entire stack trace of the exception. This was done to aid in troubleshooting. Production servers should not spit out such juicy fodder that could be leveraged by attackers.

Each new successful '/Start' request returns a random number as the 'job ID' that can be used in later '/Query' requests. It is theoretically possible that Client1 could issue a request that gets a job ID that just happens to be the same as another client's previously posted job ID. Thus Client1 could overwrite the other client's results. This is, of course, solvable given time.

## Notable Implementation Details, Design Choices
If client requests status of a job while that job is running should we return the prime numbers generated for the job so far?
Pros: It's good to get feedback and the progress of the job.
Cons: This exposes some level of DoS vulnerability.

There are some unimplemented unit tests that would benefit from mocking but I didn't go that far with testing.

The way parameters are passed in the URLs used by the '/Start' endpoint is a bit atypical. Chalk that up to me not diving deeper into flask to get this working better.

## TODO
Cache results so Client2 using 3,11 gets the results from Client1's 3,11 calculations 
Move unit tests into their own directory.
Handle requests asynchronously

## Credits
Portions of this project used code from sources on the internet. They are listed here:

The function used to generate prime numbers was obtained from:
 - https://hackernoon.com/prime-numbers-using-python-824ff4b3ea19
I could have used http://www.sympy.org/en/index.html instead but found the former first.
