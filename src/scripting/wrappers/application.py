
import re, managers, threading

DBSCHEMA_ID = '753ea72c-475d-4a29-96be-71c522ca2097'
DBTABLE_ID = '92269b6e-4b6b-4882-852f-f7ef0e89c079'

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

class VDOM_storage(object):
	
	pass

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
		self.database = managers.database_manager.get_database_by_name(managers.request_manager.current.app_id(), self.__name)
		if not self.database or (not self.database.is_ready and not self.database.open()):
			raise Exception("Database with name \"%s\" does not exist" % self.__name)
		self.__conn = self.database.get_connection()
		self.__cur = self.__conn.cursor()
			
	def fetchone(self, sql, params={}):
		self.__cur.execute(sql, params)
		return self.__cur.fetchone()
			
	def fetchall(self, sql, params={}):
		self.__cur.execute(sql, params)
		return self.__cur.fetchall()
			
	def commit(self, sql=None, params={}):
		if sql is not None:
			self.__cur.execute(sql, params)
		if self.__conn:
			self.__conn.commit()
		return (self.__cur.lastrowid, self.__cur.rowcount)
		
	def create(self, table_name, table_diffinition=""):
		application_id=managers.request_manager.current.app_id()
		application = managers.xml_manager.get_application(application_id)
		parent = application.search_objects_by_name(self.__name)
		if table_name in parent[0].get_objects_by_name().keys():
			obj = application.search_objects_by_name(table_name)[0]
			return self.database.get_table(obj.id, table_name, table_diffinition)
		else:
			obj_name,obj_id = application.create_object(DBTABLE_ID, parent[0])
			obj = application.search_object(obj_id)
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
		
	__db = threading.local()

	def __getattribute__(self, name):
			try:
				return object.__getattribute__(self, name)
			except:
				if getattr(self.__db, 'database', None) is None:
					self.__db.database = VDOM_database(name)
				return self.__db.database
	
	def create(self, db_name, title="DBSchema", description=""):
		application_id=managers.request_manager.current.app_id()
		application = managers.xml_manager.get_application(application_id)
		database = managers.database_manager.get_database_by_name(application_id, db_name)
		if not database:
			obj_name, obj_id = application.create_object(DBSCHEMA_ID)
			obj = application.search_object(obj_id)
			obj.set_name(db_name)
			obj.set_attributes({"title": title, "description": description})
			database = managers.database_manager.get_database(application_id, obj_id)
			database.name = db_name
			database.open()
		return database
		
	def get_list(self):
		application_id=managers.request_manager.current.app_id()
		return managers.database_manager.list_databases(application_id)
	
class VDOM_resources(object):
	
	def create(self, data, resource_format="res", name=""):
		"""Create new resource"""
		application_id=managers.request_manager.current.app_id()
		attributes = {"res_type":"permanent",
						"res_format":resource_format,
						"name":name,
		
						}
		managers.resource_manager.add_resource(application_id, None, attributes, data)
		#application.create_resource(application.id, as_string(type), as_string(name), as_binary(data))
		return id
		
	def delete(self, resource_id):
		"""Delete resource"""
		application_id=managers.request_manager.current.app_id()
		managers.resource_manager.delete_resource(application_id, resource_id)

	def create_temporary(self, object_id, label, data, resource_format="res", name=""):
		"""Create temporary resource with lable"""
		application_id=managers.request_manager.current.app_id()
		
		attributes = {"res_type":"temporary",
					  "res_format":resource_format,
					  "name":name,
					  "label":label,
					 }
		
		managers.resource_manager.add_resource(application_id, object_id, attributes, data)

	def get(self, res_id):
		"""Geting resource"""
		application_id=managers.request_manager.current.app_id()
		managers.resource_manager.get_resource(application_id, res_id)
		
	def get_list(self):
		"""Geting resource list"""
		application_id=managers.request_manager.current.app_id()
		managers.resource_manager.list_resource(application_id)		
		
	def get_by_label(self, object_id, label):
		managers.resource_manager.get_resource_by_label(object_id, label)	
		
	
class VDOM_application(object):
	
	def __init__(self):
		self._objects=VDOM_objects()
		self._databases=VDOM_databases()
		self._resources=VDOM_resources()
		self._storage=VDOM_storage()

	def _get_id(self):
		return managers.request_manager.current.app_id()

	def _get_name(self):
		return managers.request_manager.current.application().name
		
	def _get_structure(self):
		return managers.request_manager.current.application().app_map
	
	id=property(_get_id)
	name=property(_get_name)
	structure=property(_get_structure)
	objects=property(lambda self: self._objects)
	databases=property(lambda self: self._databases)
	resources=property(lambda self: self._resources)
	storage=property(lambda self: self._storage)
