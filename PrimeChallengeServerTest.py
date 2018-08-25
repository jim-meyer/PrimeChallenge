import unittest
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

	def test_startJobImpl_multicallers(self):
		with PrimeGenerator.start_thread_pool() as tp:
			jobId1 = PrimeChallengeServer.startJobImpl('1', '11')
			jobId2 = PrimeChallengeServer.startJobImpl('12', '17')
			jobId3 = PrimeChallengeServer.startJobImpl('18', '24')
		result1 = PrimeChallengeServer.queryJobImpl(jobId1)
		result2 = PrimeChallengeServer.queryJobImpl(jobId2)
		result3 = PrimeChallengeServer.queryJobImpl(jobId3)
		self.assertEqual('[1, 2, 3, 5, 7, 11]', result1)
		self.assertEqual('[13, 17]', result2)
		self.assertEqual('[19, 23]', result3)

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
