"""XML Manager module"""

import shutil, os, os.path, sys, traceback, base64, zipfile, thread, time, copy
from metaimporter import VDOM_metaimporter
from utils.threads import VDOM_daemon


class VDOM_xml_sync_daemon(VDOM_daemon):
	
	def __init__(self, name="XML Sync", sleep=VDOM_CONFIG["APP-SAVE-TIMEOUT"]):
		VDOM_daemon.__init__(self, name=name, sleep=sleep)

	def prepare(self):
		debug("Start %s"%self.name)

	def cleanup(self):
		debug("Stop %s"%self.name)

	def work(self):
		managers.xml_manager.sync()
    
class VDOM_xml_manager(object):
	"""XML Manager class"""

	def __init__(self):
		"""constructor"""
		# properties
		self.__applications = {}	# map application id to application object
		self.__types = {}		# map type id to type object
		self.__type_by_name = {}	# map type name to type object
		self.__app_id_list = []
		self.__type_id_list = []
		self.__app_to_sync = []
		self.obj_count = 0

		sys.meta_path.append(VDOM_metaimporter())

		managers.resource_manager.save_index_off()
		managers.resource_manager.restore()
		managers.database_manager.restore()

		# sync semaphores
		self.__sem = VDOM_semaphore()
		self.__app_sem = VDOM_semaphore()

		# clear resources and source code
		id_list = managers.storage.read_object(VDOM_CONFIG["XML-MANAGER-APP-STORAGE-RECORD"])
		if id_list:
			for ii in id_list:
				managers.source_cache.clear_container_swap(ii)

		type_list = managers.storage.read_object(VDOM_CONFIG["XML-MANAGER-TYPE-STORAGE-RECORD"])
		if type_list:
			for tt in type_list:
				managers.source_cache.clear_type_sources(tt)

		# list files in type directory and load types from files
		ret = VDOM_type_enumerator().get()
		for fname in ret:
			try:
				(result, type_object) = self.load_type(fname)
				if result:
					sys.stderr.write(_("Loaded type \'") + str(type_object.id) + "\' name \'" + str(type_object.name) + "\'\n")
				else:
					sys.stderr.write(_("  Type \'") + str(type_object.name) + "\' ignored due to duplicate ID (owned by %s)\n" % self.__types[type_object.id].name)
			except Exception, e:
				sys.stderr.write(_("Error loading type \'") + str(fname) + "\': " + str(e) + "\n")
				traceback.print_exc(file=debugfile)
		# wait_for_options()
		# list files in app directory and load applications from files
		ret = VDOM_application_enumerator().get()
		for fname in ret:
			try:
				(result, app_object) = self.load_application(fname, boot = True)
				sys.stderr.write(_("Loaded application \'") + str(app_object.id) + "\'\n")
			except VDOM_exception_missing_type, t:
				sys.stderr.write(_("Error loading application \'") + str(fname) + "\': Missing type " + str(t) + "\n")
			except VDOM_exception_lic, s:
				sys.stderr.write(_("Error loading application \'") + str(fname) + "\': " + str(s) + "\n")
			except Exception, e:
				sys.stderr.write(_("Error loading application \'") + str(fname) + "\': " + str(e) + "\n")
				traceback.print_exc(file=debugfile)
				if VDOM_CONFIG["AUTO-REMOVE-INCORRECT-APPLICATIONS"]:
					shutil.rmtree(os.path.split(fname)[0], True)

		self.__sync_type()
		self.__sync_app()

		# remove unused resources
		managers.resource_manager.collect_unused()
		managers.resource_manager.save_index_on(True)

		#thread.start_new_thread(self.__app_sync_thread, ())

	def __app_sync_thread(self):
		while True:
			if len(self.__app_to_sync) > 0:
				self.__app_sem.lock()
				while len(self.__app_to_sync) > 0:
					the_id = self.__app_to_sync.pop(0)
					try:
						while True:
							self.__app_to_sync.remove(the_id)
					except: pass
					if the_id in self.__applications:
						xmlstr = self.__applications[the_id].get_xml_as_string()
						if len(xmlstr) > 0:
							try:
								managers.file_manager.write(file_access.application_xml, the_id, None, None, xmlstr, False, False)
							except Exception, e:
								debug("\nApplication '%s' save error: %s\n" % (the_id, str(e)))
				self.__app_sem.unlock()
			time.sleep(VDOM_CONFIG["APP-SAVE-TIMEOUT"])

	def sync(self):
		if len(self.__app_to_sync) > 0:
			self.__app_sem.lock()
			while len(self.__app_to_sync) > 0:
				the_id = self.__app_to_sync.pop(0)
				try:
					while True:
						self.__app_to_sync.remove(the_id)
				except: pass
				if the_id in self.__applications:
					xmlstr = self.__applications[the_id].get_xml_as_string()
					if len(xmlstr) > 0:
						try:
							managers.file_manager.write(file_access.application_xml, the_id, None, None, xmlstr, False, False)
						except Exception, e:
							debug("\nApplication '%s' save error: %s\n" % (the_id, str(e)))
			self.__app_sem.unlock()
		
	### app

	def load_application(self, filename, boot = False):
		"""load application object from external xml file, Return: (if app exists, app object)"""
		doc = xml_object(filename)
		e = None
		obj = VDOM_application(self)
		try:
			obj.create(doc)
		except Exception ,x:
			e = x
		if e and not boot:
			try:
				self.uninstall_abnormal(obj)
			except:
				traceback.print_exc(file=debugfile)
		if e:
			raise e
		else:
			if obj.id not in self.__applications:
				# store application object in the map
				self.__sem.lock()
				try:
					self.__applications[obj.id] = obj
					try:
						self.__app_id_list.index(obj.id)
					except ValueError:
						self.__app_id_list.append(obj.id)
				finally:
					self.__sem.unlock()
				return (True, obj)
			return (False, obj)

	### type

	def load_type(self, fname):
		"""load type object from external xml file, Return: (if type exists, type object)"""
		doc = xml_object(fname)
		obj = VDOM_type()
		obj.filename = fname
		obj.create(doc)
		if obj.id not in self.__types:
			# store type object in the map
			self.__sem.lock()
			try:
				self.__types[obj.id] = obj
				self.__type_by_name[obj.name.lower()] = obj
				try:
					self.__type_id_list.index(obj.id)
				except ValueError:
					self.__type_id_list.append(obj.id)
			finally:
				self.__sem.unlock()
			return (True, obj)
		return (False, obj)

	def unload_type(self, _id):
		self.__sem.lock()
		try:
			if _id in self.__types:
				del self.__types[_id]
		finally:
			self.__sem.unlock()

	def test_type(self, fname):
		doc = None
		try:
			doc = xml_object(fname)
		except Exception, e:
			sys.stderr.write(_("Error checking type: ") + str(e) + "\n")
			traceback.print_exc(file=debugfile)
			raise VDOM_exception_parse(_("XML parse error"))
		obj = VDOM_type()
		obj.create(doc)
		if obj.id not in self.__types:
			return None # don't have it
		return obj.id

	def __sync_app(self):
		"""save application data"""
		managers.storage.write_object(VDOM_CONFIG["XML-MANAGER-APP-STORAGE-RECORD"], self.__app_id_list)

	def __sync_type(self):
		"""save type data"""
		managers.storage.write_object(VDOM_CONFIG["XML-MANAGER-TYPE-STORAGE-RECORD"], self.__type_id_list)

	def app_sync(self, app_id):
		if app_id not in self.__app_to_sync:
			self.__app_sem.lock()
			self.__app_to_sync.append(app_id)
			self.__app_sem.unlock()

