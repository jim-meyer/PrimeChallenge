import json
import multiprocessing as mp

import RedisClientFactory


# We can handle requests asynchronously via threads since the redis client is thread safe AND we are not accessing or
# altering variables shared across threads.
thread_pool = None


def debug_log(msg):
#	print(msg)
	pass


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
	debug_log('Entering _generate_primes_between_sync({0}, {1}, <redis client>, {2})'.format(start, end, key_to_store_results_under))
	if redis_client is None:
		redis_client = RedisClientFactory.get_redis_client()

	primes = _generate_primes_between(start, end)
	# We store the job results as json for convenience of marshaling to/from redis
	primes_as_json = json.dumps(primes)
	redis_client.set(key_to_store_results_under, primes_as_json)
	debug_log('Exiting _generate_primes_between_sync({0}, {1}, <redis client>, {2})'.format(start, end, key_to_store_results_under))
	return primes


def _generate_primes_between_sync_shim(*args, **kwargs):
	debug_log('Entering _generate_primes_between_sync_shim()')
	_generate_primes_between_sync(args[0]['start'], args[0]['end'], args[0]['redis_client'], args[0]['key_to_store_results_under'])
	debug_log('Exiting _generate_primes_between_sync_shim()')


def _generate_primes_between_sync_shim2(start, end, redis_server_ip, key_to_store_results_under):
	debug_log('Entering _generate_primes_between_sync_shim2({0}, {1}, {2}, {3})'.format(start, end, redis_server_ip, key_to_store_results_under))
	RedisClientFactory.register_redis_server(redis_server_ip)
	redis_client = RedisClientFactory.get_redis_client_for_ip(redis_server_ip)
	_generate_primes_between_sync(start, end, redis_client, key_to_store_results_under)
	debug_log('Exiting _generate_primes_between_sync_shim2({0}, {1}, {2}, {3})'.format(start, end, redis_server_ip, key_to_store_results_under))


def generate_primes_between_async(start, end, redis_client, key_to_store_results_under):
	# This is here just in case it helps to change things to be synchronous for debugging purposes
#	_generate_primes_between_sync(start, end, redis_client, key_to_store_results_under)
	debug_log('Entering generate_primes_between_async()')
	redis_server_ip = RedisClientFactory.get_redis_server_ip()
	p = mp.Process(target=_generate_primes_between_sync_shim2, args=(start, end, redis_server_ip, key_to_store_results_under,))
	p.start()
	debug_log('Exiting generate_primes_between_async()')
