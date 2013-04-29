import managers
import wsgidav.util as util
from webdav_request import VDOM_webdav_request
from wsgidav.dav_error import DAVError, HTTP_FORBIDDEN

class VDOM_domain_controller(object):
	
	def __init__(self, appid):
		
		try:
			self._application = managers.xml_manager.get_application(appid) 
		except:
			self._application = None
			
	def getDomainRealm(self, inputRelativeURL, environ):
		davProvider = environ["wsgidav.provider"]
		if not davProvider:
			if environ["wsgidav.verbose"] >= 2:
				print >>sys.stdout, "getDomainRealm(%s): '%s'" %(inputURL, None)
			return None
		obj_name = davProvider.sharePath.strip("/")
		if obj_name == "":
			return None
		obj = self._application.search_objects_by_name(obj_name)[0]
			
		return obj.id

	def requireAuthentication(self, realmname, environ):
		return True

	def isRealmUser(self, realmname, username, environ):
		return True

	def getRealmUserPassword(self, realmname, username, environ):
		return ""

	def authDomainUser(self, realmname, username, password, environ):
		#request = VDOM_webdav_request(environ)
		#managers.request_manager.current = request
		
		path = environ["PATH_INFO"]
		obj_id = realmname
		func_name = "authentication"

		xml_data = """{"path": "%s",
		            "user": "%s",
		            "password": "%s"}""" % (path, username, password)
		try:
			ret = managers.dispatcher.dispatch_action(self._application.id, obj_id, func_name, "",xml_data)
		except:
			raise DAVError(HTTP_FORBIDDEN)
		if ret:
			return ret
		return False

#	def _get_app(self, host):
#
#		vh = managers.virtual_hosts
#		app_id = vh.get_site(host.lower())
#		if not app_id:
#			app_id = vh.get_def_site()
#		return managers.xml_manager.get_application(app_id)

#	def _get_object_id(self, path, app):
#		pathInfoParts = path.strip("/").split("/")
#		name = pathInfoParts[0]
#		if not app:
#			return None
#		try:        
#			obj = app.get_objects_by_name()[name.lower()]
#			r  = util.toUnicode(obj.id) if obj else None
#		except:
#			r = ""
#		return r