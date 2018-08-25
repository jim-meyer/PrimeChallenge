import argparse
import json
from http import HTTPStatus
import random
from flask import Flask

import PrimeGenerator
import RedisClientFactory
import HTTPStatusException

# help prevent replay attempts
random.seed()

app = Flask(__name__)
redis_client = None


def safe_int_cast(str):
	"""
	A simple convenience function to make code a bit more concise
	"""
	try:
		result = int(str)
	except:
		result = None
	return result


def get_key(start, end):
	"""
	We cache the results of calculations in redis so if another caller makes an identical request we can quickly
	return the results. The function creates the key that is used to refer to cached requests by the request's parameters.
	:param start:
	:param end:
	:return: string:
	"""
	return '{0},{1}'.format(start, end)


# Two functions that made unit tests easier and cleaner to write
def set_redis_client(new_redis_client):
	global redis_client
	redis_client = new_redis_client


def get_redis_client():
	global redis_client
	return redis_client


def startJobImpl(start, end):
	"""
	Starts a job that computes the prime numbers between 'start' and 'end'
	:param start: string: The start number indicates the starting number (inclusive) for the start of the prime list
	:param end: string: The end number indicates the ending number (inclusive) for the end of the prime list
	:return: string: a job ID that can be passed to queryJobImpl()
	"""
	# Run sanity checks and return suitable error if the arguments are not ints
	startInt = safe_int_cast(start)
	if startInt is None:
		raise HTTPStatusException.HTTPStatusException('{0} must be an int'.format(start), HTTPStatus.BAD_REQUEST)

	endInt = safe_int_cast(end)
	if endInt is None:
		raise HTTPStatusException.HTTPStatusException('{0} must be an int'.format(end), HTTPStatus.BAD_REQUEST)

	if endInt < startInt:
		raise HTTPStatusException.HTTPStatusException('First argument ({0}) must be less than the second argument ({1})'
		                                              .format(startInt, endInt), HTTPStatus.BAD_REQUEST)

	if startInt < 0:
		raise HTTPStatusException.HTTPStatusException('First argument ({0}) must be greater than zero'
		                                              .format(startInt), HTTPStatus.BAD_REQUEST)

	job_id = random.randint(0, 0x7fffffff)
	job_id_str = '{:02x}'.format(job_id)
	key = get_key(start, end)
	# First we store the job ID along with the request's parameters
	client = get_redis_client()
	client.set(job_id_str, key)

	# Do a "quick" check to see if we've already cached the primes in redis. If we have then there is no sense
	# calculating them again. "Quick" is in quotes since there may very well be some cases where it's faster to
	# simply generate the primes rather than hit the network and redis and back. But until more analysis is done
	# this seems reasonable.
	primes_as_json = client.get(key)
	if primes_as_json is None:
		# Now we generate the prime numbers asynchronously. The asyn processing will update redis by storing the
		# prime numbers associated with the start/end parameters. That way a '/Query' can look up the parameters
		# by job ID, then look up the prime numbers based on those parameters.
		PrimeGenerator.generate_primes_between_async(startInt, endInt, client, key)
	else:
		pass

	return job_id_str


def queryJobImpl(jobId):
	primes_as_json = ''
	client = get_redis_client()
	job_args_key = client.get(jobId)
	if job_args_key is None:
		raise HTTPStatusException.HTTPStatusException('Job {0} could not be found'.format(jobId), HTTPStatus.NOT_FOUND)
	else:
		primes_as_json = client.get(job_args_key)
		if primes_as_json is None:
			raise HTTPStatusException.HTTPStatusException('The prime numbers for {0} are still being calculated'
			                                              .format(job_args_key), HTTPStatus.NO_CONTENT)
	# This silly little dance is because the redis client returns b'some string' when everything else
	# expects 'some string'. Since assertEqual(b'some string', 'some string') fails it was easiest to fix this here.
	# Besides, this could potentially cause other issues to real clients.
	obj1 = json.loads(primes_as_json)
	canonical_json = json.dumps(obj1)
	return canonical_json


@app.route('/Start/<start>,<end>', methods=['POST'])
@app.errorhandler(HTTPStatus.BAD_REQUEST)
@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def StartJob(start, end):
	try:
		result = startJobImpl(start, end)
		http_status = HTTPStatus.OK
	except HTTPStatusException.HTTPStatusException as ex:
		result = ex.msg
		http_status = ex.http_status
	except Exception as ex:
		result = 'An unexpected error occurred: {0}'.format(str(ex))
		http_status = HTTPStatus.INTERNAL_SERVER_ERROR
	return result, http_status


@app.route('/Query/<jobId>', methods=['GET'])
@app.errorhandler(HTTPStatus.NOT_FOUND)
@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def QueryJob(jobId):
	try:
		result = queryJobImpl(jobId)
		http_status = HTTPStatus.OK
	except HTTPStatusException.HTTPStatusException as ex:
		result = ex.msg
		http_status = ex.http_status
	except Exception as ex:
		result = 'An unexpected error occurred: {0}'.format(str(ex))
		http_status = HTTPStatus.INTERNAL_SERVER_ERROR
	return result, http_status


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-r', '--redisServerIP', default='127.0.0.1',
	                    help='The IP Address of the redis server that will store the cached results of requests')
	parser.add_argument('-l', '--listenerAddress', default='127.0.0.1',
	                    help='The IP address of that this server will listen on. If you need this server to be ' \
	                    'reachable from another host use 0.0.0.0 but understand the security implications first.')
	args = parser.parse_args()

	print('Listening on {0}'.format(args.listenerAddress))
	print('Using redis server at {0}'.format(args.redisServerIP))

	# Set up our access to the redis server
	RedisClientFactory.register_redis_server(args.redisServerIP)
	set_redis_client(RedisClientFactory.get_redis_client())

	# Start the thread pool that will handle the async prime number generation
	with PrimeGenerator.start_thread_pool() as tp:
		# Start the flask web server
		app.run(host=args.listenerAddress, port=8080)
	# The thread pool has shut down nicely already via the 'with'/__exit__() protocol
