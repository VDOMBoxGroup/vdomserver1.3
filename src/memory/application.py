"""XML application module"""

import re, sys, os, SOAPpy, thread, threading
from threading import Condition
from names import APPLICATION_SECTION, REQUEST_SECTION, SESSION_SECTION, ON_START, ON_FINISH
from parser import VDOM_parser


rexp = re.compile(r"\#res\(([a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12})\)", re.IGNORECASE)


class VDOM_application(VDOM_parser):
	"""XML VDOM application class"""

	def __init__(self, manager):
		"""constructor"""
		self.xml_manager = manager
		self.parse_list = ["information", "objects", "structure", "actions", "resources", "databases", "e2vdom", "languages", "security", "libraries", "backupfiles"]
		self.info_map = {
			"id":		["id", "str(%s)", "Id"],
			"name":		["name", "%s", "Name"],
			"description":	["description", "%s", "Description"],
			"owner":	["owner", "%s", "Owner"],
			"password":	["password", "%s", "Password"],
			"active":	["active", "%s", "Active"],
			"index":	["index_page", "%s", "Index"],
			"icon":		["icon", "%s", "Icon"],
			"serverversion":["server_version", "%s", "ServerVersion"],
			"scriptinglanguage":["scripting_language", "%s", "ScriptingLanguage"],
			
			"defaultlanguage":["default_language", "%s", "DefaultLanguage"],
		    "currentlanguage":["current_language", "%s", "CurrentLanguage"],
		}
		self.object_map = {
			"name":	["name", "%s"],
			"id":	["id", "str(%s).lower()"],
			"type":	["type", "self.xml_manager.get_type(%s.lower())"]
		}
		# --- for sync --------------------------------------------------------------------------------------
		self.__read_locks = []	# store here the thread IDs of read sessions
		self.__write_locks = []	# store here the thread IDs of write sessions that are waiting
		self.__1sem = VDOM_semaphore()
		self.__cond_read = Condition()
		self.__cond_write = Condition()
		# required attributes
		self.required_attributes = ["id"]
		self.objects = {}	# top-level objects - map id to VDOM_object instance
		self.objects_list = []	# list of top-level objects as they appear in xml
		self.__all_objects = {}	# map of all objects in the application - for quick searching by ID
		self.resources = {}
		self.structure_resources = {}
		self.languages = ""
		self.app_map = None	# application structure, map level_idx : VDOM_structure_level
		self.index_page = None	# index container
		# event
		self.events = {}	# map container_id : {source_object_id : {ev_name : VDOM_application_event()}}
		self.events_by_object = {}	# map source_object_id : {ev_name : VDOM_application_event()}
		self.actions = {}	# map ID : VDOM_action_info()
		self.global_actions = {}# map ID : {name : VDOM_server_action()}
		self.o_tmp = []
		self.libs = {}
		self.scripting_language = "vscript"
		self.default_language = "en-US"
		# backups
		self.__backup_files={}
		# base
		VDOM_parser.__init__(self)
		# semaphore used to lock application object for modifications
		self.__sem = VDOM_semaphore()

	def create(self, xml_obj = None):
		if not xml_obj:	# create new xml object
			xml_obj = xml_object(VDOM_CONFIG["APPLICATION-XML-TEMPLATE"])
			new_id = str(uuid4())
			inf = xml_obj.get_child_by_name("information")
			_id = inf.get_child_by_name("id")
			_id.value = new_id
			_sv = inf.get_child_by_name("serverversion")
			_sv.value = VDOM_server_version
		# base
		self.__xml_obj = xml_obj
		VDOM_parser.create(self, xml_obj)
		# parse #Res() links in all objects
		self.__parse_links(self)
		# write to resource manager which objects use which resources
		for oid in self.__all_objects:
			obj = self.__all_objects[oid]
			for res_id in obj.resources.keys():
				attributes = {"id" : res_id}
				if managers.resource_manager.check_resource(self.id, attributes):
					managers.resource_manager.add_resource(self.id, obj.id, attributes, None)
		for res_id in self.resources.keys():
			attributes = {"id" : res_id}
			if managers.resource_manager.check_resource(self.id, attributes):
				managers.resource_manager.add_resource(self.id, self.id, attributes, None)
		# check if need to create structure
		if len(self.structure_element.children) == 0:
			# generate structure
			for o in self.objects_list:
				i = xml_object(name="Object")
				self.structure_element.children.append(i)
				i.attributes["ID"] = o.id
				i.attributes["Top"] = "0"
				i.attributes["Left"] = "0"
				i.attributes["ResourceID"] = ""
		self.do_parse_structure(self.structure_element)
		
		self.sync()
		del self.o_tmp

		on_start=self.global_actions[APPLICATION_SECTION][APPLICATION_SECTION+ON_START]
		if on_start.code:
			#threading.currentThread().application=self.id
			__import__(self.id)
			managers.engine.special(self, on_start, namespace={})
			#threading.currentThread().application=None

	def __repr__(self):
		return "VDOM application (name='%s' id='%s')" % (self.name, self.id)

	def __str__(self):
		return repr(self)

	def objects_amount(self):
		return len(self.__all_objects)

	def get_xml(self):
		"""get xml document"""
		return self.__xml_obj

	def parse_objects(self, xml_obj, obj_list = None, obj_list1 = None, obj_list2 = None, parent = None):
		"""parse objects"""
		if parent:
			parent.objects_element = xml_obj
		object_list = self.objects
		object_list1 = self.objects_list
		if obj_list != None:
			object_list = obj_list
		if obj_list1 != None:
			object_list1 = obj_list1
		for child in xml_obj.children:
			if "object" == child.lname:
				obj = self.parse_object(child, parent)
				object_list[obj.id] = obj	# add new object
				object_list1.append(obj)
				if obj_list2 != None:
					if obj.name in obj_list2:
						raise VDOM_exception_dup(_("Duplicate object name %s" % str(obj.name)))
					obj_list2[obj.name] = obj

	def parse_object(self, xml_obj, parent):
		"""parse one object"""
		obj = VDOM_object(self)
		if hasattr(self, "o_tmp"):
			self.o_tmp.append(obj)
		# set primary attributes
		for name in xml_obj.attributes:
			value = xml_obj.attributes[name]
			if name in self.object_map:
				exec "obj." + self.object_map[name][0] + " = " + (self.object_map[name][1] % "value")
				# make name lower-case and store original name
				if "name" == name:
					obj.original_name = obj.name
					obj.name = obj.name.lower()
		# parse other object parts
		obj.parse(xml_obj)
		obj.parent = parent
		if not parent:
			obj.toplevel = obj
		else:
			obj.toplevel = parent.toplevel
		# check copy
		if "copy" == obj.type.name:
			obj.toplevel.has_copy += 1
		# parse child objects
		for child in xml_obj.children:
			if "objects" == child.lname:
				self.parse_objects(child, obj.get_objects(), obj.get_objects_list(), obj.objects_by_name, obj)
		# store in cache
		if obj.id in self.__all_objects:
			raise VDOM_exception_dup(_("Duplicate object id: %s") % obj.id)
		self.__all_objects[obj.id] = obj
		return obj

