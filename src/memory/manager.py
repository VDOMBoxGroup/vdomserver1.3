"""XML Manager module"""

import shutil, os, os.path, sys, traceback, base64, zipfile, time, copy # , thread
from metaimporter import VDOM_metaimporter
from utils.threads import VDOM_daemon
from daemon import VDOM_xml_synchronizer
from utils.card_connect import send_to_card
from names import APPLICATION_SECTION, ON_UNINSTALL
from database.dbobject import VDOM_sql_query

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
		managers.scheduler_manager.restore()

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
		types = VDOM_type_enumerator().get()
		types_count = len(types)
		for counter in xrange(types_count):
			fname = types[counter]
			if counter > types_count/4.0 and counter <= (types_count/4.0 +1):
				send_to_card("booting 30")
			elif counter > types_count/4.0*2 and counter <= (types_count/4.0*2 +1):
				send_to_card("booting 40")
			elif counter > types_count/4.0*3 and counter <= (types_count/4.0*3 +1):
				send_to_card("booting 50")
			try:
				(result, type_object) = self.load_type(fname)
				if result:
					sys.stderr.write(_("Loaded type \'") + str(type_object.id) + "\' name \'" + str(type_object.name) + "\'\n")
				else:
					sys.stderr.write(_("  Type \'") + str(type_object.name) + "\' ignored due to duplicate ID (owned by %s)\n" % self.__types[type_object.id].name)
			except Exception, e:
				sys.stderr.write(_("Error loading type \'") + str(fname) + "\': " + str(e) + "\n")
				traceback.print_exc(file=debugfile)
		wait_for_options()
		send_to_card("booting 60")
		# list files in app directory and load applications from files
		apps = VDOM_application_enumerator().get()
		apps_count = len(apps)
		for counter in xrange(apps_count):
			fname = apps[counter]
			if counter > apps_count/4.0 and counter <= (apps_count/4.0 +1):
				send_to_card("booting 70")
			elif counter > apps_count/4.0*2 and counter <= (apps_count/4.0*2 +1):
				send_to_card("booting 80")
			elif counter > apps_count/4.0*3 and counter <= (apps_count/4.0*3 +1):
				send_to_card("booting 90")
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

		self.__daemon=VDOM_xml_synchronizer(self)
		self.__daemon.start()
		send_to_card("booting 100")


	def work(self):
		if len(self.__app_to_sync) > 0:
			#debug("APP SEM LOCK")
			self.__app_sem.lock()
			try:
				#debug("APP SEM WORK")
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
								managers.file_manager.two_step_write(file_access.application_xml, the_id, None, None, xmlstr, False, False)
							except Exception, e:
								debug("\nApplication '%s' save error: %s\n" % (the_id, str(e)))
			finally:
				#debug("APP SEM UNLOCK")
				self.__app_sem.unlock()
				#debug("APP SEM DONE")
		
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
		"""load type object from external xml file, Return: tuple(bool(if type exists), type xml object)"""
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
				if not self.__type_id_list.count(obj.id):
					self.__type_id_list.append(obj.id)
			finally:
				self.__sem.unlock()
			return (True, obj)
		return (False, obj)

	def unload_type(self, _id):
		self.__sem.lock()
		try:
			if _id in self.__types:
				obj = self.__types[_id]
				del self.__types[_id]
				del self.__type_by_name[obj.name.lower()]
				self.__type_id_list.remove(_id)
				del obj
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
			#debug("APP SYNC LOCK")
			self.__app_sem.lock()
			try:
				#debug("APP SYNC APPEND")
				self.__app_to_sync.append(app_id)
			finally:
				#debug("APP SYNC UNLOCK")
				self.__app_sem.unlock()
				#debug("APP SYNC DONE")

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

	def import_application(self, path, ignore_version=False):
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
			if p.key.strip():
				from local_server.local_server import check_application_license
				if not p.key.strip().isdigit() or check_application_license(p.id, p.key.strip()) in ("None","0"):
					raise Exception("You have no permission to install this application. Please contact your dealer for support.")
			(result, app_object) = self.load_application(p.work_xml_file)
			if not result:			# previous version of application not removed?
				return ("", "")
			app_version = app_object.server_version or "0.0.0"
			app_object.server_version = VDOM_server_version
			app_object.information_element.get_child_by_name("serverversion").value = VDOM_server_version
			app_object.sync()
			
			
			app_object.set_info("Active", "1")
			app_object.invalidate_libraries()
			debug(_("Loaded application \'") + str(app_object.id) + "\'")
			if not ignore_version:
				if app_version.split('.')[:2] != VDOM_server_version.split('.')[:2]:
					return (str(app_object.id), "This application could not be installed on server version %s.%s. Please contact your dealer for support."%tuple(VDOM_server_version.split('.')[:2]))
				if VDOM_server_version.split('.')[2] < app_version.split('.')[2]:
					return (str(app_object.id), "Server version (%s) is unsuitable for this application (%s)" % (VDOM_server_version, app_version))
			
		except Exception, e:
			debug(_("Error loading application from path \'") + path + "\': " + str(e))
			traceback.print_exc(file=debugfile)
			if hasattr(p, "app_path") and p.app_path:
				shutil.rmtree(p.app_path, True)
			if hasattr(p, "id") and p.id:
				managers.resource_manager.invalidate_resources(p.id)
			return (None, str(e))
		
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
			raise
			##return True
		
		
		on_uninstall=appobj.global_actions[APPLICATION_SECTION][APPLICATION_SECTION+ON_UNINSTALL]
		if on_uninstall.code:
			__import__(appobj.id)
			try:
				managers.engine.special(appobj, on_uninstall, namespace={})
			except Exception as e:
				debug("Error while executing application onuninstall action: %s"%str(e))
				traceback.print_exc(file=debugfile)
						
		
		# delete all objects from this application
		l = []
		for o in appobj.objects_list:
			l.append(o)
		for o in l:
			#debug("\n"+str(o) + "\n")
			appobj.delete_object(o)
		# delete databases
		
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
			if ro and (len(ro.dependences) > 0 or remove_zero_res):
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
			try:
				the_path = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], item, appid)
				shutil.rmtree(the_path, ignore_errors=True)
			except: pass
