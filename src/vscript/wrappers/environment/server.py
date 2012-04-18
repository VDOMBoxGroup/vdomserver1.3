
import re
import managers, utils.uuid
from ... import errors
from ...subtypes import binary, generic, string, v_mismatch, v_nothing
from ..scripting import v_vdomtype, v_vdomobject, v_vdomapplication


class v_server(generic):
	
	check_regex=re.compile("[0-9A-Z]{8}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{12}", re.IGNORECASE)


	def v_application(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("application")
		else:
			return v_vdomapplication(managers.request_manager.get_request().application())


	def v_getapplication(self):
		return v_vdomapplication(managers.request_manager.get_request().application())

	def v_createobject(self, type, parent, name=None):
		application=managers.request_manager.get_request().application()
		type=type.as_string.lower()
		if not self.check_regex.search(type):
			xml_type=managers.xml_manager.get_type_by_name(type)
			type=None if xml_type is None else xml_type.id
		parent=parent.as_string.lower()
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
			object.set_name(name.as_string)
		return v_vdomobject(object)

	def v_getobject(self, object_string):
		application=managers.request_manager.get_request().application()
		object_string=object_string.as_string.lower()
		if self.check_regex.search(object_string):
			object=application.search_object(object_string)
		else:
			objects=application.search_objects_by_name(object_string)
			object=objects[0] if objects else None
		return v_vdomobject(object) if object else v_nothing

	def v_deleteobject(self, object_string):
		application=managers.request_manager.get_request().application()
		object_string=object_string.as_string.lower()
		if self.check_regex.search(object_string):
			object=application.search_object(object_string)
		else:
			objects=application.search_objects_by_name(object_string)
			object=objects[0] if len(objects)==1 else None
		if object is None:
			raise errors.invalid_procedure_call(name=u"deleteobject")
		application.delete_object(object)
		return v_mismatch

	def v_createresource(self, type, name, data):
		application=managers.request_manager.get_request().application()
		data=data.as_simple
		resid=unicode(utils.uuid.uuid4())
		if isinstance(data, binary):
			application.create_resource(resid,
				type.as_string, name.as_string, data.as_binary)
		else:
			application.create_resource(resid,
				type.as_string, name.as_string, data.as_string)
		return string(resid)
		
	def v_deleteresource(self, resource):
		managers.resource_manager.delete_resource(managers.request_manager.get_request().application(),
			resource.as_string)

	def v_htmlencode(self, string2encode):
		return string(unicode(string2encode.as_string.encode("html")))

	def v_urlencode(self, string2encode):
		return string(unicode(string2encode.as_string.encode("url")))

	def v_sendmail(self, sender, recipient, subject, message):
		managers.email_manager.send(sender.as_string,
			recipient.as_string, subject.as_string, message.as_string)


v_server=v_server()
