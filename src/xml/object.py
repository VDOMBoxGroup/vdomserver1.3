"""XML object module"""

import sys, re, SOAPpy

rexp = re.compile(r"\#res\((?P<guid>[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12})\)", re.IGNORECASE)

def on_attr_change(obj, old_value, new_value, app_id):
	# remove links to previously used resources
	_ret = rexp.findall(old_value)
	_ret1 = rexp.findall(new_value)
	ret = filter(lambda x: x not in _ret1, _ret)
	ret1 = filter(lambda x: x not in _ret, _ret1)
	for res_id in ret:
		if res_id in obj.resources:
			obj.resources[res_id] -= 1
			if obj.resources[res_id] <= 0:
				del(obj.resources[res_id])
				attributes = {"id" : res_id}
				if src.resource.resource_manager.check_resource(app_id, attributes):
					src.resource.resource_manager.delete_resource(obj.id, res_id)
	# add links to newly used resources
	for res_id in ret1:
		attributes = {"id" : res_id}
		if src.resource.resource_manager.check_resource(app_id, attributes):
			src.resource.resource_manager.add_resource(app_id, obj.id, attributes, None)
			if res_id not in obj.resources:
				obj.resources[res_id] = 0
			obj.resources[res_id] += 1


class descriptor(object):

	def __init__(self, name):
		self.__name = name

	def __get__(self, instance, owner):
		if self.__name in instance:
			return instance[self.__name].value
		else: raise AttributeError, self.__name

	def __set__(self, instance, value):
		if self.__name in instance:
			instance.object.set_attribute(self.__name, value)
		else: raise AttributeError, self.__name

	def __delete__(self, instance):
		raise AttributeError, self.__name


class attribute_container(dict):

	def __init__(self, obj):
		"""constructor"""
		self.object = obj

	def __setattr__(self, name, value):
		if name in self or "object" == name:
			dict.__setattr__(self, name, value)
		else: raise AttributeError, name

	def __delattr__(self, name):
		raise AttributeError, name


