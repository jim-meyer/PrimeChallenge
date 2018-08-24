import unittest
import PrimeGenerator

class PrimeGeneratorTestCase(unittest.TestCase):
	def test__generate_primes_between(self):
		# start and end are the same
		self.assertEqual(list([1]), PrimeGenerator._generate_primes_between(1, 1))
		self.assertEqual(list([7]), PrimeGenerator._generate_primes_between(7, 7))

		# start and end are different
		self.assertEqual(list([1, 2, 3, 5]), PrimeGenerator._generate_primes_between(1, 5))
		self.assertEqual(list([5, 7, 11, 13]), PrimeGenerator._generate_primes_between(5, 13))
		self.assertEqual(list([5, 7, 11, 13]), PrimeGenerator._generate_primes_between(4, 14))

		# Make sure list comparison is order sensitive
		self.assertEqual(list([1, 2]), PrimeGenerator._generate_primes_between(1, 2))
		self.assertNotEqual(list([2, 1]), PrimeGenerator._generate_primes_between(1, 2))


	def test__generate_primes_between_negative(self):
		# TODO
		self.assertEqual([], PrimeGenerator._generate_primes_between(13, 1))


if __name__ == '__main__':
	unittest.main()
