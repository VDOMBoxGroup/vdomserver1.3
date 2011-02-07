"""base structure parser module"""

import base64, string

class VDOM_parser:
	"""parser class"""

	def __init__(self):
		"""constructor"""
		pass

	def create(self, xml_obj):
		"""constructor"""
		# NOTE: derived classes must fill self.parse_list and self.info_map before calling this
		for e_name in self.parse_list:
			o = xml_obj.get_child_by_name(e_name)
			if not o:
				o = xml_object(name=e_name.capitalize())
				xml_obj.children.append(o)
				#debug("  created element \"%s\"" % e_name)
			setattr(self, e_name + "_element", o)
			getattr(self, "parse_" + e_name)(o)
		self.validate_attributes()

	def get_xml_as_string(self):
		"""get xml document as string"""
		# override
		pass

	def parse_information(self, xml_obj):
		"""parse information section"""
		for child in xml_obj.children:
			if child.lname in self.info_map:
				data = child.value
				exec "self." + self.info_map[child.lname][0] + " = " + (self.info_map[child.lname][1] % "data")
				setattr(self, "__" + self.info_map[child.lname][0] + "_original", getattr(self, self.info_map[child.lname][0]))
		for attr in self.info_map.keys():
			attrname = self.info_map[attr][0]
			if not hasattr(self, attrname):
				setattr(self, attrname, "")
				setattr(self, "__" + attrname + "_original", "")

	def parse_resources(self, xml_obj):
		"""parse resources section"""
		for child in xml_obj.children:
			self.parse_resource(child)
		# remove resources node from memory
		xml_obj.delete()

	def parse_databases(self, xml_obj):
		"""parse databases section"""
		for child in xml_obj.children:
			self.parse_database(child)
		# remove databases node from memory
		xml_obj.delete()

	def parse_resource(self, xml_obj):
		"""parse one resource"""
		try:
			res_id = xml_obj.attributes["id"]
			res_name = xml_obj.attributes["name"]
			res_type = xml_obj.attributes["type"]
			# unbase64
			bindata = base64.b64decode(xml_obj.value.strip())
			# save resource - call overrided method
			self.save_resource(res_id, res_type, res_name, bindata)
		except KeyError:
			raise VDOM_exception_parse("resource format error")

	def parse_database(self, xml_obj):
		"""parse one database"""
		try:
			db_id = xml_obj.attributes["id"]
			db_name = xml_obj.attributes["name"]
			db_type = xml_obj.attributes["type"]
			bindata = None
			if db_type == "xml":
				bindata = xml_obj.toxml()
			else:
				# unbase64
				bindata = base64.b64decode(xml_obj.value.strip())
			# save database
			attributes = {
				"id" : db_id,
				"name" : db_name,
				"owner": self.id,
				"type": db_type
				}
			src.database.database_manager.add_database(self.id, attributes, bindata)
		except KeyError:
			raise VDOM_exception_parse("database format error")

	def save_resource(self, res_id, res_type, res_name, data):
		"""method to save resource"""
		# override
		pass

	def validate_attributes(self):
		"""check if required attributes are present"""
		for attr_name in self.required_attributes:
			try:
				getattr(self, attr_name)
			except AttributeError:
				raise VDOM_exception_parse("attribute \"%s\" not defined" % attr_name)

import src.database
from src.xml.xml_object import xml_object
from src.util.exception import *
