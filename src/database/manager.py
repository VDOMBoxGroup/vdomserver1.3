"""database manager"""
import string
import sys
import src.util.uuid
import src.file_access
from src.util.exception import VDOM_exception
from src.database.dbobject import VDOM_database_object
from src.database.dbobject import VDOM_database_table
from xml.dom.minidom import parseString
from xml.dom import Node
import time

class VDOM_database_manager(object):
	"""database manager class"""

	def __init__(self):
		"""constructor"""
		self.__index = {}
	
	def restore(self):	
		"""Restoring databases from last session.(After reboot or power off)"""
		self.__index = src.storage.storage.read_object(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"])
		if self.__index:
			remove_list = []
			is_dirty_index = False
			for id in self.__index: #check for not existing or temporary resources
				database = self.__index[id]
				if not src.file_access.file_manager.exists(src.file_access.database,database.owner_id,None, database.filename):
					remove_list.append(id)

			for id in remove_list:
				self.__index.pop(id)
				is_dirty_index = True
				
			if is_dirty_index:
				src.storage.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"],self.__index)
		else:
			self.remove_databases()
	
	def add_database(self, owner_id, attributes, data):
		"""Adding a new database"""
		if "id" in attributes and attributes["id"] in self.__index:
			pass
		else:
			database = VDOM_database_object(owner_id,attributes["id"])
			try:
				for key in attributes:
					if key != "id" or key != "type":
						setattr(database, key, attributes[key])
						#exec "database." + key + " = \"" + attributes[key] + "\""
			except:
				pass
			
			self.__index[database.id] = database
			if attributes["type"] == "sqlite":
				src.file_access.file_manager.write(src.file_access.database,database.owner_id,None, database.filename, data)
			elif attributes["type"] == "xml":
				self.create_from_xml(database, data)
			elif attributes["type"] == "multifile":
				self.create_from_tar(database, data)
			src.storage.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"],self.__index)
		return attributes["id"]
		
	def check_database(self, owner_id, id):
		"""Check a database"""
		if id not in self.__index:
			return False
		database = self.__index[id]
		if database.owner_id != owner_id:
			return False
		if not database.filename:
			return False
		return True
			
	def get_database(self, owner_id, db_id):
		"""Getting database object"""
		database = None
		if db_id in self.__index:
			database = self.__index[db_id]
			#if database.application_id == owner_id:
		else:
			database = self.create_database(owner_id, db_id)
		return database
	
	def create_database(self, owner_id, id):
		"""Creation of new database"""
		database = VDOM_database_object(owner_id,id)
		self.__index[database.id] = database
		src.file_access.file_manager.create_database_directory(owner_id)
		src.storage.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"],self.__index)
		return database
	
	def create_from_xml(self, database, xml_data):
		"""Creation of database from xml representation"""
		src.file_access.file_manager.create_database_directory(database.owner_id)
		dom_db = parseString(xml_data)
		database.id = dom_db.firstChild.getAttribute("ID")
		database.name = dom_db.firstChild.getAttribute("Name")
		values = []
		for table in dom_db.firstChild.childNodes:
			if table.nodeType != Node.ELEMENT_NODE:
				continue
			tbl = VDOM_database_table(database.owner_id, database.id, table.getAttribute("id"), table.getAttribute("name"))
			field_list = ""		
			id_field = False
			for column in table.getElementsByTagName("header")[0].childNodes:
				if column.nodeType != Node.ELEMENT_NODE:
					continue
				if un_quote(column.getAttribute("name")) == "id":
					id_field = True
				declaration = "\'"+un_quote(column.getAttribute("name"))+"\'"
				type = column.getAttribute("type")
				if not type or type == "INTEGER" or type == "REAL" or type == "TEXT" or type == "BLOB":
					declaration += " "+ type
				if column.getAttribute("notnull") == "true":
					declaration += " NOT NULL"
				if column.getAttribute("primary") == "true":
					if column.getAttribute("autoincrement") == "true":
						declaration += " PRIMARY KEY AUTOINCREMENT"
					else:
						declaration += " PRIMARY KEY"
				if column.getAttribute("unique") == "true":
					declaration += " UNIQUE"
					
				if len(field_list):
					field_list += ", " + declaration
				else:
					field_list = declaration
			if not id_field:
				if field_list:
					field_list = "id INTEGER PRIMARY KEY AUTOINCREMENT, " + field_list
				else:
					field_list = "id INTEGER PRIMARY KEY AUTOINCREMENT"
			tbl.create("("+field_list+")")
			for row in table.getElementsByTagName("data")[0].childNodes:
				if row.nodeType != Node.ELEMENT_NODE:
					continue
				values = []
				for cell in row.childNodes:
					if cell.nodeType != Node.ELEMENT_NODE:
						continue
					if not cell.firstChild or cell.firstChild.nodeValue == "None":
						values.append(None)
					else:
						values.append(cell.firstChild.nodeValue)
				if values:
					tbl.addrow_from_list(values)
		database.get_connection().commit()
	
	def create_from_tar(self, database, xml_data):
		"""Creation of database from tar archive"""
		src.file_access.file_manager.create_database_directory("%s/%s"%(database.owner_id,database.id))
		src.file_access.file_manager.get_path(src.file_access.database,database.owner_id,database.id)
		
		
	def remove_databases(self):
		"""Clearing all databases"""
		src.file_access.file_manager.clear(src.file_access.database,None, None)
		self.__index = {}
		src.storage.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"],self.__index)
	
	def list_databases(self, owner_id):
		"""listing of all resources of application"""
		result = {}
		for key in self.__index:
			if self.__index[key].owner_id == owner_id:
				result[key] = self.__index[key].id
		return result
	
	def list_names(self, owner_id):
		"""listing of all resources of application"""
		result = {}
		for key in self.__index:
			if self.__index[key].owner_id == owner_id and self.__index[key].name:
				result[self.__index[key].name] = self.__index[key].id
		return result
	
	def delete_database(self,owner_id, db_id=None):
		"""Remove one or all databases of given owner"""
		remove_list = []
		database = None
		for key in self.__index:
			database = self.__index[key]
			if database.owner_id == owner_id and (db_id == None or db_id == database.id):
				remove_list.append(key)
		
		is_dirty_index = False
		for key in remove_list:
			self.__index.pop(key)
			is_dirty_index = True

		if is_dirty_index:
			src.storage.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"],self.__index)
		if db_id and database:
			src.file_access.file_manager.delete(src.file_access.database,owner_id,None,database.filename)
		else:
			src.file_access.file_manager.clear(src.file_access.database,owner_id, None)
	
	def save_index(self):
		"""Saving changes in database index to Storage"""
		src.storage.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"],self.__index)


internal_database_manager = VDOM_database_manager()
del VDOM_database_manager

def un_quote(param):
	"""Delete all quotes from param"""
	return param.replace("\'","").replace("\"","").replace("\\","")