### public ###########################################################################################
	def get_application(self, appid):
		"""get application object by id"""
		if appid in self.__applications:
			return self.__applications[appid]
		raise VDOM_exception_missing_app(str(appid))

	def get_type(self, typeid):
		"""get type object by id"""
		if typeid in self.__types:
			return self.__types[typeid]
		raise VDOM_exception_missing_type(str(typeid))

	def get_type_by_name(self, name):
		"""get type object by its name"""
		if name.lower() in self.__type_by_name:
			return self.__type_by_name[name.lower()]
		return None
		#raise VDOM_exception_missing_type(str(name))

	def remove_type(self, typeid):
		"""remove type"""
		if typeid in self.__types:
			self.__sem.lock()
			try:
				self.__type_id_list.remove(typeid)
				obj = self.__types[typeid]
				del self.__type_by_name[obj.name.lower()]
				del obj
				del self.__types[typeid]
				managers.file_manager.delete(file_access.global_type, None, None, typeid + ".xml")
				self.__sync_type()
			finally:
				self.__sem.unlock()

	def get_applications(self):
		"""get applications"""
		return self.__applications.keys()

	def get_types(self):
		"""get types"""
		return self.__types.keys()

	def create_application(self):
		"""create new application and return its id"""
		# check user rights
		if not managers.acl_manager.session_user_has_access("vdombox", security.create_application):
			raise VDOM_exception_sec(_("Creating application is not allowed"))
		newapp = VDOM_application(self)
		newapp.create()
		managers.file_manager.create_application_skell(newapp.id)
		newapp.sync()
		self.__sem.lock()
		try:
			# store application object in the map
			self.__applications[newapp.id] = newapp
			self.__app_id_list.append(newapp.id)
			self.__sync_app()
		finally:
			self.__sem.unlock()
		# grant access to this application
		managers.acl_manager.grant_access_to_application(newapp.id)
		return newapp.id

	def search_object(self, id_app, id_obj):
		"""find object"""
		try:
			app = self.__applications[id_app]
			return app.search_object(id_obj)
		except:
			return None

