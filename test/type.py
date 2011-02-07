
import src.xml.type as thetype
import unittest, sys
from xml.dom.minidom import parse

class TEST(unittest.TestCase):
	"""xml type module test class"""

	def test1(self):
		"""create type object"""
		doc = parse("xml/type.xml") # parse an XML file
		obj = thetype.VDOM_type(doc)
		self.assertEqual(1, obj.dynamic)
