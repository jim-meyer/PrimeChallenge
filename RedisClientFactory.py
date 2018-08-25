import redis


g_redis_server_ip = None
g_use_fake_redis_client = False

class RealRedisClient():
	"""
	The implementation that uses and actual redis server.
	"""
	def __init__(self):
		global g_redis_server_ip
		self.redis_conn = redis.StrictRedis(host=g_redis_server_ip, port=6379, db=0)

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


def register_redis_server(redis_server_ip):
	"""
	We rely on somebody telling this code which redis server to use by calling this function.
	:param redis_server_ip:
	"""
	global g_redis_server_ip
	g_redis_server_ip = redis_server_ip


def get_redis_client():
	"""
	Returns a class that support redis 'get' and 'set' operations.
	If we're running unit tests we return a redis-like implementation that doesn't require a redis server.
	:return:
	"""
	global g_use_fake_redis_client
	if g_use_fake_redis_client:
		result = FakeRedisClient()
	else:
		result = RealRedisClient()
	return result


def use_fake_redis_client():
	"""
	Used by unit tests where we don't want to require a real redis server to be available.
	:return:
	"""
	global g_use_fake_redis_client
	g_use_fake_redis_client = True
