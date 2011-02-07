
import src.util.semaphore as sem
import unittest

class TEST(unittest.TestCase):
	"""semaphore module test class"""

	def test_create(self):
		""" Create semaphore """
		m = sem.VDOM_semaphore(10)
		m.lock()
		m.unlock()
		return True

	def test_create1(self):
		""" Create semaphore with counter 1"""
		m = sem.VDOM_semaphore(1)
		m.lock()
		m.unlock()
		return True
