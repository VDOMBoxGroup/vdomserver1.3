
import re
import managers, utils.uuid
from mailing.message import Message, MailAttachment
from ... import errors
from ...subtypes import binary, generic, string, integer, boolean, array, v_mismatch, v_nothing, integer
from ..scripting import v_vdomtype, v_vdomobject, v_vdomapplication


class v_attachment(generic):
	
	def __init__(self, attachment=None):
		generic.__init__(self)
		self._value=attachment or MailAttachment()
		
	
	value=property(lambda self: self._value)
	

	def v_data(self, **keywords):
		if "let" in keywords:
			self._value.data=keywords["let"].as_binary
		elif "set" in keywords:
			raise errors.object_has_no_property("data")
		else:
			return binary(self._value.data)	
		
	def v_filename(self, **keywords):
		if "let" in keywords:
			self._value.filename=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("filename")
		else:
			return string(self._value.filename)	
		
		
	def v_contenttype(self, **keywords):
		if "let" in keywords:
			self._value.content_type=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("contenttype")
		else:
			return string(self._value.content_type)	
		
	def v_contentsubtype(self, **keywords):
		if "let" in keywords:
			self._value.content_subtype=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("contentsubtype")
		else:
			return string(self._value.content_subtype)	

class v_attachmentcollection(generic):
	
	def __init__(self, value):
		generic.__init__(self)
		self._value=value

	def __call__(self, index, **keywords):
		if "let" in keywords:
			raise errors.object_has_no_property
		elif "set" in keywords:
			raise errors.object_has_no_property
		else:
			try:
				return v_attachment(self._value.attach[index.as_integer])
			except KeyError:
				return errors.subscript_out_of_range
	def __iter__(self):
		for attachment in self._value:
			yield variant(v_attachment(attachment))

class v_message(generic):

	def __init__(self, message=None):
		generic.__init__(self)
		self._value=message or Message()
		
		
	value=property(lambda self: self._value)
	

	def v_id(self, **keywords):
		if "let" in keywords:
			self._value.id=keywords["let"].as_integer
		elif "set" in keywords:
			raise errors.object_has_no_property("id")
		else:
			return integer(self._value.id)

	def v_subject(self, **keywords):
		if "let" in keywords:
			self._value.subject=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("subject")
		else:
			return v_empty if self._value.subject is None else string(self._value.subject)

	def v_sender(self, **keywords): # FromEmail -> Mail / MailBox / Origin
		if "let" in keywords:
			self._value.from_email=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("sender")
		else:
			return v_empty if self._value.from_email is None else string(self._value.from_email)

	def v_replyto(self, **keywords):
		if "let" in keywords:
			self._value.reply_to=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("replyto")
		else:
			return v_empty if self._value.reply_to is None else string(self._value.reply_to)
		
	def v_recipients(self, **keywords): # ToEmail -> Recipients
		if "let" in keywords:
			self._value.to_email=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("recipients")
		else:
			return v_empty if self._value.to_email is None else string(self._value.to_email)
		
	def v_body(self, **keywords): # Body -> Text / Contents
		if "let" in keywords:
			self._value.body=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("body")
		else:
			return v_empty if self._value.body is None else string(self._value.body)
		
	def v_nomultipart(self, **keywords):
		if "let" in keywords:
			self._value.nomultipart=keywords["let"].as_boolean
		elif "set" in keywords:
			raise errors.object_has_no_property("nomultipart")
		else:
			return boolean(self._value.nomultipart)
		
	def v_priority(self, **keywords):
		if "let" in keywords:
			self._value.priority=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("priority")
		else:
			return string(self._value.priority)
		
	def v_contenttype(self, **keywords):
		if "let" in keywords:
			keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("contenttype")
		else:
			return string("")
		
	def v_charset(self, **keywords):
		if "let" in keywords:
			keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("charset")
		else:
			return string("")
		
	def v_ttl(self, **keywords):
		if "let" in keywords:
			self._value.ttl=keywords["let"].as_integer
		elif "set" in keywords:
			raise errors.object_has_no_property("priority")
		else:
			return integer(self._value.ttl)
		
	def v_attachments(self, index=None, **keywords):
		if index is None:
			if "let" in keywords or "set" in keywords:
				raise errors.object_has_no_property("attachments")
			else:
				return v_attachment(self._value.attach[index.as_integer])
		else:
			return v_attachmentcollection(self._value.attach)


	def v_addattachment(self, attachment):
		self._value.attach.append(attachment.is_specific(v_attachment).value)
		return v_mismatch
		

class v_mailer(generic):
	
	def v_send(self, message):
		return integer(managers.email_manager.send(message.is_specific(v_message).value))
		        
	def v_receive(self, server, port, login, password, secure=None, index=None, delete=None):
		from mailing.pop import VDOM_Pop3_client
		p = VDOM_Pop3_client(server.as_string, port.as_integer, secure=False if secure is None else secure.as_boolean)
		p.user(login.as_string, password.as_string)
		if not p.connected:
			raise errors.mailserver_closed_connection()		
		message=p.fetch_message(0 if index is None else index.as_integer, False if delete is None else delete.as_boolean)
		p.quit()
		return v_message(message)
	
	def v_receiveall(self, server, port, login, password, secure=None, offset=None, limit=None, delete=None):
		from mailing.pop import VDOM_Pop3_client
		p = VDOM_Pop3_client(server.as_string, port.as_integer, secure=False if secure is None else secure.as_boolean)
		p.user(login.as_string, password.as_string)
		if not p.connected:
			raise errors.mailserver_closed_connection()
		messages=p.fetch_all_messages(0 if offset is None else offset.as_integer,None if limit is None else limit.as_integer, False if delete is None else delete.as_boolean)
		p.quit()
		return array(items=[v_message(item) for item in messages])	

	def v_status(self, msg_id):
		ret = managers.email_manager.check(msg_id.as_integer)
		return string(ret) if ret else v_nothing		
		
		
class v_server(generic):
	
	check_regex=re.compile("[0-9A-Z]{8}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{12}", re.IGNORECASE)
	
	
	def __init__(self):
		generic.__init__(self)
		self._mailer=v_mailer()


	def v_application(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("application")
		else:
			return v_vdomapplication(managers.request_manager.current.application())


	def v_getapplication(self):
		return v_vdomapplication(managers.request_manager.current.application())

	def v_createobject(self, type, parent, name=None):
		application=managers.request_manager.current.application()
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
		application=managers.request_manager.current.application()
		object_string=object_string.as_string.lower()
		if self.check_regex.search(object_string):
			object=application.search_object(object_string)
		else:
			objects=application.search_objects_by_name(object_string)
			object=objects[0] if objects else None
		return v_vdomobject(object) if object else v_nothing

	def v_deleteobject(self, object_string):
		application=managers.request_manager.current.application()
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
		application=managers.request_manager.current.application()
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
		managers.resource_manager.delete_resource(managers.request_manager.current.application(),
			resource.as_string)

	def v_htmlencode(self, string2encode):
		return string(unicode(string2encode.as_string.encode("html")))

	def v_urlencode(self, string2encode):
		return string(unicode(string2encode.as_string.encode("url")))

	def v_sendmail(self, sender, recipient, subject, message):
		return integer(managers.email_manager.send(sender.as_string,
			recipient.as_string, subject.as_string, message.as_string))

	def v_mailstatus(self, msg_id):
		ret = managers.email_manager.check(msg_id.as_integer)
		return string(ret) if ret else v_nothing		
	
	def v_mailer(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("mailer")
		else:
			return self._mailer
