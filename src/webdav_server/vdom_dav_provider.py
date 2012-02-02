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
        self._app = managers.xml_manager.get_application(app_id)
        self._object = self._app if not self._obj_id else self._app.search_object(self._obj_id)
#        self._dict = None
        
        # Setting the name from the file path should fix the case on Windows
        
        self.name = self._object.name + ".xml" if self._obj_id else ""
            
        self.name = self.name.encode("utf8")

    # Getter methods for standard live properties     
    def getContentLength(self):
        return len(self._object.xml_obj.toxml())
    def getContentType(self):
        mimetype = "text/xml" 
        return mimetype
    def getCreationDate(self):
        return None
    def getDisplayName(self):
        return self.name
    def getEtag(self):
        return None
    def getLastModified(self):
        return None
    def supportEtag(self):
        return False
    def supportRanges(self):
        return False
    
    def getContent(self):
        """Open content as a stream for reading.
         
        See DAVResource.getContent()
        """
        assert not self.isCollection
        # issue 28: if we open in text mode, \r\n is converted to one byte.
        # So the file size reported by Windows differs from len(..), thus
        # content-length will be wrong. 
#        mime = self.getContentType()
#        if mime.startswith("text"):
#            return file(self._filePath, "r", BUFFER_SIZE)
        
        
        return StringIO(self._object.xml_obj.toxml())
   

    
               


    
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
        self._app = managers.xml_manager.get_application(app_id)
        self._object = self._app if not self._obj_id else self._app.search_object(self._obj_id)
#        self._dict = None
        
        # Setting the name from the file path should fix the case on Windows
        
        self.name = self._object.name if self._obj_id else ""
            
        self.name = self.name.encode("utf8")
        

    # Getter methods for standard live properties     
    def getDisplayName(self):
        name = self.name
        
        return name
    def getDirectoryInfo(self):
        return None
    def getEtag(self):
        return None
    def getLastModified(self):
        return None

    def getMemberNames(self):
        """Return list of direct collection member names (utf-8 encoded).
        
        See DAVCollection.getMemberNames()
        """
        # On Windows NT/2k/XP and Unix, if path is a Unicode object, the result 
        # will be a list of Unicode objects. 
        # Undecodable filenames will still be returned as string objects    
        # If we don't request unicode, for example Vista may return a '?' 
        # instead of a special character. The name would then be unusable to
        # build a distinct URL that references this resource.

        nameList = []
        # self._filePath is unicode, so os.listdir returns unicode as well
        #assert isinstance(self._filePath, unicode) 
        for name in self._object.objects:
            if not self._object.objects[name].objects:
                name = self._object.objects[name].name + ".xml"
            else:
                name = self._object.objects[name].name
            
            name = name.encode("utf8")
            nameList.append(name)
        return nameList

    def getMember(self, name):
        """Return direct collection member (DAVResource or derived).
        
        See DAVCollection.getMember()
        """
        path = util.joinUri(self.path, name)
        name = name.split(".")[0]
        obj = self._object.get_objects_by_name()[name]
        if obj.objects:
            res = FolderResource(path, self.environ, self._app.id, obj.id)
        else:
            res = FileResource(path, self.environ, self._app.id, obj.id)
        return res



    # --- Read / write ---------------------------------------------------------
    
    
               


    
#===============================================================================
# FilesystemProvider
#===============================================================================
class VDOM_Provider(DAVProvider):

    def __init__(self, rootFolderPath, readonly=False):
        if not rootFolderPath or not managers.xml_manager.get_application(rootFolderPath):
            raise ValueError("Application %s does not exists" % rootFolderPath)
        super(VDOM_Provider, self).__init__()
        self.rootFolderPath = rootFolderPath
        self.readonly = readonly

        
    def __repr__(self):
        rw = "Read-Write"
        if self.readonly:
            rw = "Read-Only"
        return "%s for application '%s' (%s)" % (self.__class__.__name__, 
                                          self.rootFolderPath, rw)


    def _locToFilePath(self, path):
        """Convert resource path to a unicode absolute file path."""
        assert self.rootFolderPath is not None
        pathInfoParts = path.strip("/").split("/")
        
        r = os.path.abspath(os.path.join(self.rootFolderPath, *pathInfoParts))
        if not r.startswith(self.rootFolderPath):
            raise RuntimeError("Security exception: tried to access file outside root.")
        r = util.toUnicode(r)
#        print "_locToFilePath(%s): %s" % (path, r)
        return r  

    def _getObjectId(self, path):
        assert self.rootFolderPath is not None
        pathInfoParts = path.strip("/").split("/")
        r = pathInfoParts[-1].split(".")[0]
        app = managers.xml_manager.get_application(self.rootFolderPath)
        if not r:
            r = self.rootFolderPath
        else:
            objects = app.get_all_objects()
            for o in objects:
                if r == app.search_object(o).name:
                    r = app.search_object(o).id
                    break
        r = util.toUnicode(r)
        return r
            
    
    def getResourceInst(self, path, environ):
        """Return info dictionary for path.

        See DAVProvider.getResourceInst()
        """
        self._count_getResourceInst += 1
        obj_id = self._getObjectId(path)
        if not obj_id:
            return None
        obj = managers.xml_manager.search_object(self.rootFolderPath, obj_id)
        if obj:
            if not obj.objects:
                return FileResource(path, environ, self.rootFolderPath, obj.id)
        else:
            obj_id = None
        return FolderResource(path, environ, self.rootFolderPath, obj_id)
        
