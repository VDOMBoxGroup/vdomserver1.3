
import hashlib, xml.dom.minidom
import managers
from utils.remote_api import VDOM_service
from .. import errors
from ..subtypes import boolean, generic, string, true, false, v_empty


class whole_error(errors.generic):

	def __init__(self, message, line=None):
		errors.generic.__init__(self,
			message=u"WHOLE error: %s"%message,
			line=line)

class whole_connection_error(whole_error):

	def __init__(self, url, login, message, line=None):
		whole_error.__init__(self,
			message=u"Unable to connect to %s as %s (message)"%(url, login, message),
			line=line)

class whole_no_connection_error(whole_error):

	def __init__(self, line=None):
		whole_error.__init__(self,
			message=u"No connection are established",
			line=line)

class whole_remote_call_error(whole_error):

	def __init__(self, url, message, line=None):
		whole_error.__init__(self,
			message=u"Unable to make remote call to %s (%s)"%(url, message),
			line=line)

class whole_incorrect_response(whole_error):

	def __init__(self, line=None):
		whole_error.__init__(self,
			message=u"Incorrect response",
			line=line)

class whole_no_api_error(whole_error):

	def __init__(self, line=None):
		whole_error.__init__(self,
			message=u"Application has no API support",
			line=line)

class whole_no_application(whole_error):

	def __init__(self, line=None):
		whole_error.__init__(self,
			message=u"Application not found",
			line=line)


v_wholeerror=whole_error
v_wholeconnectionerror=whole_connection_error
v_wholenoconnectionerror=whole_no_connection_error
v_wholeremotecallerror=whole_remote_call_error
v_wholeincorrectresponse=whole_incorrect_response
v_wholenoapierror=whole_no_api_error
v_wholenoapplication=whole_no_application


def search_for_application_id(name, string):
	document, name=xml.dom.minidom.parseString(string.encode("utf-8")), name.lower()
	try:
		for application_node in document.getElementsByTagName("Applications")[0].getElementsByTagName("Application"):
			if u"".join(node.data for node in application_node.getElementsByTagName("Name")[0].childNodes if node.nodeType==node.TEXT_NODE).lower()==name:
				return u"".join(node.data for node in application_node.getElementsByTagName("Id")[0].childNodes \
					if node.nodeType==node.TEXT_NODE)
		return None
	except KeyError:
		raise whole_incorrect_response

def search_for_api_container(string):
	document=xml.dom.minidom.parseString(string.encode("utf-8"))
	try:
		for object_node in document.getElementsByTagName("Objects")[0].getElementsByTagName("Object"):
			if object_node.attributes["Name"].nodeValue.lower()=="api":
				return object_node.attributes["ID"].nodeValue
		return None
	except KeyError:
		raise whole_incorrect_response

def search_for_action_names(string):
	document=xml.dom.minidom.parseString(string.encode("utf-8"))
	try:
		return [action_node.attributes["Name"].nodeValue \
			for action_node in document.getElementsByTagName("ServerActions")[0].getElementsByTagName("Action")]
	except KeyError:
		raise whole_incorrect_response


class v_wholeapplication(generic):

	def __init__(self, url, service, application):
		self._url=url
		self._service=service
		self._application=application
		try:
			result=self._service.remote("get_top_objects", None, False)
		except Exception as error:
			raise whole_remote_call_error(self._url, error)
		self._container=search_for_api_container(result)
		if not self._container:
			raise whole_no_api_error


	def v_application(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("application")
		else:
			if not self._service:
				raise whole_no_connection_error
			return string(self._application)

	def v_container(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("container")
		else:
			return string(self._container) if self._container else v_empty

	def v_actions(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("actions")
		else:
			if not self._service:
				raise whole_no_connection_error
			try:
				result=self._service.remote("get_server_actions_list", [self._container], False)
			except Exception as error:
				raise whole_remote_call_error(self._url, error)
			names=search_for_action_names(result)
			return array([string(name) for name in names if name.lower()!="onload"])


	def v_invoke(self, name, *arguments):
		if not self._service:
			raise whole_no_connection_error
		try:
			if arguments:
				if len(arguments)==1:
					parameter=arguments[0].as_string
				else:
					parameter=[argument.as_string for argument in arguments]
			else:
				parameter=None
			result=self.service.call(self._container, name.as_string, parameter)
		except Exception as error:
			raise whole_remote_call_error(self._url, error)
		return string(result)


class v_wholeconnection(generic):
	
	def __init__(self):
		self._service=None


	def v_isconnected(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("isconnected")
		else:
			if not self._service: return boolean(false)
			try: self._service.remote("keep_alive", None, True)
			except: return boolean(false)
			return boolean(true)


	def v_open(self, url, login, password):
		self._url=url.as_string
		self._login=login.as_string
		self._password=hashlib.md5(password.as_string).hexdigest()
		try:
			self._service=VDOM_service.connect(self._url, self._login, self._password, None)
		except Exception as error:
			raise whole_connection_error(self._url, self._login, error)

	def v_close(self):
		self._service=None

	def v_applications(self, name, container=None, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("applications")
		else:
			if not self._service:
				raise whole_no_connection_error
			try:
				result=self._service.remote("list_applications", None, True)
			except Exception as error:
				raise whole_remote_call_error(self._url, error)
			application=search_for_application_id(name.as_string, result)
			if not application: raise whole_no_application
			try:
				service=VDOM_service.connect(self._url, self._login, self._password, application)
			except Exception as error:
				raise whole_connection_error(self._url, self._login, error)
			return v_wholeapplication(self._url, service, application)