class VDOM_object(object):
	"""XML object class"""

	parse_list = ["attributes", "actions", "languages"]

	valid_attributes = ["objects", "objects_list", "objects_by_name", "attributes", "copy_objects",
				"actions", "application", "doc", "parent", "type", "id", "name", "xml_obj",
				"attributes_element", "objects_element", "resources",
				"dynamic", "types", "containers", "libraries",
				"optimization_priority", "order", "_VDOM_object__sem",
				"toplevel", "has_copy", "original_name", "actions_element", "languages","languages_element"]

	def __init__(self, app):
		"""constructor"""
		try:
			l = int(system_options["object_amount"])
			if "1" != system_options["server_license_type"] and app.xml_manager.obj_count >= l:
				raise VDOM_exception_lic(_("License exceeded"))
		except VDOM_exception, e:
			raise
		self.objects = {}
		self.objects_list = []
		self.objects_by_name = {}	# map of all child objects + this object
		self.attributes = attribute_container(self)
		self.copy_objects = []	# list of ids of copy objects targeting this one
		self.resources = {}	# map resource id to the number of links to this resource

		self.actions = {"name": {}, "id": {}}	# map name/id : VDOM_server_action object
		self.application = app
		self.parent = None
		self.toplevel = None	# link to the top-level container object
		self.has_copy = 0	# if object has copy inside (only for toplevel objects)
		self.languages = {}

		# semaphore used to lock VDOM object for modifications
		self.__sem = VDOM_semaphore()

		increase_objects_count(app)

	def __repr__(self):
		return "VDOM object (name='%s' id='%s')" % (self.name, self.id)

	def __str__(self):
		return repr(self)

	def get_all_children(self):
		# works only for top level objects
		r = []
		m = self.application.get_all_objects()
		for a in m:
			if m[a].toplevel is self:
				r.append(a)
		return r

	def __setattr__(self, name, value):
		if name in VDOM_object.valid_attributes:
			object.__setattr__(self, name, value)
		else:
			raise AttributeError, name

	def __delattr__(self, name):
		if name in VDOM_object.valid_attributes:
			object.__delattr__(self, name)
		else: raise AttributeError, name

	def has_attribute(self, name):
		"""test if object has some attribute"""
		return name in self.attributes

	def parse(self, xml_obj):
		"""parse object"""
		self.xml_obj = xml_obj
		for child in xml_obj.children:
			if child.lname in VDOM_object.parse_list:
				getattr(self, "parse_"+child.lname)(child)
				setattr(self, child.lname+"_element", child)
		# add 'onload' action if it's not here
		if 0 == len(self.actions["name"]) and 1 != self.type.container:
			_id = str(src.util.uuid.uuid4())
			self.actions["name"]["onload"] = VDOM_server_action("", _id, "", "", "", "onload")
			self.actions["id"][_id] = self.actions["name"]["onload"]

			action = """<Action ID="%s" Name="onload" Top="" Left="" State=""><![CDATA[]]></Action>""" % _id
			xml_obj = xml_object(srcdata=action.encode("utf-8"))
			actions = self.xml_obj.get_child_by_name("Actions")
			actions.append_as_copy(xml_obj)
			xml_obj.delete()

	def parse_attributes(self, xml_obj):
		"""parse object attributes"""
		self.attributes_element = xml_obj
		# load default values for attributes
		type_attr = self.type.get_attributes()
		for attr_name in type_attr.keys():
			if hasattr(self.attributes, attr_name):
				raise AttributeError, attr_name
			attr = VDOM_attribute(attr_name, type_attr[attr_name].default_value, None)	# for default attributes the node is None cause it doesn't exist in application xml
			self.attributes[attr_name] = attr
			if attr_name not in attribute_container.__dict__:
				setattr(attribute_container, attr_name, descriptor(attr_name))
		# load attributes from xml
		for child in xml_obj.children:
			if "attribute" == child.lname:
				name = child.attributes["name"]
				if name not in self.attributes:
					debug("Unknown attribute '%s' of '%s' object ignored" % (name, self.type.name))
					continue
				attr = VDOM_attribute(name, child.get_value_as_xml(), child)
				self.attributes[name] = attr

	def parse_actions(self, xml_obj):
		"""parse object server actions section"""
		if 1 == self.type.container:
			return
		_onload = False
		for s_node in xml_obj.children:
			if "action" == s_node.lname:
				name = s_node.attributes["name"]
				_id = s_node.attributes["id"] = s_node.attributes["id"].lower()
				_top = s_node.attributes["top"]
				_left = s_node.attributes["left"]
				_state = s_node.attributes["state"]
				code = s_node.value.strip()
				if "onload" == name.lower():
					_onload = True
				self.actions["name"][name] = VDOM_server_action(code, _id, _top, _left, _state, name)
				self.actions["id"][_id] = self.actions["name"][name]
		if not _onload:
			_id = str(src.util.uuid.uuid4())
			self.actions["name"]["onload"] = VDOM_server_action("", _id, "", "", "", "onload")
			self.actions["id"][_id] = self.actions["name"]["onload"]

			action = """<Action ID="%s" Name="onload" Top="" Left="" State=""><![CDATA[]]></Action>""" % _id
			xml_obj = xml_object(srcdata=action.encode("utf-8"))
			actions = self.xml_obj.get_child_by_name("Actions")
			actions.append_as_copy(xml_obj)
			xml_obj.delete()

	def parse_languages(self, xml_obj):
		"""parse object languages"""
		self.languages_element = xml_obj
		for child in xml_obj.children:
			#if child..nodeType != Node.ELEMENT_NODE:
			#	continue
			if "Language" == child.name:
				code = child.attributes["Code"]
				if code not in self.languages:
					self.languages[code] = {}
				for _child in child.children:
					if "Sentence" == _child.name:
						sent_id = _child.attributes["ID"]
						self.languages[code][sent_id] = _child.value


	def set_actions(self, xml_obj):
		if 1 == self.type.container:
			return
		if not src.security.acl_manager.session_user_has_access2(self.application.id, self.id, src.security.modify_object):
			raise VDOM_exception_sec(_("Modifying object is not allowed"))
		self.__sem.lock()
		try:
			self.actions = {"name": {}, "id": {}}
			self.parse_actions(xml_obj)
			#debug(str(self.actions_element))
			if hasattr(self, "actions_element"):
				self.actions_element.delete()
			self.actions_element = self.xml_obj.append_as_copy(xml_obj)
			# invalidate
			self.__do_invalidate(self)
			self.__do_invalidate1(self)
		finally:
			self.__sem.unlock()

	def create_action(self, actionname, value):
		if 1 == self.type.container:
			return
		if not src.security.acl_manager.session_user_has_access2(self.application.id, self.id, src.security.modify_object):
			raise VDOM_exception_sec(_("Modifying object is not allowed"))
		if not is_valid_identifier(actionname):
			raise SOAPpy.faultType(name_error, _("Incorrect server action name"), "")
		self.__sem.lock()
		try:
			_id = str(src.util.uuid.uuid4())
			self.actions["name"][actionname] = VDOM_server_action(value, _id, "", "", "", actionname)
			self.actions["id"][_id] = self.actions["name"][actionname]

			action = """<Action ID="%s" Name="%s" Top="" Left="" State=""><![CDATA[%s]]></Action>""" % (_id, actionname, value)

			xml_obj = xml_object(srcdata=action.encode("utf-8"))
			actions = self.xml_obj.get_child_by_name("Actions")
			actions.append_as_copy(xml_obj)

			xml_obj.delete()

			# invalidate
			self.__do_invalidate(self)
			self.__do_invalidate1(self)
		finally:
			self.__sem.unlock()
		return _id;

	def delete_action(self, actionid):
		if not src.security.acl_manager.session_user_has_access2(self.application.id, self.id, src.security.modify_object):
			raise VDOM_exception_sec(_("Modifying object is not allowed"))
		if actionid not in self.actions["id"]:
			# action_id_error to errors.py ?
			raise SOAPpy.faultType(object_id_error, _("No such server action"), _("<Error><ActionID>%s</ActionID></Error>") % actionid)

		self.__sem.lock()
		try:
			actions = self.xml_obj.get_child_by_name("Actions")

			# finding action
			for child in actions.children:
				if "Action" == child.name and child.attributes["ID"] == actionid:
					actions.children.remove(child)
					break;

			del self.actions["name"][ self.actions["id"][actionid].name ]
			del self.actions["id"][actionid]

			# invalidate
			self.__do_invalidate(self)
			self.__do_invalidate1(self)
		finally:
			self.__sem.unlock()

	def rename_action(self, actionid, new_actionname):
		if not src.security.acl_manager.session_user_has_access2(self.application.id, self.id, src.security.modify_object):
			raise VDOM_exception_sec(_("Modifying object is not allowed"))

		if actionid not in self.actions["id"]:
			raise SOAPpy.faultType(object_id_error, _("No such server action"), _("<Error><ActionID>%s</ActionID></Error>") % actionid)		

		if not is_valid_identifier(new_actionname):
			raise SOAPpy.faultType(name_error, _("Incorrect server action name"), _("<Error><ActionName>%s</ActionName></Error>") % new_actionname)

		for action in self.actions["name"]:
			if action == new_actionname:
				raise SOAPpy.faultType(name_error, _("The name is already in use"), _("<Error><ActionName>%s</ActionName></Error>") % new_actionname)

		self.__sem.lock()
		try:
			#self.actions["id"][actionid].cache = None

			actions = self.xml_obj.get_child_by_name("Actions")

			for child in actions.children:
				if "Action" == child.name and child.attributes["ID"] == actionid:
					child.attributes["Name"] = new_actionname
					break;

			old_actionname = self.actions["id"][actionid].name
			del self.actions["name"][old_actionname]
			self.actions["id"][actionid].name = new_actionname
			self.actions["name"][new_actionname] = self.actions["id"][actionid]

			# invalidate
			self.__do_invalidate(self)
			self.__do_invalidate1(self)
		finally:
			self.__sem.unlock()

	def set_action(self, actionid, actionvalue):
		if not src.security.acl_manager.session_user_has_access2(self.application.id, self.id, src.security.modify_object):
			raise VDOM_exception_sec(_("Modifying object is not allowed"))

		if actionid not in self.actions["id"]:
			raise SOAPpy.faultType(object_id_error, _("No such server action"), _("<Error><ActionID>%s</ActionID></Error>") % actionid)		

		self.__sem.lock()
		try:
			actionname = self.actions["id"][actionid].name

			self.actions["id"][actionid].cache = None
			self.actions["name"][actionname].cache = None

			actions = self.xml_obj.get_child_by_name("Actions")

			for child in actions.children:
				if "Action" == child.name and child.attributes["ID"] == actionid:
					child.value = actionvalue
					break;

			self.actions["id"][actionid].code = actionvalue
			self.actions["name"][ self.actions["id"][actionid].name ].code = actionvalue

			# invalidate
			self.__do_invalidate(self)
			self.__do_invalidate1(self)
		finally:
			self.__sem.unlock()	

	def get_objects(self):
		"""get list of inner objects"""
		return self.objects

	def get_objects_list(self):
		"""get list of objects in the order they appear in xml"""
		return self.objects_list

	def get_objects_by_name(self):
		"""get map of objects by name"""
		return self.objects_by_name

	def get_attributes(self):
		"""get list of object attributes"""
		return self.attributes

	def get_attribute(self, name):
		"""get object attribute"""
		if name in self.attributes:
			return self.attributes[name].value
		raise AttributeError, name

	def set_attributes(self, attr, do_compute=True):
		values = {};
		for name in attr:
			v = self.set_attribute_ex(name, attr[name], do_compute) 
			#if attribute changed returns {"value": value, "old_value": old_value} 
			#else return None
			if v:
				values[name] = v

		#call attribute changing handler with multiply attributes
		src.source.dispatcher.dispatch_handler(self.application.id, self.id, "set_attr", values)

		self.__do_invalidate(self)
		src.request.request_manager.get_request().container_id = self.toplevel.id
		if do_compute:
			src.engine.engine.compute(self.application, self, self.parent)

	def set_attribute_ex(self, name, value, do_compute=True):
		"""set attribute value"""
		# this method doesn't clear source code and doesn't dispatch handlers and doesn't call compute
		# but set_attributes does all these things
		if not src.security.acl_manager.session_user_has_access2(self.application.id, self.id, src.security.modify_object):
			raise VDOM_exception_sec(_("Modifying object is not allowed"))
		if name not in self.attributes:
			return
		if not isinstance(value, basestring):
			value = str(value)
		# re
