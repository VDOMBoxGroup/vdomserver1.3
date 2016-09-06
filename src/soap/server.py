"""web services server"""

import sys, os, time, zlib, base64, copy, traceback, tempfile, shutil, SOAPpy


import managers, security
from errors import *
import utils
from utils.encode import *
from utils.semaphore import VDOM_semaphore
from utils.mutex import VDOM_named_mutex_auto
from utils.exception import *
import soaputils
from utils.uuid import uuid4
from memory.xml_object import xml_object # memory.
from database.dbobject import VDOM_sql_query
from utils.app_management import import_application, update_application, uninstall_application
from version import VDOM_server_version

sessions = {}	# opened sessions
names = {}	# logged in users


class VDOM_web_services_server(object):
	"""class that implements web services methods"""

	def __init__(self):
		"""constructor"""
		self.__sem = VDOM_semaphore()

	def __check_session(self, sid, skey):
		"""check authentication and session key"""
#		debug("*****")
#		debug(str(sid))
#		debug("*****")
		autolock = VDOM_named_mutex_auto(sid)

		ret = True

		mngr = managers.session_manager
		sess = mngr[sid]
		if not sess:
			raise SOAPpy.faultType(session_id_error, _("Session ID error"), _("Invalid session ID supplied"))
			#ret = False	# invalid session id

		if not sess["login"]:
			ret = False	# not logged in

		if sid not in sessions:
			ret = False	# invalid session id

		if not ret:
			self.__term_session(sid)
			return False

		# now check session key value
		parts = skey.split("_")	# getting key and index
		_key = parts[0] # received key
		_index = parts[1] # received number of the key
#		debug("Got key %s and index %s" % (parts[0], parts[1]))
		keymap = sess["keymap"]
		keyindex = sess["keyindex"]
		keylast = sess["keylast"]
		pr = sessions[sid]
		try:
			if int(_index) < keyindex and _index not in keymap:
				raise VDOM_exception_sec("Incorrect key")	# means this key has already been used
		except:
			self.__term_session(sid)
			return False
		if _index not in keymap:	# don't have a key generated for this number
			# generate keys
			keymap[str(keyindex)] = pr.next_session_key(keylast)
			for ii in xrange(keyindex + 1, int(_index) + 10):	# generate 10 more keys than needed
				keymap[str(ii)] = pr.next_session_key(keymap[str(ii-1)])
			sess["keyindex"] = int(_index) + 10
			sess["keylast"] = keymap[str(int(_index) + 9)]

#		debug("Must be: " + keymap[parts[1]])
		if _key != keymap[_index]:
			self.__term_session(sid)
			return False
		del keymap[_index]
		return True

	def __term_session(self, sid):
		"""terminate session"""
		self.__sem.lock()
		try:
			# remove protector object
			try: del sessions[sid]
			except: pass
			# remove session
			mngr = managers.session_manager
			sess = None
			try:
				sess = mngr[sid]
				name = sess.user#["username"]
				if name in names:
					del names[name]
			except:
				pass
			del mngr[sid]
		finally:
			self.__sem.unlock()

	def __format_error(self, msg,*msgs):
		"""prepare error xml message"""
		return "<Error><![CDATA[%s%s]]></Error>" % (msg, "".join(msgs))

	def __session_key_error(self):
		"""prepare session key error xml message"""
		raise SOAPpy.faultType(session_key_error, _("Session key error"), _("Invalid session key supplied, your session has been closed"))
#		return self.__format_error(_("Invalid session key supplied. Your session has been closed."))

	def __success(self):
		"""get xml representing successful result"""
		return "<Result>OK</Result>"


### session methods =================================================================================

	def open_session(self, name, pwd_md5):
		"""open session with the server"""
		self.__sem.lock()
		try:
			if not managers.user_manager.match_user_md5(name, pwd_md5):
				time.sleep(1)
				#self.__sem.unlock()
				raise SOAPpy.faultType(login_incorrect_error, _("Login incorrect"), _("<Error><User>%s</User></Error>") % name)
	#			return self.__format_error(_("Login incorrect"))
		finally:
			self.__sem.unlock()
		# open session
		mngr = managers.session_manager
		sid = mngr.create_session()
		sess = mngr.get_session(sid)
		sess.value("login", "1")
		#sess.value("username", name)
		sess.set_user(name, pwd_md5, md5=True)

		# create protector object
		hash_string = soaputils.get_hash_str()
		session_key = soaputils.get_session_key()
		pr = soaputils.VDOM_session_protector(hash_string)
		# save protector object
		self.__sem.lock()
		try:
			sessions[sid] = pr
		finally:
			self.__sem.unlock()

		keymap = {}
		# generate next session key (with index 0)
		keymap["0"] = pr.next_session_key(session_key)
#		debug("Key 0: " + keymap["0"])

		# store map {key number : key value} in session
		sess.value("keymap", keymap)
		# store next key index
		sess.value("keyindex", 1)
		# store last generated key value
		sess.value("keylast", keymap["0"])

		# return
		ret = "<Session>"
		ret += "<SessionId><![CDATA[%s]]></SessionId>" % sid
		ret += "<SessionKey><![CDATA[%s]]></SessionKey>" % session_key
		ret += "<HashString><![CDATA[%s]]></HashString>" % hash_string
		ret += "</Session>"
		ret += "<Hostname>%s</Hostname>" % managers.request_manager.get_request().app_vhname
		ret += "<Username>%s</Username>" % name
		ret += "<ServerVersion>%s</ServerVersion>" % VDOM_server_version
#		managers.request_manager.get_request().cookies().cookie("sid", sid)
		return ret

	def close_session(self, sid):
		"""close session"""
		self.__term_session(sid)
		return self.__success()
### =================================================================================================

	def __parse_attr(self, attr, namefromtag = True, lowercase = False):
		param = {}
		root = None
		try:
			root = xml_object(srcdata=attr.encode("utf-8"))
			for child in root.children:
				name = ""
				if namefromtag:
					name = child.name
				else:
					name = child.attributes["name"]
				if "" == name:
					continue
				if lowercase:
					name = name.lower()
				param[name] = child.get_value_as_xml()
			root.delete()
		except:
			if root:
				root.delete()
		return param

	def __app_info(self, app):
		result = ""
		for key in app.info_map:
			cap = app.info_map[key][2]
			result += "<%s>%s</%s>\n" % (cap, self.__attrvalue(getattr(app, app.info_map[key][0])), cap)
		# add statistics
		default_app = "True" if managers.virtual_hosts.get_def_site() == app.id else "False"
		result += '<Hosts default="%s">\n' % default_app
		sites = managers.virtual_hosts.get_sites()
		for site in sites:
			if app.id == managers.virtual_hosts.get_site(site):
				result += "<Host>%s</Host>\n" % site
		result += "</Hosts>\n"
		result += "<Numberofpages>%d</Numberofpages>\n" % len(app.objects)
		result += "<Numberofobjects>%d</Numberofobjects>\n" % app.objects_amount()
		return "<Information>\n%s</Information>\n" % result

