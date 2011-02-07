
from src.xml.xml_object import xml_object
from src.xml.event import *
from src.xml.structure import *
from src.util.exception import *


class VDOM_application_wrapper:

	_map = {
			"index": "index_page",
			"serverversion": "server_version",
			"scriptinglanguage": "scripting_language"
		}

	def __init__(self, s, data):
		x = xml_object(srcdata = data)
		try:
			if "application" != x.lname:
				raise VDOM_exception_element(x.lname)
			i = x.get_child_by_name("information")
			if not i:
				raise VDOM_exception_element("information")
			for c in i.children:
				if c.lname in VDOM_application_wrapper._map:
					setattr(self, VDOM_application_wrapper._map[c.lname], c.value)
				else:
					setattr(self, c.lname, c.value)
		finally:
			x.delete()
		self.session = s
		self.__objects_list = None
		self.__objects_map = None
		self.__all_objects = {}
		self.__struc = None
		self.__events = None
		self.__events_by_object = None
		self.__actions = None
		self.__global_actions = None

	def __del__(self):	# remove parent objects links
		if self.__objects_list:
			for o in self.__objects_list:
				if o.has_objects:
					for o1 in o.objects_list:
						o1.parent = None

	def __getitem__(self, key):
		k = key.lower()
		if k in self.__all_objects:
			return self.__all_objects[k]
		return self.get_object(k)

	def __contains__(self, key):
		return key.lower() in self.__all_objects

	def __get_objects(self):
		x = self.session.send_request("get_top_objects", [("appid", self.id)])
		self.__objects_list = []
		self.__objects_map = {}
		self.__objects_list = VDOM_objects_list_wrapper(self.session, data = x)
		for o in self.__objects_list:
			self.__objects_map[o.id] = o
			self.__reg_object(o)

	def __get_e2vdom(self):
		x = self.session.send_request("application_e2vdom", [("appid", self.id)])
		if not x:
			return None
		y = VDOM_e2vdom_wrapper(data = x)
		self.__events = y.events
		self.__events_by_object = y.events_by_object
		self.__actions = y.actions

	def __reg_object(self, obj):
		self.__all_objects[obj.id] = obj
		if not obj.has_objects():
			return
		for o in obj.objects_list:
			self.__reg_object(o)

	# ----------------------------------------------------------------------------------------------

	def __get_objects_list(self):
		if self.__objects_list is None:
			self.__get_objects()
		return self.__objects_list

	objects_list = property(__get_objects_list)

	def __get_objects_map(self):
		if self.__objects_map is None:
			self.__get_objects()
		return self.__objects_map

	objects_map = property(__get_objects_map)

	def __get_struc(self):
		if self.__struc is None:
			x = self.session.send_request("get_application_structure", [("appid", self.id)])
			if not x:
				x = ""
			self.__struc = VDOM_structure(data = x, app = self)
		return self.__struc

	#def __set_struct(self, data):
	#	self.session.send_request("set_application_structure", [("appid", self.id), ("data", data)])