#		the_path = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], resources_path, appid)
#		try: shutil.rmtree(the_path)
#		except: pass
#		the_path = os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"], databases_path, appid)
#		try: shutil.rmtree(the_path)
#		except: pass
		
		del appobj
		return True

	def export_application(self, appid, exptype, path, embed_types = False):
		"""export application: save to path/<appid>.xml or path/<appid>.zip"""
		if exptype not in ["xml", "zip"]:
			raise VDOM_exception_param("Unsupported export type")
		app = self.get_application(appid)
		self.__export_xml(app, path, embed_types)
		if "zip" == exptype:
			self.__export_zip(app, path)
		return True

	def __export_db(self, app, file):
		"""praparing database data for app export"""
		file.write("\t<Databases>\n")
		lst = managers.database_manager.list_databases(app.id)
		for ll in lst:
			query = VDOM_sql_query(app.id, ll, "VACUUM")
			query.commit()
			query.close()
			do = managers.database_manager.get_database(app.id, ll)
			data = managers.file_manager.read(file_access.database, app.id, None, do.filename)
			if "" != do.name and len(data) > 0:
				data = base64.b64encode(data)
				x = """\t\t<Database ID="%s" Name="%s" Type="sqlite">""" % (do.id, do.name)
				file.write(x.encode("utf-8"))
				file.write(data)
				file.write("</Database>\n")
		file.write("\t</Databases>\n")

	def __export_sec(self, app):
		"""praparing security data for app export"""
		g = "\t\t<Groups>\n"
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
			g += "\t\t\t<Group>\n\t\t\t<Name><![CDATA[%s]]></Name>\n\t\t\t\t<Description><![CDATA[%s]]></Description>\n\t\t\t<Rights>\n" % (_name, obj.description)
			for item in groups[_name]:
				g += '\t\t\t\t<Right Target="%s" Access="%s"/>\n' % item
			g += "\t\t\t\t</Rights>\n\t\t</Group>\n"
		g += "\t\t</Groups>\n"
		u = "\t\t<Users>\n"
		for _name in users:
			obj = managers.user_manager.get_user_object(_name)
			u += "\t\t\t<User>\n\t\t\t\t<Login><![CDATA[%s]]></Login>\n\t\t\t\t<Password><![CDATA[%s]]></Password>\n\t\t\t\t<FirstName><![CDATA[%s]]></FirstName>\n\t\t\t\t<LastName><![CDATA[%s]]></LastName>\n\t\t\t\t<Email><![CDATA[%s]]></Email>\n\t\t\t<SecurityLevel><![CDATA[%s]]></SecurityLevel>\n\t\t\t<MemberOf><![CDATA[%s]]></MemberOf>\n\t\t\t<Rights>\n" % (_name, obj.password, obj.first_name, obj.last_name, obj.email, obj.security_level, ",".join(obj.member_of))
			for item in users[_name]:
				u += '\t\t\t\t<Right Target="%s" Access="%s"/>\n' % item
			u += "\t\t\t\t</Rights>\n\t\t</User>\n"
		u += "\t\t</Users>\n"
		l = self.__export_ldap(app)
		return "\t<Security>\n" + g + u + l + "\t</Security>\n"

	def __export_xml(self, app, path,embed_types = False):
		"""export application as xml file"""
		file = open(os.path.join(path, app.id + ".xml"), "wb")
		xmlstr = app.get_xml_as_string()
		s = "</Application>"
		parts = xmlstr.split(s)
		file.write(parts[0])
		del parts
		# resources
		file.write("\t<Resources>\n")
		lst = managers.resource_manager.list_resources(app.id)
		for ll in lst:
			ro = managers.resource_manager.get_resource(app.id, ll)
			if "" == ro.label:
				try:
					data = ro.get_data()
				except:
					continue
				data = base64.b64encode(data)
				x = """\t\t<Resource ID="%s" Type="%s" Name="%s">""" % (ro.id, ro.res_format, ro.name)
				file.write(x.encode("utf-8"))
				file.write(data)
				file.write("</Resource>\n")
		file.write("\t</Resources>\n")
		# db
		self.__export_db(app, file)
		# sec
		file.write(self.__export_sec(app))
		if embed_types:
			file.write(self.__export_types(app))
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
		
	def __export_types(self,app):
		"""praparing <EmbededTypes data for app export"""
		from cStringIO import StringIO
		main_buf = StringIO()
		main_buf.write("\t<EmbeddedTypes>\n")
		used_types = set()
		for obj_id in app.get_all_objects():
			used_types.add(app.search_object(obj_id).type)
		for u_type in used_types:
			main_buf.write(("\t\t<EmbeddedType ID=\"%s\" Name=\"%s\" Timestamp=\"%s\">"%(u_type.id,u_type.name,os.stat(u_type.filename)[8])).encode("utf8"))
			type_buf = StringIO()
			xmlstr = u_type.get_xml_as_string()
			sep = "</Type>"
			parts = xmlstr.split(sep)
			type_buf.write(parts[0].encode("utf8"))
			del parts
			# resources
			type_buf.write("<Resources>\n")
			res_lst = managers.resource_manager.list_resources(u_type.id)
			for res_id in res_lst:
				resource = managers.resource_manager.get_resource(u_type.id, res_id)
				if not resource.label:
					try:
						data = resource.get_data()
					except:
						continue
					data = base64.b64encode(data)
					x = """\t<Resource ID="%s" Type="%s" Name="%s">""" % (resource.id, resource.res_format, resource.name)
					type_buf.write(x.encode("utf-8"))
					type_buf.write(data)
					type_buf.write("</Resource>\n")
			type_buf.write("</Resources>\n")
			type_buf.write("</Type>")
			main_buf.write(base64.b64encode(type_buf.getvalue()))
			del type_buf
			main_buf.write("</EmbeddedType>\n")
			
		main_buf.write("\t</EmbeddedTypes>\n")
		return main_buf.getvalue()
	
	def __export_ldap(self, app):
		from subprocess import *
		import shlex, shutil, tempfile
		from cStringIO import StringIO
		main_buf = StringIO()
		main_buf.write("\t\t<LDAP>")
		path = tempfile.mkdtemp("", "ldap", VDOM_CONFIG["TEMP-DIRECTORY"])
		cmd = """sh /opt/boot/ldap_backup.sh -g %s -b -o %s""" % (app.id, os.path.abspath(path))
		out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
		out.wait()
		rc = out.returncode
		if rc == 0:
			zf = zipfile.ZipFile(os.path.join(path, "ldap.zip"), mode="w", compression=zipfile.ZIP_DEFLATED)
			l = os.listdir(path)
			for file_name in l:
				if file_name != "ldap.zip":
					zf.write(os.path.join(path, file_name))
				
			zf.close()
			data = managers.file_manager.read_file(os.path.join(path, "ldap.zip"))
			data = base64.b64encode(data)
			main_buf.write(data.encode("utf-8"))
		main_buf.write("</LDAP>\n")
		return main_buf.getvalue()
	    
	def modify_objects_count(self, num):
		self.__sem.lock()
		try:
			self.obj_count += num
		finally:
			self.__sem.unlock()

	def uninstall_abnormal(self, app):
		if hasattr(app, "o_tmp"):
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
from local_server.local_server import wait_for_options
from version import VDOM_server_version
