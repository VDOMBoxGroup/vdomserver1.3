
import src.request.arguments as args
import unittest

class TEST(unittest.TestCase):
	"""id module test class"""

	def test1(self):
		"""create request arguments"""
		arg = {'a':'b'}
		a = args.VDOM_request_arguments(arg)
		return a.arguments() and True
