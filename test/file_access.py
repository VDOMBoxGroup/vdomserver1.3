import unittest, sys

from src import file_access
import src.file_access
from src.config import VDOM_CONFIG


class TEST(unittest.TestCase):
	"""file access module test"""


	def test1(self):
		"""file path generating"""
		src.file_access.file_manager.get_path( src.file_access.application_xml, "id", None, None )
		src.file_access.file_manager.get_path( src.file_access.global_type, None, None, "object.xml" )
		src.file_access.file_manager.get_path( src.file_access.cache, "id", None, "cache.py" )
		src.file_access.file_manager.get_path( src.file_access.resource, "id", None, "image.jpg" )
		src.file_access.file_manager.get_path( src.file_access.object_resource, "id", "objid", "image.jpg" )
		return True


	def test2(self):
		"""write test"""
		#src.file_access.file_manager.write( file_access.application_xml, "id", None, "test" )
		src.file_access.file_manager.write( file_access.global_type, None, None, "object.xml", "test" )
		src.file_access.file_manager.write( file_access.cache, "id", None, "cache.py", "test" )
		src.file_access.file_manager.write( file_access.resource, "id", None, "image.jpg", "test" )
		src.file_access.file_manager.write( file_access.object_resource, "id", "objid", "image.jpg", "test" )



	def test3(self):
		"""test exists function"""
		if src.file_access.file_manager.exists( file_access.application_xml, "id", None, None ): sys.stderr.write( "yes " )
		else: sys.stderr.write( "no " )

		if src.file_access.file_manager.exists( file_access.global_type, None, None, "object.xml" ): sys.stderr.write( "yes " )
		else: sys.stderr.write( "no " )
	
		if src.file_access.file_manager.exists( file_access.cache, "id", None, "cache.py" ): sys.stderr.write( "yes " )
		else: sys.stderr.write( "no " )

		if src.file_access.file_manager.exists( file_access.resource, "id", None, "image.jpg" ): sys.stderr.write( "yes " )
		else: sys.stderr.write( "no " )
		
		if src.file_access.file_manager.exists( file_access.object_resource, "id", "objid", "image.jpg" ): sys.stderr.write( "yes " )
		else: sys.stderr.write( "no " )
		
		return True
	



	def test4(self):
		"""read test"""
		src.file_access.file_manager.read( file_access.application_xml, "id", None, None )
		src.file_access.file_manager.read( file_access.global_type, None, None, "object.xml" )
		src.file_access.file_manager.read( file_access.cache, "id", None, "cache.py" )
		src.file_access.file_manager.read( file_access.resource, "id", None, "image.jpg" )
		src.file_access.file_manager.read( file_access.object_resource, "id", "objid", "image.jpg" )

		
	def test5(self):
		"""delete test"""
		#src.file_access.file_manager.delete( file_access.application_xml, "id", None, None )
		src.file_access.file_manager.delete( file_access.global_type, None, None, "object.xml" )
		src.file_access.file_manager.delete( file_access.cache, "id", None, "cache.py" )
		src.file_access.file_manager.delete( file_access.resource, "id", None, "image.jpg" )
		src.file_access.file_manager.delete( file_access.object_resource, "id", "objid","image.jpg" )

	def test6(self):
		"""write-exists-read test"""
		text = "text"
		src.file_access.file_manager.write( file_access.resource, "id", None, "image2.jpg", text )
		if( not src.file_access.file_manager.exists( file_access.resource, "id", None, "image2.jpg" ) ):
			sys.stderr.write( "error! file does not exist" )

		read_text = src.file_access.file_manager.read( file_access.resource, "id", None, "image2.jpg" )
		if( text != read_text ):
			sys.stderr.write( "error! files content does not match " )
		src.file_access.file_manager.delete( file_access.resource, "id", None, "image2.jpg" )

	def test7(self):
		"""clear test"""
		src.file_access.file_manager.clear( file_access.resource, "id", None)
		
