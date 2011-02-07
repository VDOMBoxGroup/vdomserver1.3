
import src.request.cookies as cookies
import unittest

class TEST(unittest.TestCase):
	"""cookies module test class"""

	def test1(self):
		"""push cookie"""
		args = {}
		h = cookies.VDOM_cookies(args)
		h.cookie("h1", "v1")
		self.assertEqual(h.cookie("h1"), "v1")

	def test2(self):
		"""add cookie"""
		args = {}
		h = cookies.VDOM_cookies(args)
		h.cookie("h1", "v1")
		h.cookie("h1", "v2", False)
		self.assertEqual(h.cookie("h1"), "v1;v2")

	def test3(self):
		"""remove cookie"""
		args = {}
		h = cookies.VDOM_cookies(args)
		h.cookie("h1", "v1")
		h.remove("h1")
		self.assertEqual(h.cookie("h1"), None)

	def test4(self):
		"""create set-cookie header"""
		args = {}
		h = cookies.VDOM_cookies(args)
		h.cookie("h1", "v1")
		h.cookie("h2", "v2")
		self.assertEqual(h.get_string(), "h2=v2; h1=v1;")
