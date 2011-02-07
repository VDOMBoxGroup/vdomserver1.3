import unittest, sys

import src.file_access
import src.resource
from src.config import VDOM_CONFIG


class TEST(unittest.TestCase):
	"""resource module test"""
	

	def test1(self):
		"""writing new file"""
		src.resource.resource_manager.write("id","res001","file.txt","lksfjhjksdfhn\nkjadwoijd\n")
		return True
	def test2(self):
		"""geting resource list"""
		src.resource.resource_manager.list()
		return True
	def test3(self):
		"""writing one more file with same name"""
		VDOM_CONFIG[ "Multi-linked-resourse-test" ] = src.resource.resource_manager.write("id","res002","file.txt","lksfjhjksdfhn\nkjadwoijd\n")
		return True
	def test4(self):
		"""linking existing file"""
		src.resource.resource_manager.link("id","res003","file.txt",VDOM_CONFIG[ "Multi-linked-resourse-test" ])
		return True
	def test5(self):
		"""one more resource list"""
		src.resource.resource_manager.list()
		return True
	def test6(self):
		"""deleting file with two links"""
		src.resource.resource_manager.delete("id","res003")
		return True
	def test7(self):
		"""deleting same file"""
		src.resource.resource_manager.delete("id","res002")
		return True
	def test8(self):
		"""deleting file"""
		src.resource.resource_manager.delete("id","res001")
		return True
	def test9(self):
		"""final resource list"""
		src.resource.resource_manager.list()
		return True
	