### application methods =============================================================================

	def create_application(self, sid, skey, attr):
		"""create new application"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		mngr = managers.xml_manager
		appid = mngr.create_application()
		app = mngr.get_application(appid)
		try:
			param = self.__parse_attr(attr)
			for key in param.keys():
				app.set_info(key, param[key])
			app.sync()
		except:
			raise SOAPpy.faultType(app_attr_error, _("Create application error"), _("Error setting information"))
#			return self.__format_error(_("Error setting information"))
		return "<Application ID=\"%s\">\n%s</Application>" % (appid, self.__app_info(app))

	def set_application_info(self, sid, skey, appid, attr):
		"""set application info attributes"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		param = self.__parse_attr(attr)
		for key in param.keys():
			ret[0].set_info(key, param[key])
		ret[0].sync()
		return self.__app_info(ret[0])

	def get_application_info(self, sid, skey, appid):
		"""get application info attributes"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		return self.__app_info(ret[0])

	def __do_list_applications(self, right):
		result = "<Applications>"
		mngr = managers.xml_manager
		applst = mngr.get_applications()
		for appid in applst:
			app = None
			try: app = mngr.get_application(appid)
			except: pass
			if app and managers.acl_manager.session_user_has_access2(app.id, app.id, right):
				appname = app.name
				if "" == appname:
					appname = _("Not specified")
				result += "<Application ID=\"%s\">\n" % appid
				result += self.__app_info(app)
				result += "</Application>"
		result += "</Applications>"
		return result

	def list_applications(self, sid, skey):
		"""get the list of installed applications"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		return self.__do_list_applications(security.list_application)

	def get_resource(self, sid, skey, owner_id, resource_id):
		"""get resource"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		try:
			ro = managers.resource_manager.get_resource(owner_id, resource_id)
			data = ro.get_data()
			return "<Resource><![CDATA[%s]]></Resource>\n<ResourceID>%s</ResourceID>\n<ResourceName>%s</ResourceName>\n<ResourceType>%s</ResourceType>\n<ResourceUseCount>%s</ResourceUseCount>" % (utils.encode.encode_resource(data), resource_id, ro.name, ro.res_format, len(ro.dependences))
		except Exception, e:
			#traceback.print_exc(file=debugfile)
			#debug("Get type resource error: " + str(e))
			raise SOAPpy.faultType(resource_not_found_error, _("Resource not found"), _("<Error><ResourceID>%s</ResourceID></Error>") % resource_id)
#			return self.__format_error(_("Resource not found")) + ("\n<ResourceID>%s</ResourceID>" % resource_id)

	def list_resources(self, sid, skey, owner_id):
		"""list resources"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		result = "<Resources>\n"
		res = managers.resource_manager.list_resources(owner_id)
		for resid in res:
			try:
				ro = managers.resource_manager.get_resource(owner_id, resid)
			except:
				continue
			if not getattr(ro,"label",None): #TODO: in new version label will always non exist. So no meanin in this line
				result += """<Resource id="%s" name="%s" type="%s" usecount="%s"/>\n""" % (ro.id, ro.name, ro.res_format,len(ro.dependences))
		result += "</Resources>\n"
		return result

	def get_application_language_data(self, sid, skey, appid):
		"""get application language data"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		return ret[0].languages

	def get_application_structure(self, sid, skey, appid):
		"""get application structure"""
		autolock = VDOM_named_mutex_auto(appid + "_structure")
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		if not managers.acl_manager.session_user_has_access2(appid, appid,security.access_to_application):
			raise SOAPpy.faultType(render_wysiwyg_error, "You have no access to structure of this application", _("<Error/>"))				
		return ret[0].structure_element.toxml()

	def set_application_structure(self, sid, skey, appid, struct):
		"""set application structure"""
		autolock = VDOM_named_mutex_auto(appid + "_structure")
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, errmsg) = self.__find_application(appid)
		if not app:
			return errmsg
		x = None
		try:
			x = xml_object(srcdata=struct)
			if "structure" != x.lname:
				raise VDOM_exception_element("root")
			for child in x.children:
				if "object" != child.lname:
					raise VDOM_exception_element(child.name)
				else:
					id_value = child.attributes["id"]
					if not app.search_object(id_value):	# unknown object
						raise VDOM_exception_element("object id=" + id_value)
					# process level nodes
					for child2 in child.children:
						if "level" != child2.lname:
							raise VDOM_exception_element(child2.name)
						# process object nodes
						for child3 in child2.children:
							if "object" != child3.lname:
								raise VDOM_exception_element(child3.name)
							else:
								id_value = child3.attributes["id"]
								if not app.search_object(id_value):	# unknown object
									raise VDOM_exception_element("object id=" + id_value)
		except Exception, e:
			import traceback
			traceback.print_exc(file=debugfile)
			if x:
				x.delete()
			raise SOAPpy.faultType(struct_check_error, _("Structure validation error (1)"), str(e))
		try:
			app.set_structure(x)
		except Exception, e:
			import traceback
			traceback.print_exc(file=debugfile)
			x.delete()
			raise SOAPpy.faultType(struct_check_error, _("Structure validation error (2)"), str(e))
		x.delete()
		app.sync()
		return self.__success()

	def set_resource(self, sid, skey, appid, restype, resname, resdata):
		"""set application resource"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		app = ret[0]
		# decode resource data
		resdata = zlib.decompress(base64.b64decode(resdata))
		new_resource_id = str(uuid4())
		app.create_resource(new_resource_id, restype, resname, resdata)
		app.sync()
		return "<Resource id=\"%s\"/>" % new_resource_id

	def update_resource(self, sid, skey, appid, resid, resdata):
		"""set application resource"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, errmsg) = self.__find_application(appid)	# returns (app, error_message)
		if not app:
			return errmsg
		# decode resource data
		resdata = zlib.decompress(base64.b64decode(resdata))
		managers.resource_manager.update_resource(appid, resid, resdata)
		app.sync()
		return "<Resource id=\"%s\"/>" % resid

	def delete_resource(self, sid, skey, appid, resid):
		"""set application resource"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, errmsg) = self.__find_application(appid)	# returns (app, error_message)
		if not app:
			return errmsg
		managers.resource_manager.delete_resource(appid, resid, True)
		return  "<Resource>%s</Resource>"%resid

	def create_object(self, sid, skey, appid, parentid, typeid, name, attr):
		"""create object in the application"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		mngr = managers.xml_manager
		app = ret[0]
		ret = None
		if parentid == "":
			# creating top-level object
			ret = app.create_object(typeid)
		else:
			# creating object inside another object
			# find parent object
			obj = None
			try:
				obj = mngr.search_object(appid, parentid)
			except:
				raise SOAPpy.faultType(parent_object_error, _("Create object error"), _("Parent object not found"))
#				return self.__format_error(_("Parent object not found"))
			# creating child object
			ret = app.create_object(typeid, obj)
		obj_name = ret[0]
		obj_id = ret[1]
		obj = app.search_object(obj_id)
		#debug("Created object " + str(ret))

		if "" != attr:
			self.__set_attributes(obj, attr)

		if name:
			try:
				obj.set_name(name)
			except VDOM_exception, e:
				debug(unicode(e))

		app.sync()
		return self.__get_object(obj) + ("\n<ApplicationID>%s</ApplicationID>" % appid)

	def copy_object(self, sid, skey, appid, parentid, objid, tgt_appid = None):
		"""copy object in application"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		app = ret[0]

		tgt_app = None
		try:
			obj = managers.xml_manager.search_object(appid, objid)
			if obj:
				for o in obj.objects:
					if o == parentid:
						raise SOAPpy.faultType(parent_object_error, _("Create object error"), _("Parent object is the child of copying object"))
			if tgt_appid:
				ret = self.__find_application(tgt_appid)	# returns (app, error_message)
				if not ret[0]:
					return ret[1]
				tgt_app = ret[0]
				appid = tgt_appid
				managers.request_manager.current.set_application_id(tgt_appid)
			if objid == parentid:
				raise SOAPpy.faultType(parent_object_error, _("Create object error"), _("Parent object is the same as copying object"))

			action_map = {}
			obj_map = {}
			new_obj_id = self.__copy_object(app, parentid, objid, obj_map, action_map, tgt_app)
			if not tgt_app:
				tgt_app = app
			copy_obj = managers.xml_manager.search_object(appid, new_obj_id)
			self.__copy_events_structure(app, obj, copy_obj, obj_map, action_map, tgt_app)

			tgt_app.sync()
			return self.__get_object(copy_obj) + ("\n<ApplicationID>%s</ApplicationID>" % appid)
		except Exception, e:
			return self.__format_error(str(e))

	def move_object(self, sid, skey, appid, parentid, objid):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		app = ret[0]
		try:
			obj = managers.xml_manager.search_object(appid, objid)
			parent = managers.xml_manager.search_object(appid, parentid)
			if 1 == parent.type.container:
				raise SOAPpy.faultType(parent_object_error, _("Create object error"), _("Parent object is not container"))
			if objid == parentid:
				raise SOAPpy.faultType(parent_object_error, _("Create object error"), _("Parent object is the same as moving object"))
			if obj:
				for o in obj.objects:
					if o == parentid:
						raise SOAPpy.faultType(parent_object_error, _("Create object error"), _("Parent object is the child of moving object"))
			obj.xml_obj.exclude()
			parent.objects_element.append_as_copy(obj.xml_obj)
			obj.parent.objects_list.remove(obj)
			del obj.parent.objects[obj.id]
			del obj.parent.objects_by_name[obj.name]
			obj.parent = parent
			obj.toplevel = parent.toplevel
			parent.get_objects()[obj.id] = obj
			parent.get_objects_list().append(obj)
			parent.objects_by_name[obj.name] = obj
			app.sync()
			return self.__get_object(obj) + ("\n<ApplicationID>%s</ApplicationID>" % appid)
		except Exception, e:
			return self.__format_error(str(e))		

	def delete_object(self, sid, skey, appid, objid):
		"""delete object from application"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_object(appid, objid)	# returns (app, obj, error_message)
		if not ret[0]:
			return ret[2]
		# delete object
		succ = ret[0].delete_object(ret[1])
		if not succ:
			raise SOAPpy.faultType(delete_object_error, _("Delete object error"), _("Delete object error"))
#			return self.__format_error(_("Can't delete this object"))
		ret[0].sync()
		return "<Result>%s</Result>" % objid

## type methods ====================================================================================

	def list_types(self, sid, skey):
		"""get the list of installed types"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		result = "<Types>"
		mngr = managers.xml_manager
		typelst = mngr.get_types()
		for typeid in typelst:
			tp = None
			try: tp = mngr.get_type(typeid)
			except: pass
			if tp:
				typename = tp.name
				if "" == typename:
					typename = _("Not specified")
				version = tp.version
				if "" == version:
					version = _("Not specified")
				result += "<Type id=\"%s\" name=\"%s\" version=\"%s\" />" % (typeid, typename, version)
		result += "</Types>"
		return result

	def get_type(self, sid, skey, typeid):
		"""get type description"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		try:
			type_obj = managers.xml_manager.get_type(typeid)
			return type_obj.get_xml_as_string()
		except:
			raise SOAPpy.faultType(type_id_error, _("Get type error"), _("Type not registered"))
#			return self.__format_error(_("Type \"%s\" not registered" % typeid))

	def set_type(self, sid, skey, typexml):
		"""add/update type"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = managers.server_manager.set_type(typexml)
		if ret[0]:
			return self.__success()
		else:
			return self.__format_error(ret[1])

	def get_all_types(self, sid, skey):
		"""get all types description"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		result = "<Types>"
		mngr = managers.xml_manager
		typelst = mngr.get_types()
		for typeid in typelst:
			tp = None
			try: tp = mngr.get_type(typeid)
			except: pass
			if tp:
				result += tp.get_xml_as_string()
		result += "</Types>"
		result = result.replace('<?xml version="1.0" encoding="utf-8"?>\n', '')
		result = '<?xml version="1.0" encoding="utf-8"?>\n%s' % result
		return result

### object methods ====================================================================================

	def __find_object(self, appid, objid):
		"""find object with given id in the application"""
		mngr = managers.xml_manager
		app = None
		try:
			app = mngr.get_application(appid)
		except:
			raise SOAPpy.faultType(app_id_error, "Application not found", _("<Error><ApplicationID>%s</ApplicationID></Error>") % appid)
			#return (None, None, self.__format_error(_("Application not found")))
		# find object
		obj = None
		try:
			obj = app.search_object(objid)
		except:
			raise SOAPpy.faultType(object_id_error, "Object not found", _("<Error><ObjectID>%s</ObjectID></Error>") % objid)
#			return (None, None, self.__format_error(_("Object not found")))
		if not obj:
			raise SOAPpy.faultType(object_id_error, "Object not found", _("<Error><ObjectID>%s</ObjectID></Error>") % objid)
#			return (None, None, self.__format_error(_("Object not found")))
		return (app, obj, None)

	def __find_application(self, appid):
		"""find application"""
		mngr = managers.xml_manager
		app = None
		try:
			app = mngr.get_application(appid)
		except:
			raise SOAPpy.faultType(app_id_error, "Application not found", _("<Error><ApplicationID>%s</ApplicationID></Error>") % appid)
#			return (None, self.__format_error(_("Application not found")))
		return (app, None)

	def render_wysiwyg(self, sid, skey, appid, objid, parentid, dynamic):
		"""render object to xml presentation"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_object(appid, objid)	# returns (app, obj, error_message)
		if not ret[0]:
			return ret[2]
		if not managers.acl_manager.session_user_has_access2(appid, appid,security.access_to_application):
			raise SOAPpy.faultType(render_wysiwyg_error, "You have no access to this application", _("<Error><ObjectID>%s</ObjectID><ParentID>%s</ParentID></Error>") % (objid, parentid))
		_p = ret[0].search_object(parentid)
		managers.request_manager.get_request().container_id = ret[1].toplevel.id
		try:
			rend = managers.engine.wysiwyg(ret[0], ret[1], _p, dynamic)
			return "<Result>%s</Result>\n<ParentID>%s</ParentID>\n<ObjectID>%s</ObjectID>" % (rend, parentid, objid)
		except:
			traceback.print_exc(file=debugfile)
			raise SOAPpy.faultType(render_wysiwyg_error, "Render wysiwyg error", _("<Error><ObjectID>%s</ObjectID><ParentID>%s</ParentID></Error>") % (objid, parentid))

	def __do_get_object_script_presentation(self, obj, depth = 0):
		tag_name = obj.type.name.upper()
		prep = "\t" * depth
		result = prep + "<" + tag_name + " name=\"" + obj.original_name + "\""
		# simple attributes
		ext = []
		for aname in obj.get_attributes():
			val = obj.get_attributes()[aname].value
			if val != obj.type.get_attributes()[aname].default_value:
				if not need_xml_escape(val):
					result += " " + aname + "=\"" + val + "\""
				else:
					ext.append(aname)
		if len(ext) > 0 or len(obj.get_objects_list()) > 0:
			result += ">\n"
		else:
			result += "/>\n"
		# extended attributes
		for aname in ext:
			val = obj.get_attributes()[aname].value
			result += prep + "\t<Attribute Name=\"" + aname + "\"><![CDATA[" + val + "]]></Attribute>\n"
		# child objects
		for o in obj.get_objects_list():
			result += self.__do_get_object_script_presentation(o, depth + 1)
		if len(ext) > 0 or len(obj.get_objects_list()) > 0:
			result += prep + "</" + tag_name + ">\n"
		return result

	def get_object_script_presentation(self, sid, skey, appid, objid):
		"""get object xml script presentation"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_object(appid, objid)	# returns (app, obj, error_message)
		if not ret[0]:
			return ret[2]
		return "<Result>%s</Result>" % self.__do_get_object_script_presentation(ret[1])

	def __do_submit_object_script_presentation(self, app, obj, parent, xml_obj, do_create = False):
		attr_map = {}
		objects_inside = []
		if obj:
			objects_inside = copy.deepcopy(obj.get_objects_by_name().keys())
#			objects_inside.remove(obj.name)
		type_obj = managers.xml_manager.get_type_by_name(xml_obj.lname)
		for aname in type_obj.get_attributes():
			attr_map[aname.lower()] = type_obj.get_attributes()[aname].default_value
		# parse attributes
		for i in xml_obj.attributes:
			if i in attr_map or "name" == i:
				attr_map[i] = xml_obj.attributes[i]
			else:
				raise VDOM_exception_param(_("Incorrect attribute: %s") % i)
		for child in xml_obj.children:
			if "attribute" == child.lname:
				i = child.attributes["name"]
				if not i:
					continue
				if i in attr_map:
					attr_map[i] = child.get_value_as_xml()
				else:
					raise VDOM_exception_param(_("Incorrect attribute: %s") % i)
		if not do_create and type_obj != obj.type:
			do_create = True
			# delete current object
			app.delete_object(obj)
		if do_create:
			# create new object under <parent>
			ret = app.create_object(type_obj.id, parent, False)
			obj = app.search_object(ret[1])
		# write attributes to the object
		for aname in attr_map:
			if "name" == aname:
				try:
					obj.set_name(attr_map[aname])
				except VDOM_exception, e:
					raise SOAPpy.faultType(name_error, _("Name error"), "<Error><ObjectID>%s</ObjectID><Name>%s</Name></Error>" % (obj.id, attr_map[aname]))
			else:
				obj.set_attribute(aname, attr_map[aname], False)
		# process all child objects
		for child in xml_obj.children:
			if "attribute" != child.lname:
				if not do_create:
					# find object name and object by this name
					i = child.attributes["name"]
					if not i:
						continue
					obj1 = None
					_create = True
					if i in objects_inside:
						if i == obj.name:
							raise VDOM_exception_param(_("Incorrect name: %s") % str(i))
						obj1 = obj.get_objects_by_name()[i]
						_create = False
						objects_inside.remove(i)
					self.__do_submit_object_script_presentation(app, obj1, obj, child, _create)
				else:
					self.__do_submit_object_script_presentation(app, None, obj, child, do_create)
		# remove objects that remain in <objects_inside> list
		for oname in objects_inside:
			app.delete_object(obj.get_objects_by_name()[oname])
		return obj.id

	def submit_object_script_presentation(self, sid, skey, appid, objid, pres):
		"""submit object xml script presentation"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, obj, errmsg) = self.__find_object(appid, objid)	# returns (app, obj, error_message)
		if not app:
			return errmsg
		if "" == pres.strip():
			raise VDOM_exception_param(_("Empty data"))
		# parse xml presentation
		root = None
		try:
			root = xml_object(srcdata=pres.encode("utf-8"))
		except Exception, e:
			raise SOAPpy.faultType(xml_script_error, str(e), "<Error><ObjectID>%s</ObjectID></Error>" % objid)
			#return self.__format_error(_("Invalid argument: pres - " + str(e)))
		# start processing
		new_id = None
		try:
			new_id = self.__do_submit_object_script_presentation(app, obj, obj.parent, root)
		except VDOM_exception, e:
			app.sync()
			raise SOAPpy.faultType(xml_script_error, str(e), "<Error><ObjectID>%s</ObjectID></Error>" % objid)
