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
		self._live_props = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, "getResourseProperties", "",{"path": self._path})

	# Getter methods for standard live properties     
	def getContentLength(self):
		if self._live_props and "getcontentlenght" in self._live_props:
			return self._live_props["getcontentlenght"]
		return 0
	
	def getContentType(self):
		if self._live_props and "getcontenttype" in self._live_props:
			return self._live_props["getcontenttype"]
		return "application/octet-stream"
	
	def getCreationDate(self):
		if self._live_props and "creationdate" in self._live_props:
			return self._live_props["creationdate"]
		return None
	
	def getDisplayName(self):
		if self._live_props and "displayname" in self._live_props:
			return self._live_props["displayname"]
		return self.name
	
	def getEtag(self):
		if self._live_props and "getetag" in self._live_props:
			return self._live_props["getetag"]
		return None
	
	def getLastModified(self):
		if self._live_props and "getlastmodified" in self._live_props:
			return self._live_props["getlastmodified"]
		return None
	
	def supportEtag(self):
		if self._live_props and "getetag" in self._live_props:
			return True
		return False

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

	def delete(self):
		"""Remove this resource or collection (recursive).

		See DAVResource.delete()
		"""
		if self.provider.readonly:
			raise DAVError(HTTP_FORBIDDEN) 
		func_name = "delete"
		xml_data = {"path": self._path}
		managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)


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
		if self.provider.propManager:
			destRes = self.provider.getResourceInst(destPath, self.environ)
			self.provider.propManager.moveProperties(self.getRefUrl(), destRes.getRefUrl(), 
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
		self._live_props = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, "getResourseProperties", "",{"path": self._path})

	# Getter methods for standard live properties     
	def getDisplayName(self):
		if self._live_props and "displayname" in self._live_props:
			return self._live_props["displayname"]
		return self.name
	
	def getDirectoryInfo(self):
		return None
	
	def getEtag(self):
		if self._live_props and "getetag" in self._live_props:
			return self._live_props["getetag"]
		return None
	
	def getLastModified(self):
		if self._live_props and "getlastmodified" in self._live_props:
			return self._live_props["getlastmodified"]
		return None

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
		self.removeAllProperties(True)
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
		if self.provider.propManager:
			destRes = self.provider.getResourceInst(destPath, self.environ)
			self.provider.propManager.moveProperties(self.getRefUrl(), destRes.getRefUrl(), 
			                                         withChildren=True)

	def moveRecursive(self, destPath):
		if self.provider.readonly:
			raise DAVError(HTTP_FORBIDDEN)
		assert not util.isEqualOrChildUri(self.path, destPath)
		func_name = "move"
		xml_data = {"srcPath": self._path, "destPath": destPath}
		managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if self.provider.propManager:
			destRes = self.provider.getResourceInst(destPath, self.environ)
			self.provider.propManager.moveProperties(self.getRefUrl(), destRes.getRefUrl(), 
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
		try:
			if self.__app and obj_id:
				func_name = "isExists"
				xml_data = {"path":path}
				ret = managers.dispatcher.dispatch_action(self.__app.id, obj_id, func_name, "",xml_data)
				if ret:
					func_name = "isCollection"
					xml_data = {"path":path}
					ret = managers.dispatcher.dispatch_action(self.__app.id, obj_id, func_name, "",xml_data)
					if ret:
						return FolderResource(path, environ, self.__app.id, obj_id)
					else:
						return FileResource(path, environ, self.__app.id, obj_id)
				else:
					return None
		except:
			raise DAVError(HTTP_FORBIDDEN)
		return None