#		if "" != self.type.attributes[name].regexp:
#			if not re.compile(self.type.attributes[name].regexp).match(value):
#				raise SOAPpy.faultType(attr_value_error, _("Attribute value error"), "<Error><ObjectID>%s</ObjectID><Attribute>%s</Attribute></Error>" % (self.id, name))

		attr = self.attributes[name]
		_value = self.application.test4res(value, None)
		# check if value changed
		old_value = attr.value
		if old_value == _value:
			return
		self.__sem.lock()
		try:
			if not attr.xml_obj:	# this attribute was created from default value - create node in application xml document
				x = xml_object(name="Attribute")
				self.attributes_element.children.append(x)
				x.attributes["Name"] = name
				attr.xml_obj = x
			attr.xml_obj.value = value

			on_attr_change(self, attr.original_value, value, self.application.id)

			attr.original_value = value
			attr.value = _value

			return { "value":_value, "old_value":old_value }
		finally:
			self.__sem.unlock()

	def set_attribute(self, name, value, do_compute=True):
		"""set attribute value"""
		return self.set_attributes({name : value}, do_compute)

	def set_name(self, value):
		"""set object name"""
		if not src.security.acl_manager.session_user_has_access2(self.application.id, self.id, src.security.modify_object):
			raise VDOM_exception_sec(_("Modifying object is not allowed"))
		if value.lower() == self.name:
			return
		# check the name
		if not is_valid_identifier(value):
			raise VDOM_exception_name(_("Name is empty or contains invalid characters"))
		# check if name exists
		if self.parent and value.lower() in self.parent.objects_by_name:
			raise VDOM_exception_name(_("The name '%s' is already in use") % str(value))
		if not self.parent:
			for key in self.application.objects:
				if self.application.objects[key].name == value.lower():
					raise VDOM_exception_name(_("The name '%s' is already in use") % str(value))

		self.__sem.lock()
		try:
			if self.parent:
				del self.parent.objects_by_name[self.name]
				self.parent.objects_by_name[value.lower()] = self
			self.original_name = value
			self.name = value.lower()
			self.xml_obj.attributes["Name"] = value
			self.__do_invalidate(self)
		finally:
			self.__sem.unlock()

	def __do_invalidate(self, obj):
		"""invalidate source code"""
		src.source.cache.invalidate(self.application.id, obj.id)
		src.resource.resource_manager.invalidate_resources(obj.id)

		to_invalidate = []
		if obj.parent:
			to_invalidate.append(obj.parent.id)
		to_invalidate += obj.copy_objects

		for ii in to_invalidate:
			obj1 = self.application.search_object(ii)
			if obj1:
				self.__do_invalidate(obj1)

	def __do_invalidate1(self, obj):
		src.source.cache.invalidate(self.application.id, obj.id)
		src.resource.resource_manager.invalidate_resources(obj.id)
		if hasattr(obj, "dynamic"):
			del obj.dynamic
		for o in obj.objects_list:
			self.__do_invalidate1(o)

	def invalidate(self):
		self.__sem.lock()
		try:
			self.__do_invalidate(self)
		finally:
			self.__sem.unlock()

	def invalidate1(self):
		self.__sem.lock()
		try:
			self.__do_invalidate1(self)
		finally:
			self.__sem.unlock()

	def search(self, pattern):
		# return list of objects id where pattern is found
		result = []
		for a_name in self.attributes:
			if pattern in self.attributes[a_name].value:
				result.append(self.id)
				break
		for obj in self.objects_list:
			r = obj.search(pattern)
			result += r
		return result

from src.soap.errors import *
from src.xml.event import *
from src.xml.attribute import VDOM_attribute
from src.util.exception import *
from src.util.semaphore import VDOM_semaphore
from src.util.encode import *
from src.util.id import is_valid_identifier
import src.util.id
import src.util.uuid
import src.source
import src.resource
import src.engine
import src.request
import src.security