
import re
import managers, utils.uuid
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *
from .escapes import escape, unescape, escape_page, unescape_page



class xmlobjectwrapper(generic):

	def __init__(self, object):
		generic.__init__(self)
		self.__object=object

	def __getattr__(self, name):
		if name.startswith("v_"):
			name=name[2:]
			attributes=self.__object.attributes
			objects=self.__object.get_objects_by_name()
			if name in attributes:
				return shadow(self, "wrapper_%s"%name)
			elif name in objects:
				return xmlobjectwrapper(objects[name])
			else:
				raise errors.object_has_no_property(name)
		elif name.startswith("wrapper_"):
			name=name[8:]
			attributes=self.__object.attributes
			return string(attributes[name].value)
		else:
			generic.__getattr__(self, name)

	def __setattr__(self, name, value):
		if name.startswith("v_"):
			name=name[2:]
			attributes=self.__object.attributes
			objects=self.__object.get_objects_by_name()
			if name in attributes:
				setattr(self.__object, name, as_string(value))
			elif name in objects:
				raise errors.type_mismatch
			else:
				raise errors.object_has_no_property(name)
		elif name.startswith("wrapper_"):
			name=name[8:]
			attributes=self.__object.attributes
			self.__object.set_attribute_ex(name, as_string(value), do_compute=False)
		else:
			generic.__setattr__(self, name, value)

	object=property(lambda self:self.__object)
	
	def v_name(self, let=None, set=None):
		if let is not None:
			self.__object.set_name(as_string(let))
		elif set is not None:
			raise errors.object_has_no_property("name")
		else:
			return string(self.__object.name)

	def __repr__(self):
		return "XMLOBJECTWRAPPER@%s:%s"%(object.__repr__(self)[-9:-1], repr(self.__object))

class xmlapplicationwrapper(generic):

	def __init__(self, object):
		generic.__init__(self)
		self.__object=object

	def __getattr__(self, name):
		if name.startswith("v_"):
			name=name[2:]
			objects=self.__object.get_objects_by_name()
			if name in objects:
				return xmlobjectwrapper(objects[name])
			else:
				raise errors.object_has_no_property(name)
		else:
			generic.__getattr__(self, name)

	def __setattr__(self, name, value):
		if name.startswith("v_"):
			name=name[2:]
			objects=self.__object.get_objects_by_name()
			if name in objects:
				raise errors.type_mismatch
			else:
				raise errors.object_has_no_property(name)
		else:
			generic.__setattr__(self, name, value)

	object=property(lambda self:self.__object)
	
	def v_id(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("id")
		else:
			return string(self.__object.id)

	def v_name(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("name")
		else:
			return string(self.__object.name)

	def __repr__(self):
		return "XMLAPPLICATIONWRAPPER@%s:%s"%(object.__repr__(self)[-9:-1], repr(self.__object))

class server(generic):

	check_regex=re.compile("[0-9A-Z]{8}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{12}", re.IGNORECASE)

	def __init__(self):
		generic.__init__(self)

	def v_getapplication(self):
		application=managers.request_manager.get_request().application()
		return xmlapplicationwrapper(application)

	def v_application(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("name")
		else:
			application=managers.request_manager.get_request().application()
			return xmlapplicationwrapper(application)

	def v_createobject(self, type, parent, name=None):
		application=managers.request_manager.get_request().application()
		type=as_string(type).lower()
		if not server.check_regex.search(type):
			xml_type=managers.xml_manager.get_type_by_name(type)
			type=xml_type.id if xml_type is not None else None
		parent=as_string(parent).lower()
		if server.check_regex.search(parent):
			parent=application.search_object(parent)
		else:
			objects=application.search_objects_by_name(parent)
			parent=objects[0] if len(objects)==1 else None
		if type is None or parent is None:
			raise errors.invalid_procedure_call(name=u"createobject")
		object_tuple=application.create_object(type, parent)
		object=application.search_object(object_tuple[1])
		if name is not None:
			name=as_string(name)
			object.set_name(name)
		return xmlobjectwrapper(object)

	def v_deleteobject(self, object_string):
		application=managers.request_manager.get_request().application()
		object_string=as_string(object_string).lower()
		if server.check_regex.search(object_string):
			object=application.search_object(object_string)
		else:
			objects=application.search_objects_by_name(object_string)
			object=objects[0] if len(objects)==1 else None
		if object is None:
			raise errors.invalid_procedure_call(name=u"deleteobject")
		application.delete_object(object)

	def v_getobject(self, object_string):
		application=managers.request_manager.get_request().application()
		object_string=as_string(object_string).lower()
		if server.check_regex.search(object_string):
			object=application.search_object(object_string)
		else:
			objects=application.search_objects_by_name(object_string)
			object=objects[0] if objects else None
		return xmlobjectwrapper(object) if object else v_nothing

	def v_createresource(self, type, name, data):
		application=managers.request_manager.get_request().application()
		data=as_value(data)
		resid=unicode(utils.uuid.uuid4())
		if isinstance(data, binary):
			application.create_resource(resid,
				as_string(type), as_string(name), as_binary(data))
			
		else:
			application.create_resource(resid,
				as_string(type), as_string(name), as_string(data))
		return string(resid)
		
	def v_deleteresource(self, resource):
		application=managers.request_manager.get_request().application()
		managers.resource_manager.delete_resource(application, as_string(resource))

	def v_htmlencode(self, string2encode):
		return string(escape_page(string2encode))

	def v_urlencode(self, string2encode):
		return string(unicode(u"+".join(map(escape, as_string(string2encode).split()))))

	def v_sendmail(self, sender, recipient, subject, message):
		sender, recipient=as_string(sender), as_string(recipient)
		subject, message=as_string(subject), as_string(message)
		managers.email_manager.send(sender, recipient, subject, message)


server=server()
