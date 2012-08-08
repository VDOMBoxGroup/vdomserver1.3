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
from collections import OrderedDict
from wsgidav.dav_error import DAVError, HTTP_FORBIDDEN
from wsgidav.dav_provider import DAVProvider, DAVCollection, DAVNonCollection, _DAVResource
from wsgidav.property_manager import PropertyManager
from StringIO import StringIO

import wsgidav.util as util
import os
import mimetypes
import shutil
import stat
import managers
from webdav_request import VDOM_webdav_request
from webdav_cache import lru_cache
__docformat__ = "reStructuredText"

_logger = util.getModuleLogger(__name__)

BUFFER_SIZE = 8192

@lru_cache(maxsize=1000)
def get_properties(app_id, obj_id, path):
	props = managers.dispatcher.dispatch_action(app_id, obj_id, "getResourseProperties", "", """{"path": "%s"}""" % path)
	if props:
		return props


class VDOM_resource(_DAVResource):

	def __init__(self, path, isCollection, environ, app_id, obj_id):
		super(VDOM_resource, self).__init__(path, isCollection, environ)
		self._obj_id = obj_id
		self._app_id = app_id

	def _get_info(self, prop):
		properties = get_properties(self._app_id, self._obj_id, self.path)
		if properties:
			return properties.get(prop)

	def getContentLength(self):
		if self.isCollection:
			return None
		return self._get_info("getcontentlength")

	def getContentType(self):
		if self.isCollection:
			return None
		return self._get_info("getcontenttype")

	def getCreationDate(self):
		return self._get_info("creationdate")

	def getDirectoryInfo(self):
		"""Return a list of dictionaries with information for directory 
		rendering.

		This default implementation return None, so the dir browser will
		traverse all members. 

		This method COULD be implemented for collection resources.
		"""
		assert self.isCollection
		return None

	def getDisplayName(self):
		return self._get_info("dispayname") or self.name

	def getEtag(self):
		return self._get_info("getetag")

	def getLastModified(self):
		return self._get_info("getlastmodified")

	def supportRanges(self):
		return True

	def getContent(self):
		"""Open content as a stream for reading.

		See DAVResource.getContent()
		"""
		assert not self.isCollection
		func_name = "open"
		xml_data = """{"path": "%s", "mode": "rb"}""" % self.path
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			return ret
		return None

	def createEmptyResource(self, name):
		assert self.isCollection
		func_name = "createResource"

		xml_data = """{"path": "%s", "name": "%s"}""" % (self.path, name)
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			res = self.provider.getResourceInst(util.joinUri(self.path, name), self.environ)
			if res:
				return res

		raise DAVError(HTTP_FORBIDDEN)               

	def createCollection(self, name):
		assert self.isCollection
		func_name = "createCollection"
		xml_data = """{"path": "%s", "name": "%s"}""" % (self.path, name)
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			res = self.provider.getResourceInst(util.joinUri(self.path, name), self.environ)
			if res:
				return res
		raise DAVError(HTTP_FORBIDDEN)               


	def getMember(self, name):
		assert self.isCollection
		return self.provider.getResourceInst(util.joinUri(self.path, name), 
			                             self.environ)	
	
	def getMemberNames(self):
		assert self.isCollection
		memberNames = get_properties.get_children_names(self._app_id, self._obj_id, self.path)

		if not memberNames:
			func_name = "getMembers"
			xml_data = """{"path": "%s"}""" % self.path
			ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
			if ret:
				memberNames = list(ret.keys())
		return memberNames	

			

	def beginWrite(self, contentType=None):

		assert not self.isCollection
		func_name = "open"
		xml_data = """{"path": "%s", "mode": "wb"}""" % self.path
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			return ret
		raise DAVError(HTTP_FORBIDDEN)       


	def endWrite(self, withErrors):
		"""Called when PUT has finished writing.

		This is only a notification. that MAY be handled.
		"""
		func_name = "close"
		xml_data = """{"path": "%s"}""" % self.path
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		get_properties.invalidate(self._app_id, self._obj_id, os.path.normpath(util.getUriParent(self.path)))
		
	def handleDelete(self):
		if self.provider.readonly:
			raise DAVError(HTTP_FORBIDDEN) 
		func_name = "delete"
		xml_data = """{"path": "%s"}""" % self.path
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			#get_properties.invalidate(self._app_id, self._obj_id, os.path.normpath(util.getUriParent(self.path)))			
			return True

		raise DAVError(HTTP_FORBIDDEN)

	def handleCopy(self, destPath, depthInfinity):
		func_name = "copy"
		xml_data = """{"srcPath": "%s", "destPath": "%s"}""" % (self.path, destPath)
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			#get_properties.invalidate(self._app_id, self._obj_id, os.path.normpath(util.getUriParent(destPath)))
			return True

		raise DAVError(HTTP_FORBIDDEN)	

	def handleMove(self, destPath):
		func_name = "move"
		xml_data = """{"srcPath": "%s", "destPath": "%s"}""" % (self.path, destPath)
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			#get_properties.invalidate(self._app_id, self._obj_id, os.path.normpath(util.getUriParent(destPath)))		
			if util.getUriParent(destPath) != util.getUriParent(self.path):
				#get_properties.invalidate(self._app_id, self._obj_id, os.path.normpath(util.getUriParent(self.path)))
			return True

		raise DAVError(HTTP_FORBIDDEN)	


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
		#request = VDOM_webdav_request(environ)
		#managers.request_manager.current = request
		path = os.path.normpath(path)
		try:
			if self.__app and obj_id:
				res = get_properties(self.__app.id, obj_id, path)
				if res:
					isCollection = True if res["resourcetype"] == "Directory" else False
					return VDOM_resource(path, isCollection, environ, self.__app.id, obj_id)
				else:
					return None
		except:
			raise DAVError(HTTP_FORBIDDEN)
		return None

	def setPropManager(self, propManager):
		assert not propManager or hasattr(propManager, "copyProperties"), "Must be compatible with wsgidav.property_manager.PropertyManager"
		self.propManager1 = propManager
		self.propManager = PropertyManager()
		
class VDOM_webdav_manager(object):
	
	def invalidate(self, appid, objid, path):
		get_properties.invalidate(appid, objid, path)
		
	def clear(self):
		get_properties.clear()
		
	def change_property_value(self, app_id, obj_id, path, propname, value):
		get_properties.change_property_value(app_id, obj_id, path, propname, value)
		
	def change_parents_property(self, app_id, obj_id, path, propname, value):
		get_properties.change_parents_property(self, app_id, obj_id, path, propname, value)