#		self.__struc = None

	app_map = property(__get_struc)#, __set_struct)

	def __get_events(self):
		if self.__events is None:
			self.__get_e2vdom()
		return self.__events

	events = property(__get_events)

	def __get_events_by_object(self):
		if self.__events_by_object is None:
			self.__get_e2vdom()
		return self.__events_by_object

	events_by_object = property(__get_events_by_object)

	def __get_actions(self):
		if self.__actions is None:
			self.__get_e2vdom()
		return self.__actions

	actions = property(__get_actions)

	def __get_global_actions(self):
		if self.__global_actions is None:
			x = self.session.send_request("application_actions", [("appid", self.id)])
			if not x:
				return None
			self.__global_actions = VDOM_actions_map_wrapper(data = x)
		return self.__global_actions

	global_actions = property(__get_global_actions)

	def __get_number_of_objects(self):
		x = self.session.send_request("application_number_of_objects", [("appid", self.id)])
		return int(x)

	number_of_objects = property(__get_number_of_objects)

	# ----------------------------------------------------------------------------------------------

	def get_object(self, objid):
		x = self.session.send_request("get_object", [("appid", self.id), ("objid", objid)])
		if not x:
			return None
		o = VDOM_object_wrapper(self.session, data = x)
		self.__reg_object(o)
		return o

	def get_object_tree(self, objid):
		x = self.session.send_request("get_child_objects_tree", [("appid", self.id), ("objid", objid)])
		if not x:
			return None
		return VDOM_object_wrapper(self.session, data = x)

	def load_all_objects(self):
		x = self.session.send_request("get_top_objects", [("appid", self.id)])
		self.__objects_list = []
		self.__objects_map = {}
		l = VDOM_objects_list_wrapper(self.session, data = x)
		for o in l:
			o1 = self.get_object_tree(o.id)
			self.__objects_list.append(o1)
			self.__objects_map[o1.id] = o1
			self.__reg_object(o1)

	def get_info(self):
		x = self.session.send_request("application_get_info", [("appid", self.id)])
		if x:
			return x
		return None

	#def set_info(self, data):
	#	u = session_manager.current.user
	#	self.session.send_request("application_set_info", [("appid", self.id), ("data", data), ("username", u)])

	# --- source -----------------------------------------------------------------------------------

	#def get_source(self, container_id, action_name, context):
	#	x = self.session.send_request("get_source", [("appid", self.id), ("objid", container_id), ("action", action_name), ("context", context)])
	#	if not x:
	#		return None
	#	return x # ???


class VDOM_e2vdom_wrapper:

	def __init__(self, xml_obj = None, data = None):
		f = 0
		if not xml_obj:
			xml_obj = xml_object(srcdata = data)
			f = 1
		try:
			if "e2vdom" != xml_obj.lname:
				raise VDOM_exception_element(xml_obj.lname)
			self.events = {}
			self.actions = {}
			self.events_by_object = {}
			for child in xml_obj.children:
				if "events" == child.lname:
					self.parse_e2vdom_events(child)
				elif "actions" == child.lname:
					self.parse_e2vdom_actions(child)
		finally:
			if f:
				xml_obj.delete()

	def parse_e2vdom_events(self, xml_obj):
		for child in xml_obj.children:
			if "event" == child.lname:
				self.parse_e2vdom_event(child)

	def parse_e2vdom_actions(self, xml_obj):
		for child in xml_obj.children:
			if "action" == child.lname:
				self.parse_e2vdom_action(child)

	def parse_e2vdom_event(self, xml_obj):
		src_id = xml_obj.attributes.get("objsrcid", None)
		cont_id = xml_obj.attributes.get("containerid", None)
		name = xml_obj.attributes.get("name", None)
		if not src_id or not cont_id or not name:
			raise VDOM_exception_parse(_("event format error"))
		ev = VDOM_application_event()
		ev.name = name
		ev.source_object = src_id
		ev.container = cont_id
		ev.top = xml_obj.attributes.get("top", "")
		ev.left = xml_obj.attributes.get("left", "")
		ev.state = xml_obj.attributes.get("state", "")
		if cont_id not in self.events:
			self.events[cont_id] = {}
		if src_id not in self.events[cont_id]:
			self.events[cont_id][src_id] = {}
		self.events[cont_id][src_id][name] = ev
		self.events_by_object[src_id] = self.events[cont_id][src_id]
		for act in xml_obj.children:
			if "action" == act.lname:
				_id = act.attributes["id"]
				if _id and _id not in ev.actions:
					ev.actions.append(_id)
		return ev

	def parse_e2vdom_action(self, xml_obj):
		_id = xml_obj.attributes.get("id", None)
		tgt_id = xml_obj.attributes.get("objtgtid", None)
		mn = xml_obj.attributes.get("methodname", None)
		if not tgt_id or not mn or not _id:
			raise VDOM_exception_parse(_("action format error"))
		a = VDOM_action_info()
		a.method_name = mn
		a.id = _id
		a.target_object = tgt_id
		a.top = xml_obj.attributes.get("top", "")
		a.left = xml_obj.attributes.get("left", "")
		a.state = xml_obj.attributes.get("state", "")
		self.actions[_id] = a
		for par in xml_obj.children:
			if "parameter" == par.lname:
				p = VDOM_parameter()
				p.name = par.attributes["scriptname"]
				p.value = par.value
				a.parameters.append(p)
		return a


