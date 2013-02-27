
import re, managers, threading,os
from utils.exception import VDOM_exception_file_access
from file_access import storage as app_storage
#from file_access import application_storage
DBSCHEMA_ID = '753ea72c-475d-4a29-96be-71c522ca2097'
DBTABLE_ID = '92269b6e-4b6b-4882-852f-f7ef0e89c079'

db_local = threading.local()
app_local = threading.local()

class VDOM_objects(object):
	
	guid_regex=re.compile("[0-9A-Z]{8}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{12}", re.IGNORECASE)
	
	def create(self, type, parent, name=None):
		application=managers.request_manager.get_request().application()
		if not VDOM_objects.guid_regex.search(type):
			xml_type=managers.xml_manager.get_type_by_name(type)
			type=xml_type.id if xml_type is not None else None
		if VDOM_objects.guid_regex.search(parent):
			parent=application.search_object(parent)
		else:
			objects=application.search_objects_by_name(parent)
			parent=objects[0] if len(objects)==1 else None
		if type is None or parent is None: return None
		object_tuple=application.create_object(type, parent)
		object=application.search_object(object_tuple[1])
		if name is not None: object.set_name(name)
		return object

	def delete(self, object_string):
		application=managers.request_manager.get_request().application()
		if VDOM_objects.guid_regex.search(object_string):
			object=application.search_object(object_string)
		else:
			objects=application.search_objects_by_name(object_string)
			object=objects[0] if len(objects)==1 else None
		if object is None: return
		application.delete_object(object)

	def search(self, object_string):
		application=managers.request_manager.get_request().application()
		if VDOM_objects.guid_regex.search(object_string):
			object=application.search_object(object_string)
		else:
			objects=application.search_objects_by_name(object_string)
			object=objects[0] if objects else None
		return object

class VDOM_file_storage(object):
	
	def __init__(self):
		pass
		
	def open(self, filename, mode="rb"):
		from scripting.wrappers import application
		return managers.file_manager.get_fd(app_storage, application.id, None, self.__norm_filename(filename), mode)

	def opentmp(self, mode="w+b", prefix="app_data"):
		return managers.file_manager.open_tmp_file(mode, prefix)
	
	def readall(self, filename):
		from scripting.wrappers import application
		return managers.file_manager.read(app_storage, application.id, None, self.__norm_filename(filename))

	def write(self, filename, content):
		from scripting.wrappers import application
		return managers.file_manager.write(app_storage, application.id, None, self.__norm_filename(filename),content)
	
	def write_async(self, filename, content):
		from scripting.wrappers import application
		return managers.file_manager.write(app_storage, application.id, None, self.__norm_filename(filename),content,False, True)
	
	def getsize(self, filename):
		from scripting.wrappers import application
		return managers.file_manager.size(app_storage, application.id, None, self.__norm_filename(filename))
	
	def delete(self, filename):
		from scripting.wrappers import application
		return managers.file_manager.delete(app_storage, application.id, None, self.__norm_filename(filename))
	
	def abs_path(self, filename):
		from scripting.wrappers import application
		return os.path.abspath(managers.file_manager.get_path(app_storage, application.id, None, self.__norm_filename(filename)))
	
	def exists(self, filename):
		from scripting.wrappers import application
		return managers.file_manager.exists(app_storage, application.id, None, self.__norm_filename(filename))
	
	def mkdir(self, foldername):
		from scripting.wrappers import application
		managers.file_manager.create_app_storage_user_directory(application.id, self.__norm_filename(foldername))

	def rmtree(self, foldername):
		from scripting.wrappers import application
		managers.file_manager.delete_app_storage_user_directory(application.id, self.__norm_filename(foldername))
		
	def listdir(self, foldername):
		from scripting.wrappers import application
		return managers.file_manager.list_app_storage_directory(application.id, self.__norm_filename(foldername))
	
	def isfile(self, path):
		from scripting.wrappers import application
		return os.path.isfile(managers.file_manager.get_path(app_storage, application.id, None, self.__norm_filename(path)))		

	def isdir(self,path):
		from scripting.wrappers import application
		return os.path.isdir(managers.file_manager.get_path(app_storage, application.id, None, self.__norm_filename(path)))		
	
	def __norm_filename(self, filename):
		from scripting.wrappers import application
		norm_name = os.path.normpath(filename)
		rel_path = os.path.relpath(os.path.abspath(managers.file_manager.get_path(app_storage, application.id, None, norm_name)),
		                           os.path.abspath(VDOM_CONFIG["FILE-STORAGE-DIRECTORY"]))
		if rel_path[:36]!= application.id:
			raise VDOM_exception_file_access("Provided file name is invalid")
		return norm_name
	