#	def register_object(self, obj):
#		self.__all_objects[obj.id] = obj
#
#	def unregister_object(self, obj):
#		del self.__all_objects[obj.id]

	def parse_languages(self, xml_obj):
		"""parse languages section"""
		self.languages = xml_obj.toxml()
		# remove languages node from memory
		xml_obj.delete()

	def parse_actions(self, xml_obj):
		"""parse application global actions section"""
		self.do_prepare_global_actions()
		self.actions_element = xml_obj
		for s_node in xml_obj.children:
			if "action" == s_node.lname:
				name = s_node.attributes["name"]
				_id = s_node.attributes["id"].lower()
				if not _id or not name:
					continue
				_top = s_node.attributes.get("top", "")
				_left = s_node.attributes.get("left", "")
				_state = s_node.attributes.get("state", "")
				code = s_node.get_value_as_xml().strip()
				category = _id.replace(name,'') #TODO: find better solution to get category
				self.global_actions[category][_id] = VDOM_server_action(code, _id, _top, _left, _state, name)

	def parse_e2vdom(self, xml_obj):
		"""parse events section"""
		for child in xml_obj.children:
			if "events" == child.lname:
				self.e2vdom_events_element = child
				self.parse_e2vdom_events(child)
			elif "actions" == child.lname:
				self.e2vdom_actions_element = child
				self.parse_e2vdom_actions(child)
		if not hasattr(self, "e2vdom_events_element"):
			x = xml_object(name="Events")
			xml_obj.children.append(x)
			self.e2vdom_events_element = x
		if not hasattr(self, "e2vdom_actions_element"):
			x = xml_object(name="Actions")
			xml_obj.children.append(x)
			self.e2vdom_actions_element = x

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
		ev.xml_obj = xml_obj
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
		a.xml_obj = xml_obj
		self.actions[_id] = a
		for par in xml_obj.children:
			if "parameter" == par.lname:
				p = VDOM_parameter()
				p.name = par.attributes["scriptname"]
				p.value = par.value
				a.parameters.append(p)
		return a

	def parse_security(self, xml_obj):
		"""parse security section"""
		for child in xml_obj.children:
			if "groups" == child.lname:
				self.parse_security_groups(child)
			elif "users" == child.lname:
				self.parse_security_users(child)
		xml_obj.delete()

	def parse_security_groups(self, xml_obj):
		for child in xml_obj.children:
			if "group" == child.lname:
				self.parse_security_group(child)

	def parse_security_users(self, xml_obj):
		for child in xml_obj.children:
			if "user" == child.lname:
				self.parse_security_user(child)

	def parse_security_group(self, xml_obj):
		name = xml_obj.get_child_by_name("name")
		desc = xml_obj.get_child_by_name("description")
		if not name or not desc or not name.value:
			return
		name = name.value.encode("utf-8")
		desc = desc.value.encode("utf-8")
		a = {}
		r = xml_obj.get_child_by_name("rights")
		if r:
			for child in r.children:
				if "right" == child.lname:
					tgt = child.attributes["target"]
					acc = child.attributes["access"]
					if tgt and acc and (tgt in self.__all_objects or tgt == self.id):
						a[str(tgt)] = map(int, acc.split(","))
		try:
			managers.user_manager.create_group(name, desc)
		except:
			#debug("Group '%s' exists" % name)
			pass
		for tgt in a:
			for i in a[tgt]:
				managers.acl_manager.add_access(tgt, name, i)

	def parse_security_user(self, xml_obj):
		login = xml_obj.get_child_by_name("login")
		password = xml_obj.get_child_by_name("password")
		fn = xml_obj.get_child_by_name("firstname")
		ln = xml_obj.get_child_by_name("lastname")
		email = xml_obj.get_child_by_name("email")
		sl = xml_obj.get_child_by_name("securitylevel")
		memb = xml_obj.get_child_by_name("memberof")
		if not login or not password or not login.value or not password.value:
			return
		login = login.value.encode("utf-8")
		password = password.value.encode("utf-8")
		a = {}
		r = xml_obj.get_child_by_name("rights")
		if r:
			for child in r.children:
				if "right" == child.lname:
					tgt = child.attributes["target"]
					acc = child.attributes["access"]
					if tgt and acc and (tgt in self.__all_objects or tgt == self.id):
						a[str(tgt)] = map(int, acc.split(","))
		if fn and fn.value: fn = fn.value.encode("utf-8")
		else: fn = ""
		if ln and ln.value: ln = ln.value.encode("utf-8")
		else: ln = ""
		if email and email.value: email = email.value.encode("utf-8")
		else: email = ""
		if sl and sl.value: sl = sl.value.encode("utf-8")
		else: sl = ""
		try:
			managers.user_manager.create_user(login, password, fn, ln, email, sl)
		except:
			#debug("User '%s' exists" % login)
			pass # WTF!?!
		u = managers.user_manager.get_user_object(login)
		if not u:
			return
		for tgt in a:
			for i in a[tgt]:
				managers.acl_manager.add_access(tgt, login, i)
		if memb and memb.value:
			m = memb.value.encode("utf-8")
			u.member_of = m.split(",")
			managers.user_manager.sync()

	def parse_libraries(self, xml_obj):
		managers.file_manager.create_lib_path(self.id)
		for child in xml_obj.children:
			if "library" == child.lname:
				self.parse_library(child)

	def parse_library(self, xml_obj):
		name = xml_obj.attributes["name"]
		if is_valid_identifier(name):
			if "vscript" == self.scripting_language:
				try:
					threading.currentThread().application=self.id
					x, y = vcompile(xml_obj.value, bytecode = 0)
					managers.file_manager.write_lib(self.id, name, x)
					self.libs[name] = y
				except:
					pass # WTF!?!
				finally:
					threading.currentThread().application=None
			else:
				value="from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request\n%s\n"%xml_obj.value
				managers.file_manager.write_lib(self.id, name, value)
				self.libs[name] = None
		else:
			debug("  Library '%s' ignored: incorrect name" % name)

	def parse_structure_level(self, xml_obj, parent_id):
		"""parse one structure level"""
		level_index = xml_obj.attributes["index"]
		if level_index not in self.__app_map:
			self.__app_map[level_index] = VDOM_structure_level(level_index)
		if parent_id not in self.__app_map[level_index].level_map:
			self.__app_map[level_index].level_map[parent_id] = VDOM_structure_item(parent_id)
		parent_item = self.__app_map[level_index].level_map[parent_id]

		to_remove = []
		for child in xml_obj.children:
			if "object" == child.lname:
				obj_id = child.attributes["id"]
				if not obj_id or None == self.search_object(obj_id):
					debug(" Object ID '%s' not found" % obj_id, "structure")
					to_remove.append(child)
					continue
				if obj_id not in self.__app_map[level_index].level_map:
					self.__app_map[level_index].level_map[obj_id] = VDOM_structure_item(obj_id)
				obj_item = self.__app_map[level_index].level_map[obj_id]
				index = child.attributes["index"]
				if index and index.isdigit():
					obj_item.index = int(index)
				parent_item.children.append(obj_item)
				obj_item.parents.append(parent_item)
		for r in to_remove:
			r.delete()

	def parse_structure(self, xml_obj):
		pass

	def parse_backupfiles(self, xml_obj):
		for child in xml_obj.children:
			if child.lname=="file":
				self.parse_backupfiles_file(child)

	def parse_backupfiles_file(self, xml_obj):
		filename=xml_obj.attributes["name"]
		self.__backup_files[filename]=xml_obj

	def do_parse_structure(self, xml_obj):
		"""parse application structure"""
		if None != self.app_map:
			if not managers.acl_manager.session_user_has_access2(self.id, self.id, security.modify_application):
				raise VDOM_exception_sec(_("Modifying application structure is not allowed"))
		self.__app_map = {}
		# pre-fill structure
		for idx in xrange(10):
			level_index = chr(ord('0') + idx)
			self.__app_map[level_index] = VDOM_structure_level(level_index)
			for oid in self.objects:
				obj = self.objects[oid]
				self.__app_map[level_index].level_map[oid] = VDOM_structure_item(oid)
		to_remove = []
		# parse
		for child in xml_obj.children:
			if "object" == child.lname:
				obj_id = child.attributes["id"]
				if not obj_id or None == self.search_object(obj_id):
					debug("Object ID '%s' not found" % obj_id, "structure")
					to_remove.append(child)
					continue
				res_id = child.attributes["resourceid"]
				if "" != res_id:
					if obj_id not in self.structure_resources or res_id != self.structure_resources[obj_id]:
						attributes = {"id" : res_id}
						if managers.resource_manager.check_resource(self.id, attributes):
							managers.resource_manager.add_resource(self.id, obj_id, attributes, None)
					if obj_id in self.structure_resources and res_id != self.structure_resources[obj_id]:
						attributes = {"id" : self.structure_resources[obj_id]}
						if managers.resource_manager.check_resource(self.id, attributes):
							managers.resource_manager.delete_resource(obj_id, self.structure_resources[obj_id])
					self.structure_resources[obj_id] = res_id
				for level_item in child.children:
					if "level" == level_item.lname:
						# parse level
						self.parse_structure_level(level_item, obj_id)
		self.app_map = self.__app_map
		del self.__app_map
		for r in to_remove:
			r.delete()

	def do_prepare_global_actions(self):
		session_actions=self.global_actions.setdefault(SESSION_SECTION, {})
		request_actions=self.global_actions.setdefault(REQUEST_SECTION, {})
		application_actions=self.global_actions.setdefault(APPLICATION_SECTION, {})
		
		session_actions.setdefault(SESSION_SECTION+ON_START,
				VDOM_server_action("", SESSION_SECTION+ON_START, "", "", "", ON_START))
		session_actions.setdefault(SESSION_SECTION+ON_FINISH,
				VDOM_server_action("", SESSION_SECTION+ON_FINISH, "", "", "", ON_FINISH))
		
		request_actions.setdefault(REQUEST_SECTION+ON_FINISH,
				VDOM_server_action("", REQUEST_SECTION+ON_START, "", "", "", ON_START))
		
		application_actions.setdefault(APPLICATION_SECTION+ON_START,
				VDOM_server_action("", APPLICATION_SECTION+ON_START, "", "", "", ON_START))
		application_actions.setdefault(APPLICATION_SECTION+ON_FINISH,
				VDOM_server_action("", APPLICATION_SECTION+ON_FINISH, "", "", "", ON_FINISH))
		
	def test4res(self, value, owner):
		"""test for #Res(N)"""
		ret = None
		try:
			ret = rexp.split(value)
		except: debug(str(value))
		for idx in xrange(len(ret)):
			if 1 == idx % 2 and owner:	# this is resource ID
				res_id = ret[idx]
				if res_id not in owner.resources:
					owner.resources[res_id] = 0
				owner.resources[res_id] += 1
		return "".join(ret)

	def __parse_links(self, parent):
		"""replace #Res links in attributes value"""
		if hasattr(parent, "info_map"):
			for mm in parent.info_map.keys():
				mn = parent.info_map[mm][0]
				value = getattr(parent, mn)
				if value and "" != value:
					setattr(parent, mn, self.test4res(value, parent))
		# attributes
		if hasattr(parent, "get_attributes"):
			for a in parent.get_attributes().values():
				a.value = self.test4res(a.value, parent)
				# check copy object
				if "copy" == parent.type.name and "source_object" == a.name:
					obj = self.search_object(a.value)	# try to find the source object
					if obj and not parent.id in obj.copy_objects:
						obj.copy_objects.append(parent.id)
		for o in parent.get_objects_list():
			self.__parse_links(o)

	def save_resource(self, res_id, res_format, res_name, data):
		"""method to save resource"""
		attributes = {
			"id" : res_id,
			"name" : res_name,
			"res_format": res_format,
			}
		if not managers.resource_manager.check_resource(self.id, attributes):
			managers.resource_manager.add_resource(self.id, None, attributes, data)

	def __create_structure_object(self, obj):
		autolock = VDOM_named_mutex_auto(self.id + "_structure")
		x = xml_object(name="Object")
		self.structure_element.children.append(x)
		x.attributes["ID"] = obj.id
		x.attributes["ResourceID"] = ""
		x.attributes["Top"] = "0"
		x.attributes["Left"] = "0"

	def __do_create_object(self, typeid, parent = None, do_compute=True):
		"""create object, return tuple (name, id)"""
		type_obj = self.xml_manager.get_type(typeid)
		#doc = self.get_xml()
		obj_id = str(uuid4())
		obj_name = type_obj.name.lower() + "_" + "_".join(obj_id.lower().split("-"))

		target = self
		if parent: target = parent
		if not parent:
			if 3 != type_obj.container:
				raise VDOM_exception_param(_("Object '%s' can't be top-level container" % type_obj.name))
		else:
			if parent.type.name not in type_obj.containers:
				raise VDOM_exception_param(_("Object '%s' can't be created inside '%s'" % (type_obj.name, parent.type.name)))

		x = xml_object(name="Object")
		target.objects_element.children.append(x)
		x.attributes["Name"] = obj_name
		x.attributes["ID"] = obj_id
		x.attributes["Type"] = typeid
		x.children.append(xml_object(name="Actions"))
		x.children.append(xml_object(name="Objects"))
		attr_x = xml_object(name="Attributes")
		x.children.append(attr_x)

		# process all object attributes
		for a in type_obj.get_attributes().values():
			a_x = xml_object(name="Attribute")
			attr_x.children.append(a_x)
			a_x.attributes["Name"] = a.name
			if "zindex" == a.name and parent:
				# calc max zindex for parent's children
				maxz = 0
				for q in parent.objects_list:
					if "zindex" in q.attributes:
						curz = int(q.attributes.zindex)
						if maxz < curz: maxz = curz
				a_x.value = str(maxz)
			else:
				a_x.value = a.default_value

		# parse new object
		obj = self.parse_object(x, parent)
		target.get_objects()[obj.id] = obj
		target.get_objects_list().append(obj)
		# parse links
		self.__parse_links(obj)
		# add to all objects hash
		self.__all_objects[obj.id] = obj
		if parent:
			parent.objects_by_name[obj_name] = obj
			obj.toplevel = parent.toplevel
		else:
			obj.toplevel = obj

		obj.invalidate()

		managers.request_manager.get_request().container_id = obj.toplevel.id
		if do_compute:
			managers.engine.compute(self, obj, parent)

		if parent:
			managers.dispatcher.dispatch_handler(self.id, parent.id, "add_child", {"child_id":obj.id})
		else:
			self.__create_structure_object(obj)
		return (obj_name, obj_id)

	def __do_delete_object(self, obj):
		"""delete object from the application; also delete all associated resources and source code"""
		managers.dispatcher.dispatch_handler(self.id, obj.id, "on_delete", None )
		# first delete all child objects
		l = []
		for o in obj.objects_list:
			l.append(o)
		for o in l:
			self.__do_delete_object(o)
		obj.objects_list = []
		if obj.parent:
			obj.parent.objects_list.remove(obj)
		else:	# top-level container
			self.objects.pop(obj.id, None)
			if obj in self.objects_list:
				self.objects_list.remove(obj)
			# remove it from the structure
			for l_idx in self.app_map:
				l_map = self.app_map[l_idx].level_map
				x = l_map.pop(obj.id, None)
				if x:
					for obj_id in l_map:
						item = l_map[obj_id]
						while x in item.children:
							item.children.remove(x)
						while x in item.parents:
							item.parents.remove(x)
			# remove from structure section of xml document
			r = []
			for i in self.structure_element.children:
				if obj.id == i.attributes["id"]:
					r.append(i)
				else:
					for l in i.children:
						for o in l.children:
							if obj.id == o.attributes["id"]:
								r.append(o)
			for item in r:
				item.delete()

		# remove events
		for cont_id in self.events:
			if obj.id in self.events[cont_id]:
				for ev_name in self.events[cont_id][obj.id]:
					self.e2vdom_events_element.children.remove(self.events[cont_id][obj.id][ev_name].xml_obj)
					self.events[cont_id][obj.id][ev_name].xml_obj.delete()
				del self.events[cont_id][obj.id]
				del self.events_by_object[obj.id]

		to_remove = []
		for _id in self.actions:
			if obj.id == self.actions[_id].target_object:
				to_remove.append(_id)
		for _id in to_remove:
			self.e2vdom_actions_element.children.remove(self.actions[_id].xml_obj)
			self.actions[_id].xml_obj.delete()
			del self.actions[_id]
		for cont_id in self.events:
			for s_id in self.events[cont_id]:
				for ev_name in self.events[cont_id][s_id]:
					for _id in to_remove:
						if _id in self.events[cont_id][s_id][ev_name].actions:
							self.events[cont_id][s_id][ev_name].actions.remove(_id)

		# now delete object itself
		# check copy object
		if "copy" == obj.type.name:
			val = obj.get_attributes()["source_object"].value
			obj1 = self.search_object(val)	# try to find the source object
			if obj1:
				obj1.copy_objects.remove(obj.id)
			if obj.toplevel.has_copy > 0:
				obj.toplevel.has_copy -= 1

		# delete object xml element
		if obj.xml_obj:
			obj.xml_obj.delete()

		# delete source code
		obj.invalidate()
		# delete resources
