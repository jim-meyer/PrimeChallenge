import redis



class RealRedisClient():
	"""
	The implementation that uses and actual redis server.
	"""
	def __init__(self):
		self.redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0)

	def get(self, key):
		return self.redis_conn.get(key)

	def set(self, key, value):
		self.redis_conn.set(key, value)


class FakeRedisClient():
	"""
	A simplistic redis-like implementation that is/was handy for testing before having a redis server stood up.
	"""
	def __init__(self):
		self.map = {}

	def get(self, key):
		result = None
		# Have to adhere to redis semantics whereby if a key can't be found None gets returned
		if key in self.map.keys():
			result = self.map[key]
		return result

	def set(self, key, value):
		self.map[key] = value


def get_redis_client():
	"""
	Returns a class that support redis-like 'get' and 'set' operations
	:return:
	"""
	return FakeRedisClient()