class VDOM_actions_map_wrapper(dict):

	def __init__(self, xml_obj = None, data = None):
		dict.__init__(self)
		f = 0
		if not xml_obj:
			xml_obj = xml_object(srcdata = data)
			f = 1
		try:
			if "actions" != xml_obj.lname:
				raise VDOM_exception_element(xml_obj.lname)
			for child in xml_obj.children:
				if "action" == child.lname:
					self.parse_action(child)
		finally:
			if f:
				xml_obj.delete()

	def parse_action(self, s_node):
		name = s_node.attributes["name"]
		_id = s_node.attributes["id"].lower()
		_top = s_node.attributes.get("top", "")
		_left = s_node.attributes.get("left", "")
		_state = s_node.attributes.get("state", "")
		code = s_node.value.strip()
		x = VDOM_server_action(code, _id, _top, _left, _state, name)
		self[_id] = x
		self[name.lower()] = x


class VDOM_structure(dict):

	def __init__(self, xml_obj = None, data = None, app = None):
		dict.__init__(self)
		# pre-fill structure
		for idx in xrange(10):
			level_index = chr(ord('0') + idx)
			self[level_index] = VDOM_structure_level(level_index)
			for obj in app.objects_list:
				self[level_index].level_map[obj.id] = VDOM_structure_item(obj.id)
		f = 0
		if not xml_obj:
			if not data:
				return
			xml_obj = xml_object(srcdata = data)
			f = 1
		try:
			if "structure" != xml_obj.lname:
				raise VDOM_exception_element(xml_obj.lname)
			for child in xml_obj.children:
				if "object" == child.lname:
					obj_id = child.attributes["id"]
					if not obj_id:
						continue
					for level_item in child.children:
						if "level" == level_item.lname:
							self.parse_structure_level(level_item, obj_id)
		finally:
			if f:
				xml_obj.delete()

	def parse_structure_level(self, xml_obj, parent_id):
		"""parse one structure level"""
		level_index = xml_obj.attributes["index"]
		if level_index not in self:
			self[level_index] = VDOM_structure_level(level_index)
		if parent_id not in self[level_index].level_map:
			self[level_index].level_map[parent_id] = VDOM_structure_item(parent_id)
		parent_item = self[level_index].level_map[parent_id]
		for child in xml_obj.children:
			if "object" == child.lname:
				obj_id = child.attributes["id"]
				if not obj_id:
					continue
				if obj_id not in self[level_index].level_map:
					self[level_index].level_map[obj_id] = VDOM_structure_item(obj_id)
				obj_item = self[level_index].level_map[obj_id]
				index = child.attributes["index"]
				if index and index.isdigit():
					obj_item.index = int(index)
				parent_item.children.append(obj_item)
				obj_item.parents.append(parent_item)


class VDOM_objects_list_wrapper(list):

	def __init__(self, s, xml_obj = None, data = None):
		list.__init__(self)
		self.session = s
		f = 0
		if not xml_obj:
			xml_obj = xml_object(srcdata = data)
			f = 1
		try:
			if "objects" != xml_obj.lname:
				raise VDOM_exception_element(xml_obj.lname)
			for c in xml_obj.children:
				self.append(VDOM_object_wrapper(self.session, xml_obj = c))
		finally:
			if f:
				xml_obj.delete()


