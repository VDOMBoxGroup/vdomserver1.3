
import src.request.headers as headers
import unittest, sys

class TEST(unittest.TestCase):
	"""headers module test class"""

	def test1(self):
		"""push header"""
		args = {}
		h = headers.VDOM_headers(args)
		h.header("h1", "v1")
		self.assertEqual(h.header("h1"), "v1")

	def test2(self):
		"""add header"""
		args = {}
		h = headers.VDOM_headers(args)
		h.header("h1", "v1")
		h.header("h1", "v2", False)
		self.assertEqual(h.header("h1"), "v1;v2")

	def test3(self):
		"""remove header"""
		args = {}
		h = headers.VDOM_headers(args)
		h.header("h1", "v1")
		h.remove("h1")
		self.assertEqual(h.header("h1"), None)
