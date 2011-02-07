
import src.util.id as theid
import unittest, sys, random

class TEST(unittest.TestCase):
	"""id module test class"""

	def test1(self):
		"""create id"""
		random.seed()
		obj = theid.VDOM_id()
		newid = obj.new()
		sys.stderr.write(newid + "\n")

	def test2(self):
		"""generate random string"""
		obj = theid.VDOM_id()
		newid = obj.random_string(10)
		sys.stderr.write(newid + "\n")

	def test3(self):
		"""guid2mod test"""
		newid = theid.guid2mod("0-0-0")
		self.assertEqual(newid, "module_0_0_0")