#			return self.__format_error(str(e))
		app.sync()
		return "<IDOld>%s</IDOld>\n<IDNew>%s</IDNew>" % (obj.id, new_id)

	def __get_objects(self, parent):
		"""build objects xml"""
		result = ""
		for o in parent.get_objects_list():
			result += self.__get_object(o)
		return "<Objects>\n%s</Objects>" % result if result else ""

	def __get_object_list(self, parent):
		result = ''
		for o in parent.get_objects_list():
			result += '<Object Name="%s" ID="%s" Type="%s"/>' % (o.original_name, o.id, o.type.id)
		return '<Objects>%s</Objects>' % result if result else ""

	def __get_all_object_list(self, obj):
		result = "<Object Name=\"%s\" ID=\"%s\" Type=\"%s\">\n" % (obj.original_name, obj.id, obj.type.id)

		result += "<Objects>\n"
		for o in obj.get_objects_list():
			result += self.__get_all_object_list(o)
		result += "</Objects>\n"
		result += "</Object>\n"
		return result

	def __get_all_objects(self, obj):
		"""build xml of all child objects"""
		result = "<Object Name=\"%s\" ID=\"%s\" Type=\"%s\">\n" % (obj.original_name, obj.id, obj.type.id)
		# attributes
		result += "<Attributes>\n"
		for a in obj.get_attributes().values():
			result += "<Attribute Name=\"%s\">%s</Attribute>\n" % (a.name, self.__attrvalue(a.original_value))
		result += "</Attributes>\n"
#		result += "<Script>%s</Script>\n" % obj.script
		# put all child objects
		result += "<Objects>\n"
		for o in obj.get_objects_list():
			result += self.__get_all_objects(o)
		result += "</Objects>\n"
		result += self.__get_code_interface(obj)
		result += "</Object>\n"
		return result

	def __attrvalue(self, data):
		if need_xml_escape(data):
			result = data.replace("]]>", "]]]]><![CDATA[>")
			return "<![CDATA[" + result + "]]>"
		return data

	def __get_object(self, obj):
		"""build xml with object details"""
		result = "<Object Name=\"%s\" ID=\"%s\" Type=\"%s\">\n" % (obj.original_name, obj.id, obj.type.id)
		# attributes
		result += "<Attributes>\n"
		for a in obj.get_attributes().values():
			result += "<Attribute Name=\"%s\">%s</Attribute>\n" % (a.name, self.__attrvalue(a.original_value))
		result += "</Attributes>\n"