#		for ii in obj.resources.keys():
#			for j in xrange(obj.resources[ii]):
#				managers.resource_manager.delete_resource(obj.id, ii, True)
		managers.resource_manager.invalidate_resources(obj.id)
		# remove from parent
		if obj.parent:
			del obj.parent.objects[obj.id]
			del obj.parent.objects_by_name[obj.name]
		del self.__all_objects[obj.id]
		del obj.application
		del obj.toplevel
		del obj.attributes

		decrease_objects_count(self)

		return True

	def __do_search_server_action(self, obj, _id):
		for o in obj.objects_list:
			if _id in o.actions["id"]:
				return (o.actions["id"][_id], o)
			(_r1, _r2) = self.__do_search_server_action(o, _id)
			if _r1 and _r2:
				return (_r1, _r2)
		return (None, None)

# ======= public interface ===================================================================================

	def search_object(self, id_obj):
		"""find object in the application"""
		if id_obj in self.__all_objects:
			return self.__all_objects[id_obj]
		else:
			return None

	def search_objects_by_name(self, name):
		"""find objects in the application by name"""
		ret = []
		x = name.lower()
		for _id in self.__all_objects:
			if x == self.__all_objects[_id].name:
				ret.append(self.__all_objects[_id])
		return ret

	def search(self, pattern):
		# return map top level object id to the list of objects id where pattern is found
		if not managers.acl_manager.session_user_has_access2(self.id, self.id, security.modify_application):
			raise VDOM_exception_sec(_("Searching is not allowed"))
		result = {}
		for obj in self.objects_list:
			r = obj.search(pattern)
			if len(r) > 0:
				result[obj.id] = r
		return result

	def search_server_action(self, _id):
		return self.__do_search_server_action(self, _id)

	def create_resource(self, resid, restype, resname, resdata):
		"""create application resource"""
		if not managers.acl_manager.session_user_has_access2(self.id, self.id, security.modify_application):
			raise VDOM_exception_sec(_("Creating resource is not allowed"))
		self.__sem.lock()
		try:
			attributes = {
				"id" : resid,
				"name" : resname,
				"res_format": restype
				}
			managers.resource_manager.add_resource(self.id, None, attributes, resdata)
		finally:
			self.__sem.unlock()

	def delete_object(self, obj):
		if not managers.acl_manager.session_user_has_access2(self.id, obj.id, security.delete_object):
			raise VDOM_exception_sec(_("Deleting object is not allowed"))
		self.__sem.lock()
		try:
			ret = self.__do_delete_object(obj)
			return ret
		finally:
			self.__sem.unlock()

	def create_object(self, typeid, parent = None, do_compute=True):
		if parent:
			if not managers.acl_manager.session_user_has_access2(self.id, parent.id, security.create_object):
				raise VDOM_exception_sec(_("Creating object is not allowed"))
		else:
			if not managers.acl_manager.session_user_has_access2(self.id, self.id, security.create_object):
				raise VDOM_exception_sec(_("Creating object is not allowed"))
		try:
			l = int(system_options["object_amount"])
			if "1" != system_options["server_license_type"] and managers.xml_manager.obj_count >= l:
				raise VDOM_exception_lic(_("License exceeded"))
		except VDOM_exception, e:
			raise
		except: pass
		self.__sem.lock()
		try:
			ret = self.__do_create_object(typeid, parent, do_compute)
			return ret
		finally:
			self.__sem.unlock()

	def sync(self):
		"""save xml document to file"""
		self.xml_manager.app_sync(self.id)

	def set_info(self, name, value):
		"""set value of an information element"""
		if not managers.acl_manager.session_user_has_access2(self.id, self.id, security.modify_application):
			raise VDOM_exception_sec(_("Modifying application is not allowed"))
		lname = name.lower()
		if lname in self.info_map:
			self.__sem.lock()
			try:
				x = self.information_element.get_child_by_name(name)
				if not x:	# don't have this element created yet
					x = xml_object(name=name)
					self.information_element.children.append(x)
				x.value = value

				_value = self.test4res(value, None)
				oldv = ""
				if hasattr(self, "__" + lname + "_original"):
					oldv = getattr(self, "__" + lname + "_original")
				on_attr_change(self, oldv, value, self.id)
				# set property
				exec "self." + self.info_map[lname][0] + " = " + (self.info_map[lname][1] % "_value")
				exec "self.__" + self.info_map[lname][0] + "_original = " + (self.info_map[lname][1] % "value")
			finally:
				self.__sem.unlock()
		else:
			raise VDOM_exception_element(name)

	def get_objects(self):
		"""get list of top-level objects"""
		return self.objects

	def get_objects_by_name(self):
		return dict(map(lambda x: (x.name, x), self.objects_list))

	def get_all_objects(self):
		"""get hash of all objects"""
		return self.__all_objects

	def get_objects_list(self):
		"""get list of top-level objects in the order they occure in xml"""
		return self.objects_list

	def set_structure(self, xml_obj):
		self.__sem.lock()
		try:
			self.do_parse_structure(xml_obj)
			self.structure_element.delete()
			self.structure_element = self.__xml_obj.append_as_copy(xml_obj)
		finally:
			self.__sem.unlock()

	def set_library(self, name, data):
		if not is_valid_identifier(name):
			raise SOAPpy.faultType(lib_name_error, _("Incorrect library name"), "")
		self.__sem.lock()
		try:
			item = None
			for child in self.libraries_element.children:
				if name == child.attributes["name"]:
					item = child
					break
			if item:
				item.value = data
			else:
				x = xml_object(name="Library")
				x.attributes["Name"] = name
				self.libraries_element.children.append(x)
				x.value = data
			if "vscript" == self.scripting_language:
				try:
					x, y = vcompile(data, bytecode = 0)
					managers.file_manager.write_lib(self.id, name, x)
					self.libs[name] = y
				except:
					pass
			else:
				managers.file_manager.write_lib(self.id, name, data)
				self.libs[name] = None
			self.invalidate_libraries()
		finally:
			self.__sem.unlock()
	
	def remove_library(self, name):
		self.__sem.lock()
		try:
			item = None
			for child in self.libraries_element.children:
				if name == child.attributes["name"]:
					item = child
					break
			if item:
				item.delete()
				managers.file_manager.delete_lib(self.id, name)
				if name in self.libs:
					self.libs.pop(name)
		finally:
			self.__sem.unlock()
	def invalidate_libraries(self):
		"""Function to clear libraries cache"""
		for _name in self.libs:
			_module_name = "%s.%s"%(self.id,_name)
			if _module_name in sys.modules:
				sys.modules.pop(_module_name)
				
	def set_global_actions(self, xml_obj):
		self.__sem.lock()
		try:
			self.global_actions = {}
			self.parse_actions(xml_obj)
			self.actions_element.delete()
			self.actions_element = self.__xml_obj.append_as_copy(xml_obj)
		finally:
			self.__sem.unlock()

	def set_global_action(self, category, actionid, actionvalue):
		self.__sem.lock()
		try:
			global_action = self.global_actions[category][actionid]
			global_action.code = actionvalue
			
			action_node = None
			for child in self.actions_element.children:
				if "Action" == child.name and child.attributes["ID"] == actionid:
					action_node = child
					break;
			if action_node:
				action_node.value = actionvalue
			else:
				action_code = """<Action ID="%s" Name="%s" Top="" Left="" State=""><![CDATA[%s]]></Action>""" % (global_action.id, global_action.name, actionvalue)
				action_node = xml_object(srcdata=action_code.encode("utf-8"))
				self.actions_element.append_as_copy(action_node)
				action_node.delete()				
		finally:
			self.__sem.unlock()
			
	def set_e2vdom_events(self, obj, xml_obj):
		if not managers.acl_manager.session_user_has_access2(self.id, self.id, security.modify_application):
			raise VDOM_exception_sec(_("Modifying application is not allowed"))
		self.__sem.lock()
		try:
			# remove all events of the container
			if obj.id in self.events:
				for src_id in self.events[obj.id]:
					for ev_name in self.events[obj.id][src_id]:
						self.events[obj.id][src_id][ev_name].xml_obj.delete()
					if src_id in self.events_by_object:
						del self.events_by_object[src_id]
				self.events[obj.id] = {}
			for child in xml_obj.children:
				if "event" == child.lname:
					e = self.parse_e2vdom_event(child)
					if e:
						x = self.e2vdom_events_element.append_as_copy(child)
						e.xml_obj = x
		finally:
			self.__sem.unlock()

	def set_e2vdom_actions(self, obj, xml_obj):
		if not managers.acl_manager.session_user_has_access2(self.id, self.id, security.modify_application):
			raise VDOM_exception_sec(_("Modifying application is not allowed"))
		self.__sem.lock()
		try:
			# remove all actions of the container
			to_remove = []
			ll = obj.get_all_children()
			for a_id in self.actions:
				tgt_id = self.actions[a_id].target_object
				if tgt_id in obj.objects or tgt_id == obj.id or tgt_id in ll:
					self.actions[a_id].xml_obj.delete()
					to_remove.append(a_id)
			for i in to_remove:
				del self.actions[i]
			for child in xml_obj.children:
				if "action" == child.lname:
					e = self.parse_e2vdom_action(child)
					x = self.e2vdom_actions_element.append_as_copy(child)
					e.xml_obj = x
		finally:
			self.__sem.unlock()
	
	def remove_action(self, obj, actionid):
		if not managers.acl_manager.session_user_has_access2(self.id, self.id, security.modify_application):
			raise VDOM_exception_sec(_("Modifying application is not allowed"))
		self.__sem.lock()
		try:
			if actionid in self.actions:
				ll = obj.get_all_children()
				tgt_id = self.actions[actionid].target_object
				if tgt_id in obj.objects or tgt_id == obj.id or tgt_id in ll:
					self.actions[actionid].xml_obj.delete()
					del self.actions[actionid]
		finally:
			self.__sem.unlock()	
			
	def create_server_action(self, actionname,  value):
		if not managers.acl_manager.session_user_has_access2(self.id, self.id, security.modify_application):
			raise VDOM_exception_sec(_("Modifying application is not allowed"))
		self.__sem.lock()
		try:
			_id = str(uuid4())
			self.global_actions[_id] = {}
			self.global_actions[_id][actionname.lower()] = VDOM_server_action(value, _id, "", "", "", actionname)
			
		finally:
			self.__sem.unlock()	
	
	def get_xml_as_string(self):
		"""get xml document as string"""
		self.__sem.lock()
		try:
			return self.__xml_obj.toxml()
		finally:
			self.__sem.unlock()

	def get_backup_files(self):
		return list(self.__backup_files)

	def add_backup_file(self, filename):
		if filename in self.__backup_files: return
		self.__backup_files[filename]=xml_obj=xml_object(name="File")
		xml_obj.attributes["Name"]=filename
		self.backupfiles_element.children.append(xml_obj)

	def remove_backup_file(self, filename):
		xml_obj=self.__backup_files.get(filename, None)
		if xml_obj is not None:
			xml_obj.delete()
			del self.__backup_files[filename]

	# --- locking --------------------------------------------------------------------------------------

	def lock_read(self):	# lock for read
		self.__1sem.lock()
		i = thread.get_ident()
		if i in self.__read_locks:	# already have the lock
			self.__1sem.unlock()
			return
		if len(self.__write_locks) > 0:
			# have to block here until no more write locks
			self.__cond_write.acquire()
			self.__1sem.unlock()
			self.__cond_write.wait()
			self.__1sem.lock()
		if i not in self.__read_locks:
			self.__read_locks.append(i)
		self.__1sem.unlock()

	def lock_write(self):	# lock for write
		self.__1sem.lock()
		i = thread.get_ident()
		if i in self.__write_locks:	# already have the lock
			self.__1sem.unlock()
			return
		if 0 != len(self.__write_locks):
			self.__1sem.unlock()
			raise VDOM_exception_restart()
		if i in self.__read_locks:	# remove its read lock
			self.__read_locks.remove(i)
		if i not in self.__write_locks:
			self.__write_locks.append(i)
		if 0 == len(self.__read_locks) and 0 == len(self.__write_locks):	# can go
			self.__1sem.unlock()
			return
		# have to block here until all read locks are released
		self.__cond_read.acquire()
		self.__1sem.unlock()
		self.__cond_read.wait()

	def release(self):	# this is called from the session thread when the session is about to be closed
		self.__1sem.lock()
		i = thread.get_ident()
		if i in self.__read_locks:
			self.__read_locks.remove(i)
		if i in self.__write_locks:
			self.__write_locks.remove(i)
		if 0 == len(self.__read_locks) and 0 == len(self.__write_locks):	# nobody's waiting
			pass
		elif 0 != len(self.__write_locks):	# wake up thread waiting for write
			self.__cond_read.notify()
			self.__cond_read.release()
		else:	# wake up thread waiting for read
			self.__cond_write.notify()
			self.__cond_write.release()
		self.__1sem.unlock()


import managers, file_access, security

from version import VDOM_server_version
from utils.mutex import VDOM_named_mutex_auto
from soap.errors import *
from utils.encode import *

from event import *
from object import on_attr_change, VDOM_object
from xml_object import xml_object
from structure import VDOM_structure_level, VDOM_structure_item

from utils.uuid import uuid4
from utils.semaphore import VDOM_semaphore
from utils.exception import *
from utils.id import is_valid_identifier

from vscript.engine import vcompile
