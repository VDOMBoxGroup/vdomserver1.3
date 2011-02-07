
import src.log.log as thelog
import unittest, sys

class TEST(unittest.TestCase):
	"""log module test class"""

	def test1(self):
		"""create log"""
		obj = thelog.VDOM_log("_log.xml")
		return True