class VDOM_cursor_object(object):

	def __init__(self, connection, cursor):
		self.__conn = connection
		self.__cur = cursor
		self.finished = False
		
	def fetchone(self):
		return self.__cur.fetchone()
		
	def fetchmany(self, size=None):
		if size is None:
			size = self.__cur.arraysize
		return self.__cur.fetchmany(size)
	def fetchall(self):
		return self.__cur.fetchall()
	def rows(self):
		if not self.finished:
			for row in self.__cur:
				yield row
		self.finished = True
	def _lastrowid(self):
		return self.__cur.lastrowid
	def _rowcount(self):
		return self.__cur.rowcount
	def commit(self):
		if self.__conn:
			self.__conn.commit()
			
	lastrowid=property(_lastrowid)
	rowcount=property(_rowcount)
	
class VDOM_database(object):
	
	def __enter__(self):
		return self
		
	def __exit__(self, type, value, traceback):
		if type is None:
			self.__conn.commit()
		else:
			self.__conn.rollback()
		
	def __init__(self, name):
		self.__name = name
		from scripting.wrappers import application
		self.database = managers.database_manager.get_database_by_name(application.id, self.__name)
		#if not self.database or (not self.database.is_ready and not self.database.open()):
		if not self.database:
			raise Exception("Database with name \"%s\" does not exist" % self.__name)
		elif not self.database.is_ready and not self.database.open():
			raise Exception("Database with name \"%s\" could not be opened" % self.__name)
		self.__conn = self.database.get_connection()
		self.__cur = self.__conn.cursor()
			
	def fetchone(self, sql, params={}):
		self.__cur.execute(sql, params)
		return self.__cur.fetchone()
			
	def fetchall(self, sql, params={}):
		self.__cur.execute(sql, params)
		return self.__cur.fetchall()
			
	def commit(self, sql=None, params=()):
		if sql is not None:
			self.__cur.execute(sql, params)
		if self.__conn:
			self.__conn.commit()
		return (self.__cur.lastrowid, self.__cur.rowcount)
	
	def commit_isolated(self, sql, params=()):
		conn = self.database.open(timeout = 25.0)
		cur = conn.cursor()
		cur.execute(sql, params)
		conn.commit()
		return (cur.lastrowid, cur.rowcount)		

	def create(self, table_name, table_diffinition=""):
		from scripting.wrappers import application
		application_memmory = managers.xml_manager.get_application(application.id)
		parent = application_memmory.search_objects_by_name(self.__name)
		if not parent:
			raise Exception("Database %s is not exist. Cannot create table inside."%self.__name)
		if table_name in parent[0].get_objects_by_name().keys():
			obj = application_memmory.search_objects_by_name(table_name)[0]
			return self.database.get_table(obj.id, table_name, table_diffinition)
		else:
			obj_name,obj_id = application_memmory.create_object(DBTABLE_ID, parent[0],False)
			obj = application_memmory.search_object(obj_id)
			obj.set_name(table_name)
			#obj.set_attributes({"top":500,"left":600,"width": 200,"height":300})
			return self.database.get_table(obj_id, table_name, table_diffinition)

	def query(self, sql, params={}):
		self.__cur.execute(sql, params)
		return VDOM_cursor_object(self.__conn, self.__cur)
		
	def execute(self, sql, params={}):
		self.__cur.execute(sql, params)
		
	def executemany(self, sql, seq_of_params):
		self.__cur.executemany(sql, seq_of_params)
		
	def executescript(self, sql_script):
		self.__cur.executescript(sql_script)
	
	def get_list(self):
		return self.database.get_tables_list()

