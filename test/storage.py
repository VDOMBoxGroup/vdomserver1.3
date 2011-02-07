
import unittest, os, sys, time
from StringIO import StringIO
import src.storage

class TEST(unittest.TestCase):
	"""storage module test class"""

	def test1(self):
		"""create storage"""
		s = src.storage.storage
		sys.stderr.write(str(s.keys()) + "\n")
		return True

	def test2(self):
		"""write and read value"""
		s = src.storage.storage
		s.write("somekey", "somevalue")
		self.assertEqual("somevalue", s.read("somekey"))

	def test3(self):
		"""remove value"""
		s = src.storage.storage
		s.erase("somekey")
		self.assertEqual(None, s.read("somekey"))
		sys.stderr.write(str(s.keys()) + "\n")

	def test4(self):
		"""write object"""
		obj = StringIO()	# test object
		s = src.storage.storage
		ret = s.write_object("testobj", obj)
		self.assertEqual(ret, True)

	def test5(self):
		"""read object"""
		s = src.storage.storage
		ret = s.read_object("testobj")
		self.assertNotEqual(ret, None)
		self.assertEqual(isinstance(ret, StringIO), True)

	def test6(self):
		"""remove object"""
		s = src.storage.storage
		s.erase("testobj")
		self.assertEqual(None, s.read("testobj"))
		sys.stderr.write(str(s.keys()) + "\n")

	def test7(self):
		"""async write test"""
		s = src.storage.storage
		s.write_async("async_key", "async_value")
		s.write_async("async_key_1", "async_value_1")
		time.sleep(1)
		self.assertEqual("async_value", s.read("async_key"))
		self.assertEqual("async_value_1", s.read("async_key_1"))
		s.erase("async_key")
		s.erase("async_key_1")
		self.assertEqual(None, s.read("async_key"))
		self.assertEqual(None, s.read("async_key_1"))
