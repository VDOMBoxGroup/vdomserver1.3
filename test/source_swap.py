import unittest, sys

from src.source_manager.swap import *

from src.config import VDOM_CONFIG


class TEST(unittest.TestCase):
	"""source swap module test"""


	def test1(self):
		"""testing pop and push methods"""
		text = "1+1"
		VDOM_source_swap.get().push( "id", "container_id", "file.py", text )
		newtext = VDOM_source_swap.get().pop( "id", "container_id")
		if( newtext != text ):
			sys.stderr.write( "Error: text doesnot matched" );
			return False
		return True





		
