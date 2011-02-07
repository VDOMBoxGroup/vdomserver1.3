

import unittest, sys
from xml.dom.minidom import parse
import src.xml
import src.xml.application as app

class TEST(unittest.TestCase):
	"""xml application module test class"""

	def test1(self):
		"""create application object"""
		doc = parse("xml/app1.xml") # parse an XML file
		obj = app.VDOM_application(src.xml.xml_manager, doc)
		self.assertEqual("2", obj.id)