#		result += "<Objects/>\n"
		result += self.__get_code_interface(obj)
		result += "</Object>"
		return result

	def __get_code_interface(self, obj):
		result = ""
		app = obj.application
		if "pagelink" in obj.type.interfaces:
			result += "<Pagelink>\n"
#			result += """<Object ID="" Name=""/>\n"""
			for o in app.get_objects_list():
				result += """<Object ID="%s" Name="%s"/>\n""" % (o.id, o.name)
			result += "</Pagelink>\n"

		if "objectlist" in obj.type.interfaces and 1 == len(obj.type.interfaces["objectlist"]) and "" == obj.type.interfaces["objectlist"][0]:
			result += "<Objectlist>\n"
			for oid in app.get_all_objects():
				obj1 = app.search_object(oid)
				if "copy" != obj1.type.name:
					if None != obj1.parent and ("copy" != obj.type.name or 0 == obj1.toplevel.has_copy):#(oid not in obj.toplevel.all_child_objects):
						if "copy" == obj.type.name and obj.parent.type.name not in obj1.type.containers:
							continue
						result += """<Object ID="%s" Name="%s"/>\n""" % (obj1.id, obj1.name)
			result += "</Objectlist>\n"
		elif "objectlist" in obj.type.interfaces and 1 == len(obj.type.interfaces["objectlist"]):
			needed = obj.type.interfaces["objectlist"][0]
			result += "<Objectlist>\n"
			for oid in app.get_all_objects():
				obj1 = app.search_object(oid)
				if obj1.type.id == needed:
					result += """<Object ID="%s" Name="%s"/>\n""" % (obj1.id, obj1.name)
			result += "</Objectlist>\n"
		return result

	def __copy_object(self, app, parentid, objid, obj_map, action_map, newapp = None):
		"""copy object in application"""
		if newapp:
			appl = newapp
			do_compute = False
		else: 
			appl = app
			do_compute = True
		obj = app.search_object(objid)
		typeid = obj.type.id
		attr = {name:value.value for name, value in obj.get_attributes().items()}
		name = obj.name
		if parentid:
			try:
				container = appl.search_object(parentid)
			except:
				raise SOAPpy.faultType(parent_object_error, _("Create object error"), _("Parent object not found"))
			ret = appl.create_object(typeid, container, do_compute)
		else:
			ret = appl.create_object(typeid, None, do_compute)
		obj_id = ret[1]
		copy_object = appl.search_object(obj_id)
		if (parentid and parentid != obj.parent.id) or (newapp and newapp.id != app.id):
			try:
				copy_object.set_name(name)
			except:
				#raise SOAPpy.faultType(name_error, _("Name error"), "<Error><ObjectID>%s</ObjectID><Name>%s</Name></Error>" % (obj_id, str(name)))
				pass
		if attr:
			copy_object.set_attributes(attr)
		obj_map[objid] = copy_object.id
		xml_actions = ''
		server_actions_element = None
		if 1 != obj.type.container:
			xml_actions = '<ServerActions>\n'
			for _name in obj.actions["name"]:
				x = obj.actions["name"][_name]
				if _name in copy_object.actions["name"]:
					y = copy_object.actions["name"][_name]
					copy_object.set_action(y.id, x.code.replace("]]>","]]]]><![CDATA[>"))
					actionid = y.id
				else:
					actionid = copy_object.create_action(x.name, x.code.replace("]]>","]]]]><![CDATA[>"))
				xml_actions += """<Action ID="%s" Name="%s" ObjectID="%s"  ObjectName="%s" Top="%s" Left="%s" Language="" State="%s" />\n""" % (actionid, x.name, copy_object.id, copy_object.name, x.top, x.left, x.state)
				action_map[x.id] = actionid
			xml_actions += '</ServerActions>\n'
		if xml_actions:
			try:
				server_actions_element = xml_object(srcdata=xml_actions.encode("utf-8"))
				if "serveractions" != server_actions_element.lname:
					raise VDOM_exception_element(server_actions_element.lname)
				for child in server_actions_element.children:
					if "action" == child.lname:
						_id = child.attributes["id"]
						_name = child.attributes["name"]
						if not _id or not _name:
							raise VDOM_exception_element("server action")

			except Exception, e:
				if server_actions_element:
					server_actions_element.delete()
				raise SOAPpy.faultType(event_format_error, _("XML error"), str(e))

		xml_client_action = "<ClientActions>\n"	
		if obj:
			for a_id in app.actions:
				a = app.actions[a_id]
				if a.target_object == obj.id:
					actionid = str(uuid4()).upper()
					xml_client_action += """<Action ID="%s" ObjTgtID="%s" ObjTgtName="%s" MethodName="%s" Top="%s" Left="%s" State="%s">\n""" % (actionid, copy_object.id, copy_object.name, a.method_name, a.top, a.left, a.state)
					for p in a.parameters:
						xml_client_action += """<Parameter ScriptName="%s"><![CDATA[%s]]></Parameter>\n""" % (p.name, p.value)
					xml_client_action += "</Action>\n"
					action_map[a_id] = actionid
		xml_client_action += "</ClientActions>\n"
		try:
			client_actions_element = xml_object(srcdata=xml_client_action.encode("utf-8"))
			if not client_actions_element:
				raise VDOM_exception_element("ClientActions")
			# client actions
			for child in client_actions_element.children:
				if "action" == child.lname:
					_id = child.attributes["id"]
					tgt_id = child.attributes["objtgtid"]
					mn = child.attributes["methodname"]
					if not tgt_id or not mn or not _id:
						raise VDOM_exception_element("client action")
					for par in child.children:
						if "parameter" == par.lname:
							par_name = par.attributes["scriptname"]
							par_value = par.get_value_as_xml()
							if not par_name:
								raise VDOM_exception_element("Parameter")
		except Exception, e:
			if client_actions_element:
				client_actions_element.delete()
			raise SOAPpy.faultType(event_format_error, _("XML error"), str(e))
		if copy_object:
			appl.set_e2vdom_actions(copy_object, client_actions_element)
			if server_actions_element:
				for child in server_actions_element.children:
					if "action" == child.lname:
						if 1 != copy_object.type.container:
							copy_object.set_action_attributes(child)
				server_actions_element.delete()
		client_actions_element.delete()
		appl.sync()
		for ob in obj.get_objects_list():
			self.__copy_object(app, obj_id, ob.id, obj_map, action_map, newapp)
		return obj_id

	def __copy_events_structure(self, app, obj, new_obj, obj_map, action_map, tgt_app):
		if not tgt_app:
			tgt_app = app
		result = "<Events>\n"
		if obj and obj.toplevel.id in app.events:
			for src_id in app.events[obj.toplevel.id]:
				if src_id in obj_map:
					for ev_name in app.events[obj.toplevel.id][src_id]:
						result += """<Event ObjSrcID="%s" ObjSrcName="%s" TypeID="%s" ContainerID="%s" Name="%s" Top="%s" Left="%s" State="%s">\n""" % (obj_map[src_id], tgt_app.search_object(obj_map[src_id]).name, tgt_app.search_object(obj_map[src_id]).type.id, new_obj.toplevel.id, ev_name, app.events[obj.toplevel.id][src_id][ev_name].top, app.events[obj.toplevel.id][src_id][ev_name].left, app.events[obj.toplevel.id][src_id][ev_name].state)
						for a in app.events[obj.toplevel.id][src_id][ev_name].actions:
							if a in action_map:
								result += """<Action ID="%s"/>\n""" % action_map[a]
						result += "</Event>\n"
		result += "</Events>\n"
		events_element = None
		try:
			events_element = xml_object(srcdata=result.encode("utf-8"))
			if not events_element:
				raise VDOM_exception_element("Events")			
			for child in events_element.children:
				if "event" == child.lname:
					src_id = child.attributes["objsrcid"]
					name = child.attributes["name"]
					if not src_id or not name:
						raise VDOM_exception_element("Event")
					for act in child.children:
						if "action" == act.lname:
							_id = act.attributes["id"]
							if not _id:
								raise VDOM_exception_element("event.action")
		except Exception, e:
			if events_element:
				events_element.delete()
			raise SOAPpy.faultType(event_format_error, _("XML error"), str(e))

		tgt_app.set_e2vdom_events(new_obj, events_element)
		events_element.delete()

	def __set_attributes(self, obj, attr):
		"""set several attributes' value"""
		attr_map = self.__parse_attr(attr, False)
		obj.set_attributes(attr_map, False)

	def get_top_objects(self, sid, skey, appid):
		"""get application top-level objects"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, errmsg) = self.__find_application(appid)
		if not app:
			return errmsg
		return self.__get_objects(app)

	def get_top_object_list(self, sid, skey, appid):
		"""lightweight get application top-level objects"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, errmsg) = self.__find_application(appid)
		if not app:
			return errmsg
		return self.__get_object_list(app)

	def get_all_object_list(self, sid, skey, appid):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, errmsg) = self.__find_application(appid)
		if not app:
			return errmsg
		result = ''
		for o in app.get_objects_list():
			result += self.__get_all_object_list(o)
		return '<Objects>%s</Objects>' % result

	def get_child_objects(self, sid, skey, appid, objid):
		"""get object's child objects"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, obj, errmsg) = self.__find_object(appid, objid)
		if not app:
			return errmsg
		return self.__get_objects(obj)

	def get_child_objects_tree(self, sid, skey, appid, objid):
		"""get all object's child objects"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, obj, errmsg) = self.__find_object(appid, objid)
		if not app:
			return errmsg
		return self.__get_all_objects(obj) + ("\n<ApplicationID>%s</ApplicationID>" % appid)

	def get_one_object(self, sid, skey, appid, objid):
		"""get one object description"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, obj, errmsg) = self.__find_object(appid, objid)
		if not app:
			return errmsg
		if not managers.acl_manager.session_user_has_access2(appid, appid,security.access_to_application):
			raise SOAPpy.faultType(render_wysiwyg_error, "You have no access to this application", _("<Error/>"))						
		return "<Objects>\n" + self.__get_object(obj) + "</Objects>"

	def set_attribute(self, sid, skey, appid, objid, attr, value):
		"""set object attribute value"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, obj, errmsg) = self.__find_object(appid, objid)
		if not app:
			return errmsg
		# set object attribute value
		obj.set_attributes({attr: value}, False)
		app.sync()
		return self.__get_object(obj)

	def set_name(self, sid, skey, appid, objid, name):
		"""set object name"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, obj, errmsg) = self.__find_object(appid, objid)
		if not app:
			return errmsg
		# set object name
		try:
			obj.set_name(name)
		except VDOM_exception, e:
			raise SOAPpy.faultType(name_error, _("Rename error: ") + str(e), "<Error><ObjectID>%s</ObjectID><Name>%s</Name></Error>" % (obj.id, obj.original_name))
			#"<Object Name=\"%s\" ID=\"%s\" Type=\"%s\"/>" % (obj.original_name, obj.id, obj.type.id))
#			return self.__format_error(str(e)) + "\n<Object Name=\"%s\" ID=\"%s\" Type=\"%s\"/>\n"% (obj.name, obj.id, obj.type.id)
		app.sync()
		return "<Object Name=\"%s\" ID=\"%s\" Type=\"%s\"/>\n" % (obj.original_name, obj.id, obj.type.id)

	def set_attributes(self, sid, skey, appid, objid, attr):
		"""set several attributes' value"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, obj, errmsg) = self.__find_object(appid, objid)
		if not app:
			return errmsg
		try:
			self.__set_attributes(obj, attr)
		except Exception, e:
			raise SOAPpy.faultType(attr_value_error, str(e), "<Error><ObjectID>%s</ObjectID></Error>" % objid)
		app.sync()
		return self.__get_object(obj)

