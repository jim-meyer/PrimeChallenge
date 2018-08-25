import os
import unittest
import json
from http import HTTPStatus

import PrimeChallengeServer
import PrimeGenerator
import HTTPStatusException
import RedisClientFactory

NON_INT_VALUE = 'foo'
NEGATIVE_INT_VALUE = '12'
IMPOSSIBLE_JOB_ID = 'zzz_this_never_used_in_real_world_zzz'

class PrimeChallengeServerTestCase(unittest.TestCase):
	def test_startJobImpl_simple(self):
		self.assertTrue(type(str), type(PrimeChallengeServer.startJobImpl('1', '11')))

	def setUp(self):
		# These tests require a real redis client since the fake redis client doesn't work across threads/processes
#		RedisClientFactory.use_fake_redis_client()
		redis_server_ip = os.environ.get('REDIS_SERVER_IP')
		RedisClientFactory.register_redis_server(redis_server_ip)
		PrimeChallengeServer.set_redis_client(RedisClientFactory.get_redis_client())

	def tearDown(self):
#		RedisClientFactory.use_fake_redis_client(False)
		PrimeChallengeServer.set_redis_client(None)

	def assertEqualJson(self, json1, json2):
		obj1 = json.loads(json1)
		obj2 = json.loads(json2)
		self.assertEqual(obj1, obj2)

	def queryJobImplSync(self, jobId):
		while True:
			try:
				result = PrimeChallengeServer.queryJobImpl(jobId)
				break
			except HTTPStatusException.HTTPStatusException as ex:
				if ex.http_status == HTTPStatus.NO_CONTENT:
					continue
				raise
		return result

	def test_startJobImpl_multicallers(self):
		jobId1 = PrimeChallengeServer.startJobImpl('1', '11')
		jobId2 = PrimeChallengeServer.startJobImpl('12', '17')
		jobId3 = PrimeChallengeServer.startJobImpl('18', '24')
		result1 = self.queryJobImplSync(jobId1)
		result2 = self.queryJobImplSync(jobId2)
		result3 = self.queryJobImplSync(jobId3)
		self.assertEqual('[1, 2, 3, 5, 7, 11]', result1)
		self.assertEqual('[13, 17]', result2)
		self.assertEqual('[19, 23]', result3)

	def test_startJobImpl_big_prime(self):
		jobId1 = PrimeChallengeServer.startJobImpl('1', '1234566')
		jobId2 = PrimeChallengeServer.startJobImpl('12', '17')
		jobId3 = PrimeChallengeServer.startJobImpl('18', '24')
		result2 = self.queryJobImplSync(jobId2)
		result3 = self.queryJobImplSync(jobId3)
		self.assertEqual('[13, 17]', result2)
		self.assertEqual('[19, 23]', result3)
		result1 = self.queryJobImplSync(jobId1)
		arr = json.loads(result1)
		self.assertEqual(len(arr), 95361)

	def test_startJobImpl_exceptions(self):
		# First arg not <= second arg
		with self.assertRaises(HTTPStatusException.HTTPStatusException) as context:
			PrimeChallengeServer.startJobImpl('5', '3')
		self.assertEqual(context.exception.http_status, HTTPStatus.BAD_REQUEST)
		self.assertIn('5', context.exception.msg)
		self.assertIn('3', context.exception.msg)

		# First arg not an int
		with self.assertRaises(HTTPStatusException.HTTPStatusException) as context:
			PrimeChallengeServer.startJobImpl(NON_INT_VALUE, '5')
		self.assertEqual(context.exception.http_status, HTTPStatus.BAD_REQUEST)
		self.assertIn(NON_INT_VALUE, context.exception.msg)

		# Second arg not an int
		with self.assertRaises(HTTPStatusException.HTTPStatusException) as context:
			PrimeChallengeServer.startJobImpl('5', NON_INT_VALUE)
		self.assertEqual(context.exception.http_status, HTTPStatus.BAD_REQUEST)
		self.assertIn(NON_INT_VALUE, context.exception.msg)

		# First arg not an < 0
		with self.assertRaises(HTTPStatusException.HTTPStatusException) as context:
			PrimeChallengeServer.startJobImpl(NEGATIVE_INT_VALUE, '5')
		self.assertEqual(context.exception.http_status, HTTPStatus.BAD_REQUEST)
		self.assertIn(NEGATIVE_INT_VALUE, context.exception.msg)

	def test_queryJobImpl(self):
		# Note that test_startJobImpl_multicallers() tests this function for the most part
		pass

	def test_queryJobImpl_exceptions(self):
		with self.assertRaises(HTTPStatusException.HTTPStatusException) as context:
			PrimeChallengeServer.queryJobImpl(IMPOSSIBLE_JOB_ID)
		self.assertEqual(context.exception.http_status, HTTPStatus.NOT_FOUND)
		self.assertIn(IMPOSSIBLE_JOB_ID, context.exception.msg)

if __name__ == '__main__':
	unittest.main()
