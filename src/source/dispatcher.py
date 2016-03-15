"""
Dispatcher manager
"""
import SOAPpy

import managers
from soap.errors import *
import utils
from utils.exception import *


class VDOM_dispatcher:
	"""handler manager class"""
	def __init__(self):
		"""constructor"""
		self.__handler_index = {}
		self.__remote_index = {}
	
	def add_handler(self, type_id, func_name):
		"""Adding new handler"""
		if not  type_id in self.__handler_index:
			self.__handler_index[type_id] = []
		self.__handler_index[type_id].append(func_name)
	
	def add_remote_method(self, type_id, func_name):
		"""Adding new handler"""
		if not  type_id in self.__remote_index:
			self.__remote_index[type_id] = []
		self.__remote_index[type_id].append(func_name)
	
	def dispatch_handler(self, app_id, object_id, func_name, param):
		"""Processing handler"""
		try:
			object = managers.xml_manager.search_object(app_id, object_id)
			if object and object.type.id in self.__handler_index and func_name in self.__handler_index[object.type.id]:
				module=__import__(utils.id.guid2mod(object.type.id))
				if func_name in module.__dict__:
					return getattr(module, func_name)(app_id, object_id, param)
		except Exception, e:
			raise VDOM_exception_handler(str(e), func_name)
		#raise VDOM_exception(_("Handler not found"))
	
	def dispatch_remote(self, app_id, object_id, func_name, xml_param, session_id=None):
		"""Processing remote methods call"""
		try:
			object = managers.xml_manager.search_object(app_id, object_id)
			if object.type.id in self.__remote_index and func_name in self.__remote_index[object.type.id]:
				module=__import__(utils.id.guid2mod(object.type.id))
				if func_name in module.__dict__:
					if session_id:
						return getattr(module, func_name)(app_id, object_id, xml_param,session_id)
					else:
						return getattr(module, func_name)(app_id, object_id, xml_param)
		except Exception, e:
			if getattr(e, "message", None) and isinstance(e.message, unicode):
				msg = unicode(e).encode("utf8")
			else:
				msg = str(e)
			
			raise SOAPpy.faultType(remote_method_call_error, _("Remote method call error"), msg)
			#return "<Error><![CDATA[%s]]></Error>"%str(e)
		raise SOAPpy.faultType(remote_method_call_error, _("Handler not found"), str(func_name))
		#return "<Error><![CDATA[Handler not found]]></Error>"
		
	def dispatch_action(self, app_id, object_id, func_name,xml_param,xml_data):
		"""Processing action call"""
		try:
			request = managers.request_manager.get_request()
			request.arguments().arguments({"xml_param":[xml_param],"xml_data":[xml_data]})
			app = managers.xml_manager.get_application(app_id)
			obj = app.search_object(object_id)
			if not obj:
				raise Exception("Container id:%s not found"%object_id)
			request.container_id = object_id
			managers.engine.execute(app, obj, None, func_name, True)
			ret = request.session().value("response")
			request.session().remove("response")
			return ret or ""
		except Exception, e:
			if getattr(e, "message", None) and isinstance(e.message, unicode):
				msg = unicode(e).encode("utf8")
			else:
				msg = str(e)
			raise SOAPpy.faultType(remote_method_call_error, _("Action call error"), msg)
		
		raise SOAPpy.faultType(remote_method_call_error, _("Handler not found"), str(func_name))
