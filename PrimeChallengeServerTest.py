import unittest
import json
from http import HTTPStatus

import PrimeChallengeServer
import PrimeGenerator
import HTTPStatusException

NON_INT_VALUE = 'foo'
NEGATIVE_INT_VALUE = '12'
IMPOSSIBLE_JOB_ID = 'zzz_this_never_used_in_real_world_zzz'

class PrimeChallengeServerTestCase(unittest.TestCase):
	def test_startJobImpl_simple(self):
		with PrimeGenerator.start_thread_pool() as tp:
			self.assertTrue(type(str), type(PrimeChallengeServer.startJobImpl('1', '11')))

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
		with PrimeGenerator.start_thread_pool() as tp:
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
		with PrimeGenerator.start_thread_pool() as tp:
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

	def test_startJobImpl_big_prime(self):
		# The purpose of this test is just to cause multiple CPUs to stay busy long enough to feel comfortable that
		# we really are operating asynchronously.
		# So watch Task Manager as this is running and make sure that >1 CPU is busy while this runs.
		with PrimeGenerator.start_thread_pool() as tp:
			jobId1 = PrimeChallengeServer.startJobImpl('1', '123456')
			jobId2 = PrimeChallengeServer.startJobImpl('2', '123456')
			jobId3 = PrimeChallengeServer.startJobImpl('3', '123456')
			result1 = self.queryJobImplSync(jobId1)
			arr = json.loads(result1)
			self.assertEqual(len(arr), 11602)
			result2 = self.queryJobImplSync(jobId2)
			arr = json.loads(result2)
			self.assertEqual(len(arr), 11601)
			result3 = self.queryJobImplSync(jobId3)
			arr = json.loads(result3)
			self.assertEqual(len(arr), 11600)

	def test_startJobImpl_exceptions(self):
		with PrimeGenerator.start_thread_pool() as tp:
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
