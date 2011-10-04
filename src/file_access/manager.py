"""
File Manager - provides interface to file system for resource, py-cache and xml file managers
"""

import sys, os, traceback
import shutil, thread, time,types

import file_access
from utils.exception import VDOM_exception
from utils.semaphore import VDOM_semaphore
import utils.mutex as mutex
import base64
from daemon import VDOM_file_manager_writer


application_path = "applications"
global_types_path = "types"
type_source_path = "objects"
py_files_cache = "cache"
resources_path = "resources"
application_file_name = "app.xml"
databases_path = "databases"

class VDOM_file_manager(object):
	"""interface to os file system (singleton)"""

	def __init__(self):
		self.__queue = []
		self.__sem = VDOM_semaphore()
		self.__daemon=VDOM_file_manager_writer(self)
		self.__daemon.start()


	def work(self):
		if len(self.__queue) > 0:
			self.__sem.lock()
			while len(self.__queue) > 0:
				item = self.__queue.pop(0)
				fname = item[0]
				data = item[1]
#				self.write(fname, data)
				file = open(fname, "wb")
				if  type(content) == types.FileType or hasattr(content, "read"):
					shutil.copyfileobj(content, fh)
				else:
					file.write(data)
				file.close()
			self.__sem.unlock()


	def write_async(self, fname, data):
		self.__sem.lock()
		try:
			self.__queue.append((fname, data))
		except:
			self.__sem.unlock()
			return False
		self.__sem.unlock()
		return True

	### Public ###
	def exists(self, restype, application_id, object_id, file_name ):
		"""Checks if object exists"""
		if object_id:
			dirpath = self.__get_path( restype, object_id,file_name)
		else:
			dirpath = self.__get_path( restype, application_id, file_name)
		return os.path.exists( dirpath )

	def size(self, restype, application_id, object_id, file_name ):
		"""Checks if object exists"""
		if object_id:
			dirpath = self.__get_path( restype, object_id,file_name)
		else:
			dirpath = self.__get_path( restype, application_id, file_name)
		return os.path.getsize( dirpath )

	
	def write(self, restype, application_id, object_id, file_name, content, encode = False, async = False):
		"""Writes <content> to object file"""
		if object_id:
			dirpath = self.__get_path( restype, object_id,"")
		else:
			dirpath = self.__get_path( restype, application_id, "")
		if not os.path.isdir(dirpath) and restype in \
		        (file_access.type_source, file_access.resource, file_access.database, file_access.storage):
			try:
				os.makedirs(dirpath)
			except: pass
		if object_id:
			path = self.__get_path( restype, object_id, file_name )
		else:
			path = self.__get_path( restype, application_id, file_name )			
		mut = mutex.VDOM_named_mutex(path)
		mut.lock()
		try:
			if encode:
				content = content.encode("utf-8")
			if async:
				ret = self.write_async(path, content)
			else:
				fh = open(path, "wb")
				if  type(content) == types.FileType or hasattr(content, "read"):
					shutil.copyfileobj(content, fh)
				else:
					fh.write(content)
				fh.close()
		except:
			raise
			#raise VDOM_exception(_("Can't write file %s") % path)
		finally:
			mut.unlock()

	def write_file(self, fname, fdata):
		"""general file write"""
		file = open(fname, "wb")
		file.write(fdata.encode("utf-8"))
		file.close()

	def listtypedir(self):
		"""get type directory listing"""
		try:
			directory = VDOM_CONFIG["TYPES-LOCATION"]
			r1 = os.listdir(directory)
			r2 = []
			for item in r1:
				if item.endswith(".xml"):
					r2.append(os.path.join(directory, item))
			return r2
