"""This module implements interface to VDOM memory; used by scripts"""

import sys
import src.xml

class VDOM_memory_interface(object):
	"""This class is used as interface to VDOM memory"""

	def __init__(self, request_object):
		"""constructor"""
		self.__request = request_object

	def create_object(self):
		pass

	def get_object(self):
		pass

	def delete_object(self):
		pass

	def set_object_attribute(self):
		pass

	def set_object_value(self):
		pass

	def set_object_script(self):
		pass

	def search_object(self, obj_id):
		app = src.xml.xml_manager.get_application(self.__request.application_id)
		object=app.search_object(obj_id)
		return object