class VDOM_databases(object):
	def __getattribute__(self, name):
			try:
				return object.__getattribute__(self, name)
			except:
				#if getattr(VDOM_databases.__db, 'database', None) is None:
				#	VDOM_databases.__db.database = VDOM_database(name)
				#temporary to fix bug
				return VDOM_database(name)#VDOM_databases.__db.database
	
	def create(self, db_name, title="DBSchema", description=""):
		from scripting.wrappers import application
		application_memmory = managers.xml_manager.get_application(application.id)
		if not application_memmory.search_objects_by_name(db_name):
			obj_name, obj_id = application_memmory.create_object(DBSCHEMA_ID,do_compute=False)
			obj = application_memmory.search_object(obj_id)
			obj.set_name(db_name)
			obj.set_attributes({"title": title, "description": description}, do_)
			
		database = managers.database_manager.get_database_by_name(application.id, db_name)
		if not database:		
			database = managers.database_manager.create_database(application.id, obj_id, db_name)
			database.open()
		return database
		
	def get_list(self):
		from scripting.wrappers import application
		return managers.database_manager.list_databases(application.id)
	
class VDOM_resources(object):
	
	def create(self, data, resource_format="res", name=""):
		"""Create new resource"""
		from scripting.wrappers import application
		attributes = {"res_type":"permanent",
						"res_format":resource_format,
						"name":name,
		
						}
		res_id = managers.resource_manager.add_resource(application.id, None, attributes, data)
		#application.create_resource(application.id, as_string(type), as_string(name), as_binary(data))
		return res_id
		
	def delete(self, resource_id):
		"""Delete resource"""
		from scripting.wrappers import application
		managers.resource_manager.delete_resource(application.id, resource_id,True)

	def create_temporary(self, object_id, label, data, resource_format="res", name=""):
		"""Create temporary resource with lable"""
		from scripting.wrappers import application
		attributes = {"res_type":"temporary",
					  "res_format":resource_format,
					  "name":name,
					  "label":label,
					 }
		
		res_id = managers.resource_manager.add_resource(application.id, object_id, attributes, data)
		return res_id

	def get(self, res_id):
		"""Geting resource"""
		from scripting.wrappers import application
		return managers.resource_manager.get_resource(application.id, res_id)
		
	def get_list(self):
		"""Geting resource list"""
		from scripting.wrappers import application
		return managers.resource_manager.list_resource(application.id)		
		
	def get_by_label(self, object_id, label):
		return managers.resource_manager.get_resource_by_label(object_id, label)	
		
	
class VDOM_application(object):
	__app = threading.local()
	
	def __init__(self):
		self._objects=VDOM_objects()
		self._databases=VDOM_databases()
		self._resources=VDOM_resources()
		self._storage=VDOM_file_storage()

	def _get_id(self):
		if getattr(VDOM_application.__app, "app_id", None):
			return VDOM_application.__app.app_id
		else:
			return managers.request_manager.current.app_id()

	def _get_name(self):
		app_id = self._get_id()
		return managers.xml_manager.get_application(app_id).name
		
	def _get_structure(self):
		app_id = self._get_id()
		return managers.xml_manager.get_application(app_id).app_map
	
	def set_app_id(self, app_id):
		VDOM_application.__app.app_id = app_id
	
	def _get_version(self):
		return managers.xml_manager.get_application(self.id).version


	version=property(_get_version)
	id=property(_get_id)
	name=property(_get_name)
	structure=property(_get_structure)
	objects=property(lambda self: self._objects)
	databases=property(lambda self: self._databases)
	resources=property(lambda self: self._resources)
	storage=property(lambda self: self._storage)
	itself=property(lambda self: managers.request_manager.current.application()) # temporary, for objectview

	
