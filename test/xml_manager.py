import unittest, sys

import src.xml.manager as manager
from src.storage.storage import VDOM_storage




try:
	manager.VDOM_xml_manager.get().register_type( "21" )
except: pass
try:
	manager.VDOM_xml_manager.get().register_type( "22" )
except: pass

class TEST(unittest.TestCase):
	"""xml manager module test class"""

	def test1(self):
		"""add application"""
		# create storage
		stor = VDOM_storage.get()
		# xml
		obj = manager.VDOM_xml_manager.get()
		try:
			obj.add_application_from_file("xml/app1.xml")
		except: pass
		app = obj.get_application("2")
		self.assertNotEqual(None, app)
		objects = app.get_objects()
		for o in objects:
			print objects[o].id, objects[o].name, objects[o].type, objects[o].value
			attrs = objects[o].get_attributes()
			for a in attrs:
				print attrs[a].name, attrs[a].value
			objects1 = objects[o].get_objects()
			for o1 in objects1:
				print objects1[o1].id, objects1[o1].name, objects1[o1].type, objects1[o1].value
		return True

	def test2(self):
		"""test type"""
		# create storage
		stor = VDOM_storage.get()
		# xml
		obj = manager.VDOM_xml_manager.get()
		tp = obj.get_type("21")
		self.assertNotEqual(None, tp)

	def test3(self):
		"""create application"""
		obj = manager.VDOM_xml_manager.get()
		appid = obj.create_application()
		sys.stderr.write(appid + "\n")
		app = obj.get_application(appid)
		app.set_info("Name", "Test application")
		app.set_info("Password", "secret")
		app.sync()
		self.assertEqual(app.password, "secret")

	def test4(self):
		"""search object"""
		obj = manager.VDOM_xml_manager.get()
		ret = obj.search_object("2", "42")
		sys.stderr.write(str(ret) + "\n")