############################## external application management #########################################################

	def import_application(self, path):
		"""import application from a temporary path or single xml file"""
		if not managers.acl_manager.session_user_has_access("vdombox", security.create_application):
			raise VDOM_exception_sec(_("Installing application is not allowed"))
		p = parseapp()
		result = None
		try:
			p.run(path)
			debug(p.work_xml_file)
			if p.id in self.__applications:
				return ("", "")
			(result, app_object) = self.load_application(p.work_xml_file)
			if app_object.server_version != "" and VDOM_server_version < app_object.server_version:
				return (None, "Server version (%s) is unsuitable for this application (%s)" % (VDOM_server_version, app_object.server_version))
			debug(_("Loaded application \'") + str(app_object.id) + "\'")
		except Exception, e:
			debug(_("Error loading application from path \'") + path + "\': " + str(e))
			traceback.print_exc(file=debugfile)
			if hasattr(p, "app_path") and p.app_path:
				shutil.rmtree(p.app_path, True)
			if hasattr(p, "id") and p.id:
				managers.resource_manager.invalidate_resources(p.id)
			return (None, str(e))
		if not result:
			return ("", "")
		app_object.set_info("Active", "1")
		app_object.invalidate_libraries()
		return (str(app_object.id), "")

	def uninstall_application(self, appid, remove_db = True, remove_zero_res = True):
		"""uninstall application, delete application xml file"""
		if not managers.acl_manager.session_user_has_access2(appid, appid, security.delete_application):
			raise VDOM_exception_sec(_("Deleting application is not allowed"))
		autolock = VDOM_named_mutex_auto("uninstall_" + appid)
		appobj = None
		try:
			appobj = self.get_application(appid)
		except:
			return True
		
		# delete all objects from this application
		l = []
		for o in appobj.objects_list:
			l.append(o)
		for o in l:
			#debug("\n"+str(o) + "\n")
			appobj.delete_object(o)
#		del(appobj.xml_manager)
		self.__sem.lock()
		try:
			del self.__applications[appid]
			self.__app_id_list.remove(appid)
			self.__sync_app()
		finally:
			self.__sem.unlock()

		appobj.objects.clear()
		del appobj.objects
		del appobj.objects_list
		del appobj._VDOM_application__all_objects
		
		
		# remove source
		managers.source_cache.clear_container_swap(appid)
		#clear libraries cache
		appobj.invalidate_libraries()		
		# remove libs
		managers.file_manager.delete_libs(appid)
		
		# remove resources
		lst = managers.resource_manager.list_resources(appid)
		for ll in lst:
			ro = managers.resource_manager.get_resource(appid, ll)
			if len(ro.dependences) > 0 or remove_zero_res:
				debug("Remove resource %s" % ll)
				try:
					managers.resource_manager.delete_resource(None, ll, True)
				except Exception, e:
					debug("Error removing resource '%s': %s" % (ll, str(e)))
			else:
				debug("Keep resource %s" % ll)
		#managers.resource_manager.invalidate_resources(appid)

		# remove databases
		if remove_db:
			managers.database_manager.delete_database(appid)

		# remove files
		l = [application_path, resources_path]
		if remove_db:
			l.append(databases_path)
		for item in l:
			the_path = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], item, appid)
			try: shutil.rmtree(the_path)
			except: pass
