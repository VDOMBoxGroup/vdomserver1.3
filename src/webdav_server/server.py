import request_server
from wsgidav.wsgidav_app import DEFAULT_CONFIG
try:
	from wsgidav.wsgidav_app import WsgiDAVApp
except ImportError, e:
	raise RuntimeError("Could not import wsgidav package:\n%s\nSee http://wsgidav.googlecode.com/." % e)
from wsgidav.lock_storage import LockStorageDict
from wsgidav.property_manager import PropertyManager
from wsgidav.lock_manager import LockManager
from vdom_dav_provider import VDOM_Provider
from domain_controller import VDOM_domain_controller
from vdom_dav_provider import get_properties
import managers

class VDOM_webdav_manager(object):
		
	def __init__(self):
		self.__config = DEFAULT_CONFIG.copy()
		self.__config.update({"host": VDOM_CONFIG["SERVER-ADDRESS"],
		                      "port": VDOM_CONFIG["SERVER-DAV-PORT"],
		                      "propsmanager": True,
		                      "provider_mapping": {},
		                      "acceptbasic": True,      # Allow basic authentication, True or False
		                      "acceptdigest": False,     # Allow digest authentication, True or False
		                      "defaultdigest": False,
		                      "verbose": 0,
		                      })			
		self.__index = {}
		app_list = managers.xml_manager.get_applications()
		for appid in app_list:
			self.load_webdav(appid)
			
	def load_webdav(self, appid):
		start_dav = False		
		__conf = self.__config.copy()
		__conf["domaincontroller"] = VDOM_domain_controller(appid)		
		app = managers.xml_manager.get_application(appid)
		for obj in app.get_objects_list():
			if obj.type.id == '1a43b186-5c83-92fa-7a7f-5b6c252df941':
				__conf["provider_mapping"]["/"+obj.name.encode('utf8')] = VDOM_Provider(appid, obj.id)
				if not self.__index.get(appid):
					self.__index[appid] = {obj.id : '/'+obj.name}
				else:
					self.__index[appid][obj.id] = "/"+obj.name
				start_dav = True
							
		if start_dav: app.wsgidav_app = WsgiDAVApp(__conf)
		
	def add_webdav(self, appid, objid, sharePath):
		app = managers.xml_manager.get_application(appid)
		__conf = {}
		if not hasattr(app, "wsgidav_app"):
			__conf = self.__config.copy()
			__conf["domaincontroller"] = VDOM_domain_controller(appid)
			__conf["provider_mapping"][sharePath.encode('utf8')] = VDOM_Provider(appid, objid)
			app.wsgidav_app = WsgiDAVApp(__conf)
		else:
			provider = VDOM_Provider(appid, objid)
			provider.setSharePath(sharePath.encode('utf8'))
			provider.setLockManager(LockManager(LockStorageDict()))
			provider.setPropManager(PropertyManager())
			app.wsgidav_app.providerMap[sharePath.encode('utf8')] = provider
		#self.__index[appid][objid] = sharePath
		if not self.__index.get(appid):
			self.__index[appid] = {objid : sharePath}
		else:
			self.__index[appid][objid] = sharePath
			
	def del_webdav(self, appid, objid, sharePath):
		app = managers.xml_manager.get_application(appid)
		if hasattr(app, "wsgidav_app"):
			if sharePath.encode('utf8') in app.wsgidav_app.providerMap:
				del app.wsgidav_app.providerMap[sharePath.encode('utf8')]
				del self.__index[appid][objid]
				if len(self.__index[appid]) == 0: del self.__index[appid]
				
	def del_all_webdav(self, appid):
		app = managers.xml_manager.get_application(appid)
		if hasattr(app, "wsgidav_app"):	
			delattr(app, 'wsgidav_app')
		if appid in self.__index:
			del self.__index[appid]
				
	def get_webdav_share_path(self, appid, objid):
		if appid in self.__index:
			return self.__index[appid].get(objid, None)
		return None
					
	def add_to_cache(self, appid, objid, path):
		if isinstance(path, unicode):
			try:
				utf8path = path.encode('utf8')
				path = utf8path
			except Exception, e:
				debug("Error: " + unicode(e))
		get_properties(appid, objid, path)
		
	def invalidate(self, appid, objid, path):
		get_properties.invalidate(appid, objid, path)
		
	def clear(self):
		get_properties.clear()
		
	def change_property_value(self, app_id, obj_id, path, propname, value):
		get_properties.change_property_value(app_id, obj_id, path, propname, value)
		
	def change_parents_property(self, app_id, obj_id, path, propname, value):
		get_properties.change_parents_property(self, app_id, obj_id, path, propname, value)	