##### event ======================================================================================================
	def __do_get_events(self, app, obj):
		result = "<Events>\n"
		if obj and obj.id in app.events:
			for src_id in app.events[obj.id]:
#				if src_id in obj.objects or src_id == obj.id:
				#if src_id == obj.id:
				for ev_name in app.events[obj.id][src_id]:
					#result += """<Event ObjSrcID="%s" ObjSrcName="%s" TypeID="%s" ContainerID="%s" Name="%s" Top="%s" Left="%s" State="%s">\n""" % (src_id, app.search_object(src_id).name, obj.type.id, app.events[obj.id][src_id][ev_name].container, ev_name, app.events[obj.id][src_id][ev_name].top, app.events[obj.id][src_id][ev_name].left, app.events[obj.id][src_id][ev_name].state)
					result += """<Event ObjSrcID="%s" ObjSrcName="%s" TypeID="%s" ContainerID="%s" Name="%s" Top="%s" Left="%s" State="%s">\n""" % (src_id, app.search_object(src_id).name, app.search_object(src_id).type.id, app.events[obj.id][src_id][ev_name].container, ev_name, app.events[obj.id][src_id][ev_name].top, app.events[obj.id][src_id][ev_name].left, app.events[obj.id][src_id][ev_name].state)
					for a in app.events[obj.id][src_id][ev_name].actions:
						result += """<Action ID="%s"/>\n""" % a
					result += "</Event>\n"
		result += "</Events>\n"
		return result

	def __do_get_client_actions(self, app, obj):
		result = "<ClientActions>\n"	
		if obj:
			ll = obj.get_all_children()
			for a_id in app.actions:
				a = app.actions[a_id]
				if a.target_object in obj.objects or a.target_object == obj.id or a.target_object in ll:
					result += """<Action ID="%s" ObjTgtID="%s" ObjTgtName="%s" MethodName="%s" Top="%s" Left="%s" State="%s">\n""" % (a_id, a.target_object, app.search_object(a.target_object).name, a.method_name, a.top, a.left, a.state)
					for p in a.parameters:
						result += """<Parameter ScriptName="%s"><![CDATA[%s]]></Parameter>\n""" % (p.name, p.value)
					result += "</Action>\n"
		result += "</ClientActions>\n"
		return result

	def get_application_events(self, sid, skey, appid, objid):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, msg) = self.__find_application(appid)
		if not app:
			return msg
		if not managers.acl_manager.session_user_has_access2(appid, appid,security.access_to_application):
			raise SOAPpy.faultType(render_wysiwyg_error, "You have no access to events of this application", _("<Error/>"))				
		obj = app.search_object(objid)
		result =  self.__do_get_events(app, obj)
		result +=  self.__do_get_client_actions(app, obj)

		result += self.get_server_actions(sid, skey, appid, objid, check=False)
		return "<E2vdom>%s</E2vdom>" % result

	def get_events_structure(self, sid, skey, appid, objid):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, msg) = self.__find_application(appid)
		if not app:
			return msg

		obj = app.search_object(objid)
		result =  self.__do_get_events(app, obj)

		#result += "<ClientActions>\n"	
		#if obj:
		#	ll = obj.get_all_children()
		#	for a_id in app.actions:
		#		a = app.actions[a_id]
		#		if a.target_object in obj.objects or a.target_object == obj.id or a.target_object in ll:
		#			result += """<Action ID="%s" ObjectID="%s" Name="%s" Top="%s" Left="%s" State="%s">\n""" % (a_id, a.target_object, a.method_name, a.top, a.left, a.state)
		#			for p in a.parameters:
		#				result += """<Parameter ScriptName="%s"><![CDATA[%s]]></Parameter>\n""" % (p.name, p.value)
		#			result += "</Action>\n"
		#result += "</ClientActions>\n"

		result += self.__do_get_client_actions(app, obj)
		result += self.get_server_actions_list(sid, skey, appid, objid, check=False, full=True)
		return "<E2vdom>%s</E2vdom>" % result

	def set_events_structure(self, sid, skey, appid, objid, events ):	
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, msg) = self.__find_application(appid)
		if not app:
			return msg
		obj = app.search_object(objid)
		if obj and 1 == obj.type.container:
			raise VDOM_exception("Incorrect object")
		root = None
		client_actions_element = None
		server_actions_element = None
		events_element = None
		try:
			root = xml_object(srcdata=events.encode("utf-8"))
			if "e2vdom" != root.lname:
				raise VDOM_exception_element(root.lname)
			client_actions_element = root.get_child_by_name("clientactions")
			if not client_actions_element:
				raise VDOM_exception_element("ClientActions")
			server_actions_element = root.get_child_by_name("serveractions")
			if not server_actions_element:
				raise VDOM_exception_element("ServerActions")
			events_element = root.get_child_by_name("events")
			if not events_element:
				raise VDOM_exception_element("Events")
			# client actions
			for child in client_actions_element.children:
				if "action" == child.lname:
					_id = child.attributes["id"]
					tgt_id = child.attributes["ObjTgtID"]
					mn = child.attributes["methodname"]
					if not tgt_id or not mn or not _id:
						raise VDOM_exception_element("client action")
					for par in child.children:
						if "parameter" == par.lname:
							par_name = par.attributes["scriptname"]
							par_value = par.get_value_as_xml()
							if not par_name:
								raise VDOM_exception_element("Parameter")
			# server actions
			for child in server_actions_element.children:
				if "action" == child.lname:
					_id = child.attributes["id"]
					_name = child.attributes["name"]
					_object_id = child.attributes["ObjectID"]
					#_lang = child.attributes["language"]
					#if not _id or not _name or not _lang:
					if not _id or not _name or not _object_id:
						raise VDOM_exception_element("server action")
			# events
			for child in events_element.children:
				if "event" == child.lname:
					src_id = child.attributes["objsrcid"]
					name = child.attributes["name"]
					if not src_id or not name:
						raise VDOM_exception_element("Event")
					for act in child.children:
						if "action" == act.lname:
							_id = act.attributes["id"]
							if not _id:
								raise VDOM_exception_element("event.action")
		except Exception, e:
			if root:
				root.delete()
			raise SOAPpy.faultType(event_format_error, _("XML error"), str(e))
		server_actions_element.name = "Actions"
		if obj:
			app.set_e2vdom_events(obj, events_element)
			app.set_e2vdom_actions(obj, client_actions_element)
			#obj.set_actions(server_actions_element)
			for child in server_actions_element.children:
				if "action" == child.lname:
					action_object_id = child.attributes["ObjectID"]
					action_object = app.search_object(action_object_id)
					if action_object and 1 != action_object.type.container:
						action_object.set_action_attributes(child)

		#else:
		#	app.set_global_actions(server_actions_element)
		root.delete()
		app.sync()
		return self.__success()

	def __do_get_server_actions(self, obj ):
		if not len(obj.actions["name"]): return ""
		if 1 == obj.type.container: return ""
		result = '<Container ID="%s">\n' % obj.id
		for _name in obj.actions["name"]:
			x = obj.actions["name"][_name]
			result += """<Action ID="%s" Name="%s" Top="%s" Left="%s" State="%s">\n""" % (x.id, x.name, x.top, x.left, x.state)
			result += """<![CDATA[%s]]>\n""" % x.code.replace("]]>","]]]]><![CDATA[>")
			result += "</Action>\n"
		result += '</Container>\n'

		for x in obj.objects_list:
			result += self.__do_get_server_actions(x)
		return result


	def set_application_events(self, sid, skey, appid, objid, events):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, msg) = self.__find_application(appid)
		if not app:
			return msg
		obj = app.search_object(objid)
		if obj and 1 == obj.type.container:
			raise VDOM_exception("Incorrect object")
		root = None
		client_actions_element = None
		#server_actions_element = None
		events_element = None

		try:
			root = xml_object(srcdata=events.encode("utf-8"))
			if "e2vdom" != root.lname:
				raise VDOM_exception_element(root.lname)
			client_actions_element = root.get_child_by_name("clientactions")
			if not client_actions_element:
				raise VDOM_exception_element("ClientActions")
			#server_actions_element = root.get_child_by_name("serveractions")
			#if not server_actions_element:
			#	raise VDOM_exception_element("ServerActions")
			events_element = root.get_child_by_name("events")
			if not events_element:
				raise VDOM_exception_element("Events")
			# client actions
			for child in client_actions_element.children:
				if "action" == child.lname:
					_id = child.attributes["id"]
					tgt_id = child.attributes["objtgtid"]
					mn = child.attributes["methodname"]
					if not tgt_id or not mn or not _id:
						raise VDOM_exception_element("client action")
					for par in child.children:
						if "parameter" == par.lname:
							par_name = par.attributes["scriptname"]
							par_value = par.get_value_as_xml()
							if not par_name:
								raise VDOM_exception_element("Parameter")
			# server actions
			#for child in server_actions_element.children:
			#	if "action" == child.lname:
			#		_id = child.attributes["id"]
			#		_name = child.attributes["name"]
			#		_lang = child.attributes["language"]
			#		if not _id or not _name or not _lang:
			#			raise VDOM_exception_element("server action")
			# events
			for child in events_element.children:
				if "event" == child.lname:
					src_id = child.attributes["objsrcid"]
					name = child.attributes["name"]
					if not src_id or not name:
						raise VDOM_exception_element("Event")
					for act in child.children:
						if "action" == act.lname:
							_id = act.attributes["id"]
							if not _id:
								raise VDOM_exception_element("event.action")
		except Exception, e:
			if root:
				root.delete()
			raise SOAPpy.faultType(event_format_error, _("XML error"), str(e))
		#server_actions_element.name = "Actions"
		if obj:
			app.set_e2vdom_events(obj, events_element)
			app.set_e2vdom_actions(obj, client_actions_element)
		#	obj.set_actions(server_actions_element)
		#else:
		#	app.set_global_actions(server_actions_element)
		root.delete()
		app.sync()
		return self.__success()

	def set_server_actions(self, sid, skey, appid, objid, actions):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, msg) = self.__find_application(appid)
		if not app:
			return msg
		obj = app.search_object(objid)
		if obj and 1 == obj.type.container:
			raise VDOM_exception("Incorrect object")
		root = None
		try:
			root = xml_object(srcdata=actions.encode("utf-8"))
			if "serveractions" != root.lname:
				raise VDOM_exception_element(root.lname)
			for child in root.children:
				if "action" == child.lname:
					_id = child.attributes["id"]
					_name = child.attributes["name"]
					if not _id or not _name:
						raise VDOM_exception_element("server action")
		except Exception, e:
			if root:
				root.delete()
			raise SOAPpy.faultType(event_format_error, _("XML error"), str(e))
		root.name = "Actions"
		if obj:
			obj.set_actions(root)
		else:
			app.set_global_actions(root)
		root.delete()
		app.sync()
		return self.__success()

	def get_server_actions(self, sid, skey, appid, objid, check=True):
		if check:
			if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, msg) = self.__find_application(appid)
		if not app:
			return msg
		if not managers.acl_manager.session_user_has_access2(appid, appid,security.access_to_application):
			raise SOAPpy.faultType(render_wysiwyg_error, "You have no access to actions of this application", _("<Error/>"))		
		
		obj = app.search_object(objid)
		result = "<ServerActions>\n"
		if obj:
			result += self.__do_get_server_actions(obj)
		elif objid in app.global_actions:
			result += "<Container ID=\"%s\">\n"%objid
			for _name in app.global_actions[objid]:
				x = app.global_actions[objid][_name]
				result += """<Action ID="%s" Name="%s" Top="%s" Left="%s" State="%s">\n<![CDATA[%s]]>\n</Action>\n"""%( \
				        x.id, x.name, x.top, x.left, x.state,x.code.replace("]]>","]]]]><![CDATA[>"))
			result += "</Container>\n"
		result += "</ServerActions>\n"
		return result

	def __do_get_server_actions_list(self, obj, full ):
		if not len(obj.actions["name"]): return ""
		if 1 == obj.type.container: return ""
		result = "" # '<Container ID="%s">\n' % obj.id
		for _name in obj.actions["name"]:
			x = obj.actions["name"][_name]

			additional = ""	
			if full:
				additional = """  Top="%s" Left="%s" State="%s"  """%( x.top, x.left, x.state)

			result += """<Action ID="%s" Name="%s" ObjectID="%s"  ObjectName="%s" %s />\n""" % (x.id, x.name, obj.id, obj.name , additional)

		if full:
			for x in obj.objects_list:
				result += self.__do_get_server_actions_list(x, full)
		return result	

	def get_server_actions_list(self, sid, skey, appid, objid, check=True, full=False ):
		if check:
			if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, msg) = self.__find_application(appid)
		if not app:
			return msg
		if not managers.acl_manager.session_user_has_access2(appid, appid,security.access_to_application):
			raise SOAPpy.faultType(render_wysiwyg_error, "You have no access to actions of this application", _("<Error/>"))		
		obj = app.search_object(objid)
		result = "<ServerActions>\n"
		if obj:
			result += self.__do_get_server_actions_list(obj,  full )
		elif objid in app.global_actions:
			for _name in app.global_actions[objid]:
				x = app.global_actions[objid][_name]
				additional = ""	
				if full:
					additional = """  Top="%s" Left="%s" State="%s"  """%( x.top, x.left, x.state)
				result += """<Action ID="%s" Name="%s" ObjectID="%s" ObjectName="%s" %s />\n""" % (x.id, x.name, obj.id ,  obj.name, additional)
		result += "</ServerActions>\n"
		return result

	# addition to server actions API

	def create_server_action(self, sid, skey, appid, objid, actionname, actionvalue):
		"""create server action"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, obj, errmsg) = self.__find_object(appid, objid)
		if not obj:
			return errmsg
		else:
			actionid = obj.create_action(actionname, actionvalue)
			app.sync()
			return '<Action ID="%s" Name="%s" ObjectID="%s"/>' % (actionid, actionname, objid)

	def delete_server_action(self, sid, skey, appid, objid, actionid):
		"""remove server action"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, obj, errmsg) = self.__find_object(appid, objid)
		if not obj:
			return errmsg
		else:
			obj.delete_action(actionid)
			app.sync()
			return self.__success()

	def rename_server_action(self, sid, skey, appid, objid, actionid, new_actionname):
		"""rename server action"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, obj, errmsg) = self.__find_object(appid, objid)
		if not obj:
			return errmsg
		else:
			obj.rename_action(actionid, new_actionname)
			app.sync()
			return '<Action ID="%s" Name="%s" ObjectID="%s"/>' % (actionid, new_actionname, objid)

	def get_server_action(self, sid, skey, appid, objid, actionid):
		"""get server action"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, msg) = self.__find_application(appid)
		if not app:
			return msg
		if not managers.acl_manager.session_user_has_access2(appid, appid,security.access_to_application):
			raise SOAPpy.faultType(render_wysiwyg_error, "You have no access to actions of this application", _("<Error/>"))		
		
		obj = app.search_object(objid)
		if obj:
			if actionid not in obj.actions["id"]:
				raise SOAPpy.faultType(object_id_error, _("No such server action"), _("<Error><ActionID>%s</ActionID></Error>") % actionid)
			else:
				action = obj.actions["id"][actionid]
				return """<Action ID="%s" Name="%s" ObjectID="%s" Top="%s" Left="%s" State="%s">\n<![CDATA[%s]]>\n</Action>\n"""%( \
				        action.id, action.name, objid, action.top, action.left, action.state, action.code.replace("]]>","]]]]><![CDATA[>"))
		elif objid in app.global_actions:
			if actionid not in app.global_actions[objid]:
				raise SOAPpy.faultType(object_id_error, _("No such server action"), _("<Error><ActionID>%s</ActionID></Error>") % actionid)
			else:
				action = app.global_actions[objid][actionid]
				return """<Action ID="%s" Name="%s" ObjectID="%s" Top="%s" Left="%s" State="%s">\n<![CDATA[%s]]>\n</Action>\n"""%( \
				        action.id, action.name, objid, action.top, action.left, action.state, action.code.replace("]]>","]]]]><![CDATA[>"))
		else:
			raise SOAPpy.faultType(object_id_error, "Object not found", _("<Error><ObjectID>%s</ObjectID></Error>") % objid)

	def set_server_action(self, sid, skey, appid, objid, actionid, actionvalue):
		"""set server action"""
		
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, msg) = self.__find_application(appid)
		if not app:
			return msg
		actionvalue = actionvalue.replace("]]]]><![CDATA[>","]]>") #to escape inside CDATA
		obj = app.search_object(objid)
		if obj:
			obj.set_action(actionid, actionvalue)
			app.sync()
			return self.__success()
		elif objid in app.global_actions and actionid in app.global_actions[objid]:
			app.set_global_action(objid,actionid,actionvalue)
			app.sync()
			return self.__success()
		else:
			raise SOAPpy.faultType(object_id_error, "Object not found", _("<Error><ObjectID>%s</ObjectID></Error>") % objid)


