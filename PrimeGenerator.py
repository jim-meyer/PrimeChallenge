import json

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

def generate_primes_between(start, end, redis_client, key_to_store_results_under):
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
	primes = _generate_primes_between(start, end)
	# We store the job results as json for convenience of marshaling to/from redis
	primes_as_json = json.dumps(primes)
	redis_client.set(key_to_store_results_under, primes_as_json)