#		the_path = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], resources_path, appid)
#		try: shutil.rmtree(the_path)
#		except: pass
#		the_path = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], databases_path, appid)
#		try: shutil.rmtree(the_path)
#		except: pass
		
		del appobj
		return True

	def export_application(self, appid, exptype, path):
		"""export application: save to path/<appid>.xml or path/<appid>.zip"""
		if exptype not in ["xml", "zip"]:
			raise VDOM_exception_param("Unsupported export type")
		app = self.get_application(appid)
		self.__export_xml(app, path)
		if "zip" == exptype:
			self.__export_zip(app, path)
		return True

	def __export_db(self, app, file):
		file.write("<Databases>\n")
		lst = managers.database_manager.list_databases(app.id)
		for ll in lst:
			do = managers.database_manager.get_database(app.id, ll)
			data = managers.file_manager.read(file_access.database, app.id, None, do.filename)
			if "" != do.name and len(data) > 0:
				data = base64.b64encode(data)
				x = """\t<Database ID="%s" Name="%s" Type="sqlite">""" % (do.id, do.name)
				file.write(x.encode("utf-8"))
				file.write(data)
				file.write("</Database>\n")
		file.write("</Databases>\n")

	def __export_sec(self, app):
		g = "\t<Groups>\n"
		o = app.get_all_objects().keys() + [app.id]
		groups = {}	# map group_name to list [(id, access), ...]
		users = {}	# map login to list [(id, access), ...]
		for _id in o:
			if _id in managers.acl_manager.acl:
				for _name in managers.acl_manager.acl[_id]:
					_access = ",".join(map(str, managers.acl_manager.acl[_id][_name].keys()))
					obj = managers.user_manager.get_group_by_name(_name)
					if obj and not obj.system:
						if _name not in groups:
							groups[_name] = []
						groups[_name].append((_id, _access))
					obj = managers.user_manager.get_user_object(_name)
					if obj and not obj.system:
						if _name not in users:
							users[_name] = []
						users[_name].append((_id, _access))
		for _name in groups:
			obj = managers.user_manager.get_group_by_name(_name)
			g += "\t\t<Group>\n\t\t\t<Name><![CDATA[%s]]></Name>\n\t\t\t<Description><![CDATA[%s]]></Description>\n\t\t\t<Rights>\n" % (_name, obj.description)
			for item in groups[_name]:
				g += '\t\t\t\t<Right Target="%s" Access="%s"/>\n' % item
			g += "\t\t\t</Rights>\n\t\t</Group>\n"
		g += "\t</Groups>\n"
		u = "\t<Users>\n"
		for _name in users:
			obj = managers.user_manager.get_user_object(_name)
			u += "\t\t<User>\n\t\t\t<Login><![CDATA[%s]]></Login>\n\t\t\t<Password><![CDATA[%s]]></Password>\n\t\t\t<FirstName><![CDATA[%s]]></FirstName>\n\t\t\t<LastName><![CDATA[%s]]></LastName>\n\t\t\t<Email><![CDATA[%s]]></Email>\n\t\t\t<SecurityLevel><![CDATA[%s]]></SecurityLevel>\n\t\t\t<MemberOf><![CDATA[%s]]></MemberOf>\n\t\t\t<Rights>\n" % (_name, obj.password, obj.first_name, obj.last_name, obj.email, obj.security_level, ",".join(obj.member_of))
			for item in users[_name]:
				u += '\t\t\t\t<Right Target="%s" Access="%s"/>\n' % item
			u += "\t\t\t</Rights>\n\t\t</User>\n"
		u += "\t</Users>\n"
		return "<Security>\n" + g + u + "</Security>\n"

	def __export_xml(self, app, path):
		"""export application as xml file"""
		file = open(os.path.join(path, app.id + ".xml"), "wb")
		xmlstr = app.get_xml_as_string()
		s = "</Application>"
		parts = xmlstr.split(s)
		file.write(parts[0])
		del parts
		# resources
		file.write("<Resources>\n")
		lst = managers.resource_manager.list_resources(app.id)
		for ll in lst:
			ro = managers.resource_manager.get_resource(app.id, ll)
			if "" == ro.label:
				try:
					data = ro.get_data()
				except:
					continue
				data = base64.b64encode(data)
				x = """\t<Resource ID="%s" Type="%s" Name="%s">""" % (ro.id, ro.res_format, ro.name)
				file.write(x.encode("utf-8"))
				file.write(data)
				file.write("</Resource>\n")
		file.write("</Resources>\n")
		# db
		self.__export_db(app, file)
		# sec
		file.write(self.__export_sec(app))
		# finish
		file.write(s)
		file.close()

	def __export_zip(self, app, path):
		"""export application as zip file"""
		fsrc = os.path.join(path, app.id)
		zf = zipfile.ZipFile(fsrc + ".zip", mode="w", compression=zipfile.ZIP_DEFLATED)
		zf.write(fsrc + ".xml", "app.xml")
		zf.close()
		try: os.remove(fsrc + ".xml")
		except: pass

	def modify_objects_count(self, num):
		self.__sem.lock()
		self.obj_count += num
		self.__sem.unlock()

	def uninstall_abnormal(self, app):
		for o in app.o_tmp:
			self.modify_objects_count(-1)
		del app.o_tmp
		if hasattr(app, "id"):
			managers.resource_manager.invalidate_resources(app.id)
			managers.database_manager.delete_database(app.id)
		if hasattr(app, "objects"):
			del app.objects
		if hasattr(app, "objects_list"):
			del app.objects_list
		if hasattr(app, "_VDOM_application__all_objects"):
			del app._VDOM_application__all_objects


import managers, security, file_access

from utils.mutex import VDOM_named_mutex_auto
from utils.semaphore import VDOM_semaphore
from utils.exception import *
from utils.uuid import uuid4

from .type import VDOM_type
from application import VDOM_application
from enumerator import VDOM_application_enumerator, VDOM_type_enumerator
from .parseapp import parseapp
from .xml_object import xml_object
from file_access.manager import application_path, resources_path, databases_path
# from server.local_server import wait_for_options
from version import VDOM_server_version
