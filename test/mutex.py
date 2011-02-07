
import src.util.mutex as mutex
import unittest
import thread
import time
import sys

class TEST(unittest.TestCase):
	"""mutex module test class"""

	def test_create(self):
		""" Create mutex and dispose it later """
		m = mutex.VDOM_mutex()
		m.lock()
		del(m)
		return True

	def test_named(self):
		"""test named mutex"""
		man = mutex.mutex_manager
		mm = mutex.VDOM_named_mutex("name test")
		mm.lock()
		ret = man.count("name test")
		mm.unlock()
		self.assertEqual(1, ret)
		ret = man.count("name test")
		self.assertEqual(0, ret)

	def test_multithread(self):
		"""test named mutexes with multithreaded access"""
		man = mutex.mutex_manager
		thread.start_new_thread(self.my_thread, ('1', ))
		thread.start_new_thread(self.my_thread, ('2', ))
		time.sleep(3)

	def my_thread(self, ident):
		"""test thread function"""
		mm = mutex.VDOM_named_mutex("name1")
		sys.stderr.write(ident + " Try lock... ")
		mm.lock()
		sys.stderr.write(ident + " locked... ")
		time.sleep(1)
		sys.stderr.write(ident + " unlock\n")
		mm.unlock()
