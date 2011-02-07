
import src.server.vhosting as vhost
import unittest, sys

class TEST(unittest.TestCase):
	"""virtual hosting module test class"""

	def test1(self):
		"""create virtual hosting object"""
		obj = vhost.VDOM_vhosting()
		obj.set_site("123", "456")
		self.assertEqual("456", obj.get_site("123"))
		self.assertEqual(True, "123" in obj.get_sites())
		obj.set_site("123", None)
		self.assertEqual(None, obj.get_site("123"))
