# (c) 2009-2011 Martin Wendt and contributors; see WsgiDAV http://wsgidav.googlecode.com/
# Original PyFileServer (c) 2005 Ho Chun Wei.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Implementation of a DAV provider that serves resource from a file system.

ReadOnlyFilesystemProvider implements a DAV resource provider that publishes 
a file system for read-only access.
Write attempts will raise HTTP_FORBIDDEN.

FilesystemProvider inherits from ReadOnlyFilesystemProvider and implements the
missing write access functionality. 

See `Developers info`_ for more information about the WsgiDAV architecture.

.. _`Developers info`: http://docs.wsgidav.googlecode.com/hg/html/develop.html  
"""
from wsgidav.dav_error import DAVError, HTTP_FORBIDDEN
from wsgidav.dav_provider import DAVProvider, DAVCollection, DAVNonCollection
from wsgidav.property_manager import PropertyManager
from StringIO import StringIO

import wsgidav.util as util
import os
import mimetypes
import shutil
import stat
import managers
from webdav_request import VDOM_webdav_request
__docformat__ = "reStructuredText"

_logger = util.getModuleLogger(__name__)

BUFFER_SIZE = 8192


#===============================================================================
# FileResource
#===============================================================================
class FileResource(DAVNonCollection):
	"""Represents a single existing DAV resource instance.

	See also _DAVResource, DAVNonCollection, and FilesystemProvider.
	"""
	def __init__(self, path, environ, app_id, obj_id):
		super(FileResource, self).__init__(path, environ)
		self._obj_id = obj_id
		self._app_id = app_id
		self._path = path

	# Getter methods for standard live properties     
	def getContentLength(self):
		return self.provider.propManager1.getProperty(self._path, "getcontentlenght")	
	
	def getContentType(self):
		return self.provider.propManager1.getProperty(self._path, "getcontenttype") or "application/octet-stream"
	
	def getCreationDate(self):
		return self.provider.propManager1.getProperty(self._path, "creationdate")
	
	def getDisplayName(self):
		return self.provider.propManager1.getProperty(self._path, "displayname") or self.name
	
	def getEtag(self):
		return self.provider.propManager1.getProperty(self._path, "getetag")
	
	def getLastModified(self):
		return self.provider.propManager1.getProperty(self._path, "getlastmodified")

	def supportRanges(self):
		return False

	def getContent(self):
		"""Open content as a stream for reading.

		See DAVResource.getContent()
		"""
		func_name = "getData"
		xml_data = {"path": self._path}
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			return ret
		return None

	def beginWrite(self, contentType=None):
		"""Open content as a stream for writing.

		This method MUST be implemented by all providers that support write 
		access.
		"""
		func_name = "open"
		xml_data = {"path": self._path}
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			return ret
		raise DAVError(HTTP_FORBIDDEN)       


	def endWrite(self, withErrors):
		"""Called when PUT has finished writing.

		This is only a notification. that MAY be handled.
		"""
		func_name = "close"
		xml_data = {"path": self._path}
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		self.provider.propManager1.update(self._path)

	def delete(self):
		"""Remove this resource or collection (recursive).

		See DAVResource.delete()
		"""
		if self.provider.readonly:
			raise DAVError(HTTP_FORBIDDEN) 
		func_name = "delete"
		xml_data = {"path": self._path}
		managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		self.provider.propManager1.removeProperties(self._path)


	def supportRecursiveMove(self, destPath):
		"""Return True, if moveRecursive() is available (see comments there)."""
		return True

	def moveRecursive(self, destPath):
		if self.provider.readonly:
			raise DAVError(HTTP_FORBIDDEN)
		assert not util.isEqualOrChildUri(self.path, destPath)
		func_name = "move"
		xml_data = {"srcPath": self._path, "destPath": destPath}
		res = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if self.provider.propManager1 and self.provider.propManager:
			self.provider.propManager1.moveProperties(self._path, destPath.rstrip("/"), 
			                                         withChildren=False)
			destRes = self.provider.getResourceInst(destPath, self.environ)
			self.provider.propManager.moveProperties(self._path, destRes.path, 
			                                         withChildren=True)

	def copyMoveSingle(self, destPath, isMove):
		"""See DAVResource.copyMoveSingle() """
		func_name = "move" if isMove else "copy"
		xml_data = {"srcPath": self._path, "destPath": destPath}
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			return ret
		raise DAVError(HTTP_FORBIDDEN)



#===============================================================================
# FolderResource
#===============================================================================
class FolderResource(DAVCollection):
	"""Represents a single existing file system folder DAV resource.

	See also _DAVResource, DAVCollection, and FilesystemProvider.
	"""
	def __init__(self, path, environ, app_id, obj_id):
		super(FolderResource, self).__init__(path, environ)
		self._obj_id = obj_id
		self._app_id = app_id
		self._path = path
		self._app = managers.xml_manager.get_application(app_id)
		self._object = self._app if not self._obj_id else self._app.search_object(self._obj_id)

	# Getter methods for standard live properties     
	def getDisplayName(self):
		return self.provider.propManager1.getProperty(self._path, "displayname") or self.name
	
	def getDirectoryInfo(self):
		return None
	
	def getEtag(self):
		return self.provider.propManager1.getProperty(self._path, "getetag")
	
	def getLastModified(self):
		return self.provider.propManager1.getProperty(self._path, "getlastmodified")

	def getMemberNames(self):
		"""Return list of direct collection member names (utf-8 encoded).

		See DAVCollection.getMemberNames()
		"""
		func_name = "getMembers"
		xml_data = {"path": self._path}
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			return ret
		return []



	def getMember(self, name):
		assert self.isCollection
		if util.joinUri(self.path, name) not in self.provider.propManager1.getAllProperties():
			self.provider.propManager1.sync()
		return self.provider.getResourceInst(util.joinUri(self.path, name), 
			                             self.environ)
	
	def supportRecursiveMove(self, destPath):
		"""Return True, if moveRecursive() is available (see comments there)."""
		return True

	def createEmptyResource(self, name):
		"""Create an empty (length-0) resource.
	
		See DAVResource.createEmptyResource()
		"""
		func_name = "createResource"
		xml_data = {"path": self._path, "name": name}
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			self.provider.propManager1.update(ret)
			return self.provider.getResourceInst(ret, self.environ)
		raise DAVError(HTTP_FORBIDDEN)



	def createCollection(self, name):
		"""Create a new collection as member of self.
	
		See DAVResource.createCollection()
		"""
		func_name = "createCollection"
		xml_data = {"path": self._path, "name": name}
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			self.provider.propManager1.update(ret)
			return self.provider.getResourceInst(ret, self.environ)
		raise DAVError(HTTP_FORBIDDEN)


	def delete(self):
		"""Remove this resource or collection (recursive).

		See DAVResource.delete()
		"""
		if self.provider.readonly:
			raise DAVError(HTTP_FORBIDDEN) 
		func_name = "delete"
		xml_data = {"path": self._path}
		managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		self.provider.propManager1.removeProperties(self._path)
		self.removeAllLocks(True)

	def copyMoveSingle(self, destPath, isMove):
		"""See DAVResource.copyMoveSingle() """
		func_name = "move" if isMove else "copy"
		xml_data = {"srcPath": self._path, "destPath": destPath}
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			return ret
		raise DAVError(HTTP_FORBIDDEN)


	def supportRecursiveMove(self, destPath):
		"""Return True, if moveRecursive() is available (see comments there)."""
		return True

	def moveRecursive(self, destPath):
		if self.provider.readonly:
			raise DAVError(HTTP_FORBIDDEN)
		assert not util.isEqualOrChildUri(self.path, destPath)
		func_name = "move"
		xml_data = {"srcPath": self._path, "destPath": destPath}
		managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if self.provider.propManager1 and self.provider.propManager:
			self.provider.propManager1.moveProperties(self._path, destPath.rstrip("/"), 
			                                         withChildren=True)
			destRes = self.provider.getResourceInst(destPath, self.environ)
			self.provider.propManager.moveProperties(self._path, destRes.getRefUrl(), 
			                                         withChildren=True)


#===============================================================================
# FilesystemProvider
#===============================================================================
class VDOM_Provider(DAVProvider):

	def __init__(self, rootFolderPath="", readonly=False):
		super(VDOM_Provider, self).__init__()
		self.rootFolderPath = rootFolderPath
		self.readonly = readonly


	def __repr__(self):
		rw = "Read-Write"
		if self.readonly:
			rw = "Read-Only"
		return "%s for WebDAV (%s)" % (self.__class__.__name__, rw)

	def _setApplication(self, host):

		vh = managers.virtual_hosts
		app_id = vh.get_site(host.lower())
		if not app_id:
			app_id = vh.get_def_site()
		self.__app = managers.xml_manager.get_application(app_id)


	def _getObjectId(self, path):
		pathInfoParts = path.strip("/").split("/")
		name = pathInfoParts[0]
		if not self.__app:
			return None

		try:        
			obj = self.__app.get_objects_by_name()[name.lower()]
			r  = util.toUnicode(obj.id) if obj else None
		except:
			r = ""
		return r


	def getResourceInst(self, path, environ):
		"""Return info dictionary for path.

		See DAVProvider.getResourceInst()
		"""
		self._count_getResourceInst += 1
		host = environ["HTTP_HOST"]
		host = host.split(":")[0]
		self._setApplication(host)
		obj_id = self._getObjectId(path)
		request = VDOM_webdav_request(environ)
		managers.request_manager.current = request
		path = path.rstrip("/")
		try:
			if self.__app and obj_id:
				if not self.propManager1.app_id and not self.propManager1.obj_id:
					self.propManager1.app_id = self.__app.id
					self.propManager1.obj_id = obj_id
				all_props = self.propManager1.getAllProperties()
				res = self.propManager1.getAllProperties().get(path, None)
				if res:
					if res["resourcetype"] == "Directory":
						return FolderResource(path, environ, self.__app.id, obj_id)
					else:
						return FileResource(path, environ, self.__app.id, obj_id)
				else:
					return None
		except:
			raise DAVError(HTTP_FORBIDDEN)
		return None
	
	def setPropManager(self, propManager):
		assert not propManager or hasattr(propManager, "copyProperties"), "Must be compatible with wsgidav.property_manager.PropertyManager"
		self.propManager1 = propManager
		self.propManager = PropertyManager()