class VDOM_object_wrapper(object):

	def __init__(self, s, xml_obj = None, data = None):
		#self.attr_names = {}
		object.__setattr__(self, "attr_names", {})
		self.session = s
		f = 0
		if not xml_obj:
			xml_obj = xml_object(srcdata = data)
			f = 1
		try:
			if "object" != xml_obj.lname:
				raise VDOM_exception_element(xml_obj.lname)
			self.__objects_list = None
			self.__objects_map = None
			self.__actions = None
			self.parent = None
			self.id = xml_obj.attributes["id"]
			self.original_name = xml_obj.attributes["name"]
			self.name = self.original_name.lower()
			#self.type = vdom_memory[xml_obj.attributes["type"]]
			#if not self.type:
			#	raise VDOM_exception_element("object:type")
			for c in xml_obj.children:
				if hasattr(self, "parse_" + c.lname):
					getattr(self, "parse_" + c.lname)(c)
		finally:
			if f:
				xml_obj.delete()

	def __setattr__(self, name, value):
		if name in self.attr_names:
			self.attr_names[name] = 1
		object.__setattr__(self, name, value)

	def __del__(self):	# remove parent objects links
		if self.__objects_list:
			for o in self.__objects_list:
				if o.has_objects:
					for o1 in o.objects_list:
						o1.parent = None

	def delete(self):
		self.parent = None
		if self.__objects_list:
			for o in self.__objects_list:
				if o.has_objects:
					for o1 in o.objects_list:
						o1.parent = None
			self.__objects_list = None
			self.__objects_map = None

	def has_objects(self):
		if self.__objects_list:
			return True
		return False

	def parse_attributes(self, xml_obj):
		if "attributes" != xml_obj.lname:
			raise VDOM_exception_element(xml_obj.lname)
		for c in xml_obj.children:
			self.parse_attribute(c)

	def parse_attribute(self, xml_obj):
		if "attribute" != xml_obj.lname:
			raise VDOM_exception_element(xml_obj.lname)
		n = xml_obj.attributes["name"]
		setattr(self, n, xml_obj.value)
		self.attr_names[n] = 0

	def parse_objects(self, xml_obj):
		self.__objects_list = VDOM_objects_list_wrapper(self.session, xml_obj = xml_obj)
		self.__objects_map = {}
		for o in self.__objects_list:
			self.__objects_map[o.id] = o
			o.parent = self

	def __get_objects(self):
		x = self.session.send_request("get_child_objects", [("appid", self.session.appid), ("objid", self.id)])
		self.__objects_list = []
		self.__objects_map = {}
		self.__objects_list = VDOM_objects_list_wrapper(self.session, data = x)
		for o in self.__objects_list:
			self.__objects_map[o.id] = o
			o.parent = self

	# ----------------------------------------------------------------------------------------------

	def __get_objects_list(self):
		if self.__objects_list is None:
			self.__get_objects()
		return self.__objects_list

	objects_list = property(__get_objects_list)

	def __get_objects_map(self):
		if self.__objects_map is None:
			self.__get_objects()
		return self.__objects_map

	objects_map = property(__get_objects_map)

	def __get_number_of_childs(self):
		x = self.session.send_request("object_get_number_of_childs", [("appid", self.session.appid), ("objid", self.id)])
		return int(x)

	number_of_childs = property(__get_number_of_childs)

	def __get_actions(self):
		if self.__actions is None:
			x = self.session.send_request("object_actions", [("appid", self.session.appid), ("objid", self.id)])
			if not x:
				return None
			self.__actions = VDOM_actions_map_wrapper(data = x)
		return self.__actions

	actions = property(__get_actions)

	#def save(self):
	#	u = session_manager.current.user
	#	self.session.send_request("save_object", [("appid", self.session.appid), ("objid", self.id), ("data", wrap_object(self, _ci = False)), ("username", u)])
