import unittest
import PrimeGenerator
import RedisClientFactory

class PrimeGeneratorTestCase(unittest.TestCase):
	def test__generate_primes_between(self):
		test_redis_client = RedisClientFactory.get_dummy_redis_client();

		# start and end are the same
		self.assertEqual(list([1]), PrimeGenerator._generate_primes_between_sync(1, 1, test_redis_client, 'Test1'))
		self.assertEqual(list([7]), PrimeGenerator._generate_primes_between_sync(7, 7, test_redis_client, 'Test2'))
		self.assertEqual(test_redis_client.get('Test1'), '[1]')
		self.assertEqual(test_redis_client.get('Test2'), '[7]')

		# start and end are different
		self.assertEqual(list([1, 2, 3, 5]), PrimeGenerator._generate_primes_between_sync(1, 5, test_redis_client, 'Test3'))
		self.assertEqual(list([5, 7, 11, 13]), PrimeGenerator._generate_primes_between_sync(5, 13, test_redis_client, 'Test4'))
		self.assertEqual(list([5, 7, 11, 13]), PrimeGenerator._generate_primes_between_sync(4, 14, test_redis_client, 'Test5'))
		self.assertEqual(test_redis_client.get('Test3'), '[1, 2, 3, 5]')
		self.assertEqual(test_redis_client.get('Test4'), '[5, 7, 11, 13]')
		self.assertEqual(test_redis_client.get('Test5'), '[5, 7, 11, 13]')

		# Make sure list comparison is order sensitive
		self.assertEqual(list([1, 2]), PrimeGenerator._generate_primes_between_sync(1, 2, test_redis_client, 'DontCare'))
		self.assertNotEqual(list([2, 1]), PrimeGenerator._generate_primes_between_sync(1, 2, test_redis_client, 'DontCare'))


	def test__generate_primes_between_negative(self):
		test_redis_client = RedisClientFactory.get_dummy_redis_client();

		self.assertEqual([], PrimeGenerator._generate_primes_between_sync(13, 1, test_redis_client, 'Test1'))
		self.assertEqual(test_redis_client.get('Test1'), '[]')

		# Disabled for now. We catch negative numbers at a higher level.
		#self.assertEqual([], PrimeGenerator._generate_primes_between_sync(-13, 5, test_redis_client, 'Test2'))
		#self.assertEqual(test_redis_client.get('Test2'), '[]')


if __name__ == '__main__':
	unittest.main()
