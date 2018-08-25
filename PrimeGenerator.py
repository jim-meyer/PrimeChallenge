import itertools
import json
from multiprocessing import Pool as ThreadPool

import RedisClientFactory

# We can handle requests asynchronously via threads since the redis client is thread safe AND we are not accessing or
# altering variables shared across threads.
thread_pool = None


class PrimeGeneratorThreadPool(object):
	def __init__(self):
		self.thread_pool = ThreadPool()
		super().__init__()

	def __enter__(self):
		pass

	def __exit__(self, exception_type, exception_value, traceback):
		self.thread_pool.close()
		self.thread_pool.join()
		global thread_pool
		# TODO - Kind of cheesy to do this here. Hopefully can get back to clean this up a bit later.
		thread_pool = None

	def map(self, func, iterable, chunksize=None):
		return self.thread_pool.map(func, iterable, chunksize)


def start_thread_pool():
	"""
	Returns the thread pool that this code uses to generate prime numbers asynachronously.
	:return:
	"""
	global thread_pool
	thread_pool = PrimeGeneratorThreadPool()
	return thread_pool


def stop_thread_pool(pool):
	"""
	This just exists for symmetry with start_thread_pool(). It is not used since we use 'with' statements to manage
	the thread pool.
	:param pool:
	:return:
	"""
	global thread_pool
	thread_pool.close()
	thread_pool.join()
	thread_pool = None


# Based largely on code from https://hackernoon.com/prime-numbers-using-python-824ff4b3ea19
def _approach3(start, end):
	# Initialize a list
	primes = []
	for possiblePrime in range(start, end + 1):
		# Assume number is prime until shown it is not.
		isPrime = True
		for num in range(2, int(possiblePrime ** 0.5) + 1):
			if possiblePrime % num == 0:
				isPrime = False
				break
		if isPrime:
			primes.append(possiblePrime)
	return (primes)


def _generate_primes_between(start, end):
	"""
	Synchronously enerates all prime numbers between 'start' and 'end'
	:param start: int
	:param end: int
	:return: list of ints that are the requested prime numbers
	"""
	result = _approach3(start, end)
	return result


def _generate_primes_between_sync(start, end, redis_client, key_to_store_results_under):
	"""
	Starts the process of generating prime numbers between 'start' and 'end'.
	When the prime numbers are generated the results will be stored as a json string under the
	'key_to_store_results_under' using the specified redis client.
	:param start: int:
	:param end: int:
	:param redis_client: Redis client interface that support get(key) and set(key, value) semantics
	:param key_to_store_results_under: The key that the prime numbers will be stored under.
	:return:
	"""
	# We create the client here since for the multi-threading case (vs the multi-processing case) Python
	# can't pickle the object to marshal it to another thread.
	if redis_client is None:
		redis_client = RedisClientFactory.get_redis_client()

	primes = _generate_primes_between(start, end)
	# We store the job results as json for convenience of marshaling to/from redis
	primes_as_json = json.dumps(primes)
	redis_client.set(key_to_store_results_under, primes_as_json)
	return primes

def _generate_primes_between_sync_shim(*args, **kwargs):
	_generate_primes_between_sync(args[0]['start'], args[0]['end'], args[0]['redis_client'], args[0]['key_to_store_results_under'])


def generate_primes_between_async(start, end, redis_client, key_to_store_results_under):
#	_generate_primes_between_sync(start, end, redis_client, key_to_store_results_under)
	global thread_pool
	thread_pool.map(_generate_primes_between_sync_shim, [{'start': start, 'end': end, 'redis_client': None,
	                                                     'key_to_store_results_under': key_to_store_results_under}])