##### ----- ========================================================================================================

	def modify_resource(self, sid, skey, appid, objid, resid, attrname, operation, attr):
		"""modify resource"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_object(appid, objid)	# returns (app, obj, error_message)
		if not ret[0]:
			return ret[2]
		param = self.__parse_attr(attr, False)
		(success, _data) = managers.resource_editor.modify_resource(sid, appid, objid, resid, attrname, operation, param)
		if not success:
			raise SOAPpy.faultType(res_mod_error, _data, _data)
#			return self.__format_error(_data)
		return self.__get_object(ret[1])

	def get_thumbnail(self, sid, skey, appid, resid, width, height):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		ro = managers.resource_manager.get_resource(appid, resid)
		if not ro:
			raise SOAPpy.faultType(resource_not_found_error, _("Thumbnail error"), _("Resource not found"))
#			return self.__format_error(_("Resource not found"))
		_data = managers.resource_editor.do_thumbnail(ro.res_format, ro.get_data(), int(width), int(height))
		return "<Resource><![CDATA[%s]]></Resource>" % utils.encode.encode_resource(_data)

	def execute_sql(self, sid, skey, appid, dbid, sql, script):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		if not managers.acl_manager.session_user_has_access2(appid, appid, security.modify_application):
			raise VDOM_exception(_("SQL execution is not allowed"))
		_script = False
		if "True" == script:
			_script = True
		query = VDOM_sql_query(appid, dbid, sql, None, _script)
		last_id = query.lastrowid
		query.commit()
		result = query.fetchall_xml()
		if last_id:
			result += "\n<LastRowID>%s</LastRowID>"%last_id
		return result

	def remote_method_call(self, sid, skey, appid, objid, func_name, xml_param, session_id):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_object(appid, objid)	# returns (app, obj, error_message)
		if not ret[0]:
			return ret[2]
		if session_id == "":
			if not managers.acl_manager.session_user_has_access2(appid, appid, security.modify_application):
				raise SOAPpy.faultType(remote_method_call_error, _("Remote method call is not allowed"), _(""))
		else:
			try:
				sess = managers.session_manager.get_session(session_id)
				policy = sess.value(objid)
				if policy is None:
					raise AttributeError
				if "rmc_allow" not in policy:
					raise AttributeError
				if func_name not in policy["rmc_allow"]:
					raise AttributeError
			except:
				raise SOAPpy.faultType(remote_method_call_error, _("Remote method call is not allowed"), _(""))
		ret = managers.dispatcher.dispatch_remote(appid, objid, func_name, xml_param,session_id)
		return ret

	def remote_call(self, sid, skey, appid, objid, func_name, xml_param, xml_data):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		p = self.__parse_attr(xml_param, namefromtag = True, lowercase = False)
		# p = dict with arguments
		if "CallType" not in p:
			raise SOAPpy.faultType(remote_method_call_error, _("Remote call type is not defined"), _(""))
		rctype = p["CallType"]
		if rctype == "rmc":
			if not managers.acl_manager.session_user_has_access2(appid, appid, security.access_to_application):
				raise SOAPpy.faultType(remote_method_call_error, _("Remote method call is not allowed"), _(""))
			ret = managers.dispatcher.dispatch_remote(appid, objid, func_name, xml_data)
		elif rctype == "rmc_over_session" and "HTTPSessionID" in p:
			sess = managers.session_manager.get_session(p["HTTPSessionID"])
			policy = sess.value(objid)
			if policy and  "rmc_allow" in policy and func_name in policy["rmc_allow"]:
				ret = managers.dispatcher.dispatch_remote(appid, objid, func_name, xml_data,p["HTTPSessionID"])
			else:
				raise SOAPpy.faultType(remote_method_call_error, _("Remote call is not allowed"), _(""))
		elif rctype == "server_action":
			if not managers.acl_manager.session_user_has_access2(appid, objid, security.modify_object):
				raise SOAPpy.faultType(remote_method_call_error, _("Remote call is not allowed"), _(""))			
			ret = managers.dispatcher.dispatch_action(appid, objid, func_name, xml_param,xml_data)
		else:
			raise SOAPpy.faultType(remote_method_call_error, _("Remote call type is not alowed"), _(""))
		return ret
##### management ========================================================================================================

	def install_application(self, sid, skey, vhname, appxml):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		request = managers.request_manager.get_request()
		vh = request.server().virtual_hosting()
		if "" != vhname and vh.get_site(vhname):
			raise SOAPpy.faultType(duplicate_vhname_error, _("Install application error"), _("Virtual host name exists"))
#			return self.__format_error(_("Virtual host name \"%s\" already exists" % vhname))
		# save file
		tmpfilename = tempfile.mkstemp(".xml", "", VDOM_CONFIG["TEMP-DIRECTORY"])
		os.close(tmpfilename[0])
		tmpfilename = tmpfilename[1]
		tmpfile = open(tmpfilename, "wb")
		tmpfile.write(appxml.encode("utf-8"))
		tmpfile.close()
		# install
		outp, msg = import_application(tmpfilename,"xml")
		try:
			os.remove(tmpfilename)
		except Exception, e:
			pass
		if "" != outp and None != outp:
			if "" != vhname:
				vh.set_site(vhname, outp)	# outp contains the application ID
			return "<ApplicationID>%s</ApplicationID>" % outp
		elif "" == outp:
			return self.__format_error(_("Install application error."), _("Application already installed"))
			#raise SOAPpy.faultType(app_installed_error, _("Install application error"), _("Application already installed"))
		else:
			return self.__format_error(_("Install application error."), msg)
			#raise SOAPpy.faultType(app_install_error, _("Install application error"), msg)


	def uninstall_application(self, sid, skey, appid):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		outp, msg = uninstall_application(appid)
		# remove vhosts
		vh = managers.virtual_hosts
		for s in vh.get_sites():
			if vh.get_site(s) == appid:
				vh.set_site(s, None)
		if "" != outp and None != outp:
			return "<Result>OK</Result>";
		else:
			return self.__format_error(_("Uninstall application error"),msg)
			#raise SOAPpy.faultType(app_uninstall_error, _("Uninstall application error"), msg)

	def export_application(self, sid, skey, appid):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = self.__find_application(appid)	# returns (app, error_message)
		if not ret[0]:
			return ret[1]
		if ret[0].protected == "1":
			return "<Error>This application could not be exported</Error>"
		
		path = tempfile.mkdtemp("", "", VDOM_CONFIG["TEMP-DIRECTORY"])
		
		managers.xml_manager.export_application(appid, "xml", path)
		toread = os.path.join(path, appid) + ".xml"
		f = open(toread, "rb")
		data = f.read()
		f.close()

		try: shutil.rmtree(path)
		except: pass
		return data.decode("utf-8")


	def update_application(self, sid, skey, appxml):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		tmpfilename = ""
		try:
			# save file
			tmpfilename = tempfile.mkstemp(".xml", "", VDOM_CONFIG["TEMP-DIRECTORY"])
			os.close(tmpfilename[0])
			tmpfilename = tmpfilename[1]
			tmpfile = open(tmpfilename, "wb")
			tmpfile.write(appxml.encode("utf-8"))
			tmpfile.close()
			# call update function
			outp = update_application(tmpfilename, managers.virtual_hosts)
			if outp[0]:
				return """<Result>OK</Result>"""
			else:
				return self.__format_error(_("Update error: %s" % outp[1]))
		except Exception as e:
			return self.__format_error(_("Update error: %s" % str(e)))

	def check_application_exists(self, sid, skey, appid):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		result = ""
		try:
			ret = self.__find_application(appid)	# returns (app, error_message)
			if ret[0]:
				result = "true"
		except:
			result = "false"
		return """<Result>\n <ApplicationExists>\n  %s\n </ApplicationExists>\n</Result>""" % result


	def backup_application(self, sid, skey, appid, driverid):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		backupid = skey
		result = managers.backup_manager.backup(appid, driverid, 30, backupid)
		if result[0] != 0:
			raise SOAPpy.faultType(application_backup_error, _("Backup error"), _("Application was not backuped"))

		return """<Result> <Revision>%s</Revision></Result>"""%str(result[1])


	def get_task_status(self, sid, skey, taskid):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		status = managers.task_manager.get_status(taskid)
		if status:
			result = """<Result>\n <Progress>%s</Progress>\n <Message>\n  %s\n </Message>\n</Result>"""%(status.progress, status.message)
			return result				
		else:
			return self.__format_error(_("Proccess with tid %s does not exists" % taskid))
		
	def restore_application(self,sid, skey, appid, driverid, revision):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		taskid = skey
		result = managers.backup_manager.restore(driverid, appid, revision, taskid)
		if not result[0]:
			raise SOAPpy.faultType(application_restore_error, _("Restore error"), _("Application was not restored"))
		return """<Result><Revision>%s</Revision></Result>"""%str(revision)


	def list_backup_drivers(self, sid, skey):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		backup_drivers = managers.backup_manager.get_storages()
		ret = ""
		for driver in backup_drivers:
			driver_obj = backup_drivers[driver]
			ret +="""\n\t<Driver>\n\t\t<ID>%(id)s</ID>\n\t\t<Name>%(name)s</Name>\n\t\t<Description>%(type)s</Description>\n\t</Driver>\n"""%{"id":driver_obj.id, "name":driver_obj.name, "type":driver_obj.type}

		return "<Result>%s</Result>"%ret


	def set_vcard_license(self, sid, skey, serial, reboot):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		if not managers.acl_manager.session_user_can_manage():
			raise SOAPpy.faultType(server_manage_error, _("Server management is not allowed"), _(""))		
		
		from utils.system import set_virtual_card_key		
		ret = set_virtual_card_key(serial)

		if reboot and str(reboot).lower()=="true":
			import os
			f = os.popen("reboot")
			outp = f.read()
			f.close()
		return "<Result>%s</Result>"%ret
	
	def set_application_vhost(self, sid, skey, appid, hostname):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		if not managers.acl_manager.session_user_can_manage():
			raise SOAPpy.faultType(server_manage_error, _("Server management is not allowed"), _(""))				
		if not hostname or hostname.lower() == "default" or hostname == 0:
			managers.virtual_hosts.set_def_site(appid)
		else:
			managers.virtual_hosts.set_site(hostname, appid)
		return "<Result>OK</Result>"
	
	def delete_application_vhost(self,sid, skey, hostname):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		if not managers.acl_manager.session_user_can_manage():
			raise SOAPpy.faultType(server_manage_error, _("Server management is not allowed"), _(""))				
		if not hostname or hostname.lower() == "default" or hostname == 0:
			managers.virtual_hosts.set_def_site(None)
		else:
			managers.virtual_hosts.set_site(hostname, None)
		return "<Result>OK</Result>"
	
### ==================================================================================================================

	def create_guid(self, sid, skey):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		return "<GUID>%s</GUID>" % str(uuid4())

	def search(self, sid, skey, appid, pattern):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		appidlst = None
		if "" != appid:
			ret = self.__find_application(appid)	# returns (app, error_message)
			if not ret[0]:
				return ret[1]
			appidlst = [appid]
		else:
			appidlst = managers.xml_manager.get_applications()
		s = "<SearchResult>\n"
		for _id in appidlst:
			_app = managers.xml_manager.get_application(_id)
			r = _app.search(pattern)
			if 0 == len(r):
				continue
			s += """<Application ID="%s" Name="%s">\n""" % (_app.id, _app.name)
			for top_id in r:
				o1 = _app.search_object(top_id)
				s += '<Container ID="%s" Type="%s" Name="%s">\n' % (o1.id, o1.type.id, o1.name)
				for l in r[top_id]:
					o2 = _app.search_object(l)
					s += '<Object ID="%s" Type="%s" Name="%s"/>\n' % (o2.id, o2.type.id, o2.name)
				s += '</Container>\n'
			s += "</Application>\n"
		return s + "</SearchResult>"

	def keep_alive(self, sid, skey):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		return self.__success()

	def __do_create_objects(self, app, parent, xml_obj):
		for child in xml_obj.children:
			if "object" == child.lname:
				_name = child.attributes["name"]
				_type = child.attributes["type"].lower()
				_type_obj = managers.xml_manager.get_type(_type)
				_attr_map = {}
				_attr_elem = child.get_child_by_name("attributes")
				if _attr_elem:
					# load object attributes
					for _a in _attr_elem.children:
						if "attribute" == _a.lname:
							_attr_map[_a.attributes["name"]] = _a.get_value_as_xml()
				# create object
				(_new_name, _new_id) = app.create_object(_type_obj.id, parent, False)
				_new_obj = app.search_object(_new_id)
				# set name
				if _name:
					try:
						_new_obj.set_name(_name)
					except VDOM_exception, e:
						debug(unicode(e))
				# set attributes
				for aname in _attr_map:
					_new_obj.set_attribute(aname, _attr_map[aname], False)
				# process child objects
				_obj_elem = child.get_child_by_name("objects")
				if _obj_elem:
					self.__do_create_objects(app, _new_obj, _obj_elem)

	def create_objects(self, sid, skey, appid, parentid, objects):
		"""create multiple objects"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, errmsg) = self.__find_application(appid)
		if not app:
			return errmsg
		if objects.strip() is "":
			raise SOAPpy.faultType(param_syntax_error, _("Empty data"), "objects")
		parent = None
		if parentid is not "":
			parent = app.search_object(parentid)
			if parent is None:
				raise SOAPpy.faultType(parent_object_error, "", "")
		# parse xml
		root = None
		try:
			root = xml_object(srcdata=objects.encode("utf-8"))
		except Exception, e:
			raise SOAPpy.faultType(param_syntax_error, str(e), "objects")
		# start
		try:
			self.__do_create_objects(app, parent, root)
		except Exception, e:
			root.delete()
			app.sync()
			raise SOAPpy.faultType(obj_create_error, str(e), "")
		root.delete()
		app.sync()
		if parent:
			return self.__get_objects(parent)
		else:
			return self.__get_objects(app)
			#return self.__success()

	def __do_update_object(self, app, parent, xml_obj, objects_xml_obj):
		_name = xml_obj.attributes["name"]
		if _name:
			try:
				parent.set_name(_name)
			except VDOM_exception, e:
				raise SOAPpy.faultType(name_error, _("Name error"), "<Error><ObjectID>%s</ObjectID><Name>%s</Name></Error>" % (parent.id, _name))
		_attr_elem = xml_obj.get_child_by_name["attributes"]
		if _attr_elem:
			# set object attributes
			for _a in _attr_elem.children:
				if "attribute" == _a.lname:
					_a_name = _a.attributes["name"]
					if _a_name:
						parent.set_attribute(_a_name, _a.get_value_as_xml(), False)
		_current = copy.deepcopy(parent.objects.keys())		# child objects' IDs
		if objects_xml_obj:
			for child in objects_xml_obj.children:
				if "object" == child.lname:
					_type = child.attributes["type"].lower()
					_id = child.attributes["id"].lower()
					if not _type and not _id:
						raise SOAPpy.faultType(attr_value_error, _("Invalid Type or ID"), "")
					_obj_node = child.get_child_by_name("objects")
					if _id:
						if _id in _current:
							_obj = parent.objects[_id]
							if _type and _type != _obj.type.id:
								raise SOAPpy.faultType(attr_value_error, _("Invalid Type"), _type)
							self.__do_update_object(app, _obj, child, _obj_node)
							_current.remove(_id)
						else:
							raise SOAPpy.faultType(attr_value_error, _("Unknown ID"), "")
					elif _type:
						_type_obj = managers.xml_manager.get_type(_type)
						# create new object
						(_new_name, _new_id) = app.create_object(_type_obj.id, parent, False)
						_new_obj = app.search_object(_new_id)
						self.__do_update_object(app, _new_obj, child, _obj_node)
		# remove objects left in _current
		for _i in _current:
			app.delete_object(app.search_object(_i))

	def update_object(self, sid, skey, appid, objid, data):
		"""update object"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, obj, errmsg) = self.__find_object(appid, objid)
		if not obj:
			return errmsg
		if data.strip() is "":
			raise SOAPpy.faultType(param_syntax_error, _("Empty data"), "data")
		# parse xml
		root = None
		try:
			root = xml_object(srcdata=data.encode("utf-8"))
		except Exception, e:
			raise SOAPpy.faultType(param_syntax_error, str(e), "data")
		if obj.id != root.attributes["id"]:
			root.delete()
			raise SOAPpy.faultType(invalid_object_error, _("Invalid object"), objid)
		_obj_elem = root.get_child_by_name("objects")
		if _obj_elem:
			try:
				self.__do_update_object(app, obj, root, _obj_elem)
			except Exception, e:
				root.delete()
				app.sync()
				raise SOAPpy.faultType(obj_update_error, str(e), "")
		root.delete()
		app.sync()
		return self.__get_all_objects(obj)

	def set_lib(self, sid, skey, appid, libname, data):
		"""create/update library"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, errmsg) = self.__find_application(appid)
		if not app:
			return errmsg
		app.set_library(libname, data.replace("]]]]><![CDATA[>","]]>"))
		app.sync()
		return '<Library Name="%s"/>' % libname


	def del_lib(self, sid, skey, appid, libname):
		"""remove library"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, errmsg) = self.__find_application(appid)
		if not app:
			return errmsg
		app.remove_library(libname)
		app.sync()
		return '<Library Name="%s"/>' % libname

	def get_lib(self, sid, skey, appid, libname):
		"""get library"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, errmsg) = self.__find_application(appid)
		if not app:
			return errmsg
		if not managers.acl_manager.session_user_has_access2(appid, appid,security.access_to_application):
			raise SOAPpy.faultType(render_wysiwyg_error, "You have no access to libraries of this application", _("<Error/>"))		
		
		return app.get_library(libname)

	def get_libs(self, sid, skey, appid):
		"""get libraries"""
		if not self.__check_session(sid, skey): return self.__session_key_error()
		(app, errmsg) = self.__find_application(appid)
		if not app:
			return errmsg
		if not managers.acl_manager.session_user_has_access2(appid, appid,security.access_to_application):
			raise SOAPpy.faultType(render_wysiwyg_error, "You have no access to libraries of this application", _("<Error/>"))		
		
		return app.libraries_element.toxml(encode = False)

	def server_information(self, sid, skey):
		if not self.__check_session(sid, skey): return self.__session_key_error()
		ret = "<Information>\n"
		ret += "<ServerVersion>%s</ServerVersion>\n" % VDOM_server_version
		ret += "</Information>\n"
		return ret