#		except:
		except Exception, e:
			traceback.print_exc(file=sys.stderr)
			return []
		
	def read_file(self, fname):#Not used! Remove?
		"""general file read"""
		file = open(fname, "rb")
		fdata = file.read()
		file.close()
		return fdata

	def delete(self, restype, application_id, object_id, file_name):
		"""Deletes file"""
		if object_id:
			path = self.__get_path( restype, object_id, file_name )
		else:
			path = self.__get_path( restype, application_id, file_name )
		mut = mutex.VDOM_named_mutex(path)
		mut.lock()
		try:
			os.remove( path )
		except: pass
		mut.unlock()

	def read(self, restype, application_id, object_id, file_name):
		"""Returns content of file"""
		if object_id:
			fh = open( self.__get_path( restype, object_id, file_name ), "rb" )
		else:
			fh = open( self.__get_path( restype, application_id, file_name ), "rb" )
		
		content = ""
		while 1:
			buf = fh.read()
			if not buf:
				break
			content += buf
		fh.close()
		return content
	
	def get_fd(self, restype, application_id, object_id, file_name):
		"""Returns file descriptor"""
		if object_id:
			fh = open( self.__get_path( restype, object_id, file_name ), "rb" )
		else:
			fh = open( self.__get_path( restype, application_id, file_name ), "rb" )
		
		return fh
	
	def compute_crc(self, restype, application_id, object_id, file_name):
		"""Returns CRC of file"""
		"""STUB"""
		
		return None

	def copy(self, source_fname, restype, application_id, file_name):
		"""Copy <source_fname> file to object file"""
		shutil.copy(source_fname, self.__get_path( restype, application_id, None, file_name ) )

	def create_application_skell(self, application_id ):
		"""Copy <source_fname> file to object file"""
		try: os.makedirs(self.__get_path(file_access.cache, application_id, ""))
		except: pass

	def create_type_directory(self, type_id):
		"""create directory to store type data"""
		path = os.path.join( VDOM_CONFIG["FILE-ACCESS-DIRECTORY"],
								type_source_path,
								type_id)
		try:
			os.makedirs(path)
		except: pass

	def create_app_res_directory(self, app_id):
		"""create directory to store app resources"""
		path = os.path.join( VDOM_CONFIG["FILE-ACCESS-DIRECTORY"],
								application_path,
								app_id,
								resources_path)
		try:
			os.makedirs(path)
		except: pass

	def create_database_directory(self, owner_id):
		"""create directory to store app databases"""
		path = os.path.join( VDOM_CONFIG["FILE-ACCESS-DIRECTORY"],
								databases_path,
								owner_id)
		try:
			os.makedirs(path)
		except: pass
		
	def create_app_storage_user_directory(self, application_id,folder_name):
		"""create directory to store app databases"""
		path = self.__get_app_storage_file_path(application_id, folder_name )
		try:
			os.makedirs(path)
		except: pass
		
	def delete_app_storage_user_directory(self, application_id,folder_name):
		"""create directory to store app databases"""
		path = self.__get_app_storage_file_path(application_id, folder_name )
		try:
			shutil.rmtree(path)
		except: pass
		
	def clear(self, restype, application_id, object_id):
		"""Deletes all files of type"""
		if object_id:
			path = self.__get_path(restype, object_id, "")
		else:
			path = self.__get_path(restype, application_id, "")
		if os.path.exists(path):
			shutil.rmtree(path,True)
			if restype != file_access.resource :
				try:
					os.makedirs(path)
				except: pass

	def get_path(self, restype, application_id, object_id, object_name ):
		"""Public version of method (for testing)"""
		if object_id:
			return self.__get_path( restype, object_id, object_name )
		else:
			return self.__get_path( restype, application_id, object_name )

	def create_lib_path(self, appid):
		thepath = os.path.join(VDOM_CONFIG["LIB-DIRECTORY"], appid)
		try:
			os.makedirs(thepath)
		except:
			pass
		f = open(os.path.join(thepath, "__init__.py"), "wt")
		f.close()

	def delete_libs(self, appid):
		shutil.rmtree(os.path.join(VDOM_CONFIG["LIB-DIRECTORY"],appid), ignore_errors = True)

	def write_lib(self, appid, libname, data):
		fname = os.path.join(VDOM_CONFIG["LIB-DIRECTORY"],appid, libname + ".py")
		self.write_file(fname, "# coding=utf-8\n\n" + data)

	def delete_lib(self, appid, libname):
		fname = os.path.join(VDOM_CONFIG["LIB-DIRECTORY"],appid, libname + ".py")
		try:
			os.remove(fname)
		except:
			pass
		try:
			os.remove(fname + "c")
		except:
			pass

### Private ###
	def __get_path(self, restype, owner_id, object_name ):
		"""private method: returns path to object according to type of request"""
		if( restype == file_access.application_xml ):
			return self.__get_application_file_path( owner_id )
		
		elif( restype == file_access.global_type ):
			return self.__get_global_type_file_path( object_name )
		
		elif( restype == file_access.cache ):
			return self.__get_py_chache_file_path( owner_id, object_name )
		
		elif( restype == file_access.resource ):
			return self.__get_resource_file_path( owner_id, object_name )

		elif( restype == file_access.type_source ):
			return self.__get_native_type_source_file_path(owner_id, object_name )
		
		elif( restype == file_access.database ):
			return self.__get_database_file_path(owner_id, object_name )
		
		elif( restype == file_access.storage ):
			return self.__get_app_storage_file_path(owner_id, object_name )
		
	def __get_application_file_path( self, application_id ):
		"""return path to appl.xml. Input: application_id: string"""
		return os.path.join( VDOM_CONFIG[ "FILE-ACCESS-DIRECTORY" ],
								application_path,
								application_id,
								application_file_name)

		
	def __get_global_type_file_path(self, object_name):
		"""return path to global type difinition (usualy xml-file). Input: object_name: string"""
		return os.path.join( VDOM_CONFIG[ "FILE-ACCESS-DIRECTORY" ],
								global_types_path,
								object_name )



	def __get_py_chache_file_path(self, application_id, object_name):
		"""return path to py-file. Input: application_id: string, object_name: string"""
		return os.path.join( VDOM_CONFIG[ "FILE-ACCESS-DIRECTORY" ],
								application_path,
								application_id,
								py_files_cache,
								object_name  )



	def __get_resource_file_path(self, owner_id, object_name):
		"""return path to resource. Input: owner_id: string, object_name: string"""
		if owner_id:
			return os.path.join( VDOM_CONFIG[ "FILE-ACCESS-DIRECTORY" ],
								resources_path,
								owner_id,
								object_name)
		else:
			return os.path.join( VDOM_CONFIG[ "FILE-ACCESS-DIRECTORY" ], resources_path)
			

	def __get_native_type_source_file_path(self, type_id, object_name):
		"""return path to native type source file (xml-file). Input: type_id: string, object_name: string"""
		return os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"],
								type_source_path,
								object_name)

	def __get_database_file_path(self, owner_id="", object_name=""):
		"""return path to database file (sqlite3-file). Input: owner_id: string, object_name: string"""
		if owner_id:
			return os.path.join(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"],
								databases_path,
								owner_id,
								object_name)
		else:
			return os.path.join( VDOM_CONFIG[ "FILE-ACCESS-DIRECTORY" ], databases_path)

		
	def __get_app_storage_file_path(self, application_id="", file_name=""):
		"""return path to app storage files. Input: owner_id: string, object_name: string"""
		if file_name:
			#object_name = base64.b64encode(file_name,"_!")
			return os.path.join(VDOM_CONFIG["FILE-STORAGE-DIRECTORY"],application_id,file_name)
		else:
			return os.path.join(VDOM_CONFIG["FILE-STORAGE-DIRECTORY"],application_id)
