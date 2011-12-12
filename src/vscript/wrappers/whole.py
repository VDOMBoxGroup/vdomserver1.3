
import hashlib, xml.dom.minidom
import managers
from utils.remote_api import VDOM_service
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *
from ..exceptions import v_scripterror


class whole_error(v_scripterror):

	def __init__(self, message, line=None):
		v_scripterror.__init__(self,
			message=u"WHOLE error: %s"%message,
			line=line)

class whole_connection_error(whole_error):

	def __init__(self, url, login, line=None):
		whole_error.__init__(self,
			message=u"Unable to connect to %s as %s"%(url, login),
			line=line)

class whole_no_connection_error(whole_error):

	def __init__(self, line=None):
		whole_error.__init__(self,
			message=u"No connection are established",
			line=line)

class whole_remote_call_error(whole_error):

	def __init__(self, url, line=None):
		whole_error.__init__(self,
			message=u"Unable to make remote call to %s"%url,
			line=line)

class whole_incorrect_response(whole_error):

	def __init__(self, line=None):
		whole_error.__init__(self,
			message=u"Incorrect response",
			line=line)

class whole_no_api_error(whole_error):

	def __init__(self, application, line=None):
		whole_error.__init__(self,
			message=u"Application %s has no API support"%application,
			line=line)

class whole_no_application(whole_error):

	def __init__(self, application, line=None):
		whole_error.__init__(self,
			message=u"Application %s not found"%application,
			line=line)


v_wholeerror=whole_error
v_wholeconnectionerror=whole_connection_error
v_wholenoconnectionerror=whole_no_connection_error
v_wholeremotecallerror=whole_remote_call_error
v_wholeincorrectresponse=whole_incorrect_response
v_wholenoapierror=whole_no_api_error
v_wholenoapplication=whole_no_application


def search_for_application_id(name, string):
	document, name=xml.dom.minidom.parseString(string), name.lower()
	try:
		for application_node in document.getElementsByTagName("Applications")[0].getElementsByTagName("Application"):
			if u"".join(node.data for node in application_node.getElementsByTagName("Name")[0].childNodes if node.nodeType==node.TEXT_NODE).lower()==name:
				return u"".join(node.data for node in application_node.getElementsByTagName("Id")[0].childNodes \
					if node.nodeType==node.TEXT_NODE)
		raise whole_no_application(string)
	except KeyError:
		raise whole_incorrect_response

def search_for_api_container(string):
	document=xml.dom.minidom.parseString(string)
	try:
		for object_node in document.getElementsByTagName("Objects")[0].getElementsByTagName("Object"):
			if object_node.attributes["Name"].nodeValue.lower()=="api":
				return object_node.attributes["ID"].nodeValue
		raise whole_no_api_error(string)
	except KeyError:
		raise whole_incorrect_response

def search_for_action_names(string):
	document=xml.dom.minidom.parseString(string)
	try:
		return [action_node.attributes["Name"].nodeValue \
			for action_node in document.getElementsByTagName("ServerActions")[0].getElementsByTagName("Action")]
	except KeyError:
		raise whole_incorrect_response


class v_wholeapplication(generic):

	def __init__(self, url, service):
		self.url=url
		self.service=service
		try:
			result=self.service.remote("get_top_objects", None, False)
		except:
			raise whole_remote_call_error(self.url)
		self.container=search_for_api_container(result)

	def v_methods(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("application")
		else:
			if not self.service:
				raise whole_no_connection_error
			try:
				result=self.service.remote("get_server_actions_list", [self.container], False)
			except:
				raise whole_remote_call_error(self.url)
			names=search_for_action_names(result)
			return array(values=[string(name) for name in names if name.lower()!="onload"])

	def v_invoke(self, name, *arguments):
		if not self.service:
			raise whole_no_connection_error
		try:
			result=self.service.call(self.container, as_string(name), [as_string(argument) for argument in arguments])
		except:
			raise whole_remote_call_error(self.url)
		return string(result)

class v_wholeconnection(generic):
	
	def __init__(self):
		self.service=None

	def v_open(self, url, login, password):
		self.url=as_string(url)
		self.login=as_string(login)
		self.password=hashlib.md5(as_string(password)).hexdigest()
		try:
			self.service=VDOM_service.connect(self.url, self.login, self.password, None)
		except:
			raise whole_connection_error(self.url, self.login)

	def v_close(self):
		self.service=None

	def v_applications(self, name, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("application")
		else:
			if not self.service:
				raise whole_no_connection_error
			try:
				result=self.service.remote("list_applications", None, True)
			except:
				raise whole_remote_call_error(self.url)
			application=search_for_application_id(as_string(name), result)
			try:
				service=VDOM_service.connect(self.url, self.login, self.password, application)
			except:
				raise whole_connection_error(self.url, self.login)
			return v_wholeapplication(self.url, service)

	def v_isconnected(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("application")
		else:
			if not self.service:
				return v_false_value
			try:
				self.service.remote("keep_alive", None, True)
			except:
				return v_false_value
			return v_true_value
