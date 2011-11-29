
import re, md5, SOAPpy, codecs
from soap.soaputils import VDOM_session_protector
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *
from .escapes import escape, unescape, escape_page, unescape_page



class v_vdombox(generic):

	session_id_regex=re.compile("\<SessionId\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionId\>")
	session_key_regex=re.compile("\<SessionKey\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionKey\>")
	hash_string_regex=re.compile("\<HashString\>\<\!\[CDATA\[(\S+)\]\]\>\<\/HashString\>")
	key_regex=re.compile("(\r?\n\<Key\>\d+_\d+\<\/Key\>)$")

	def __init__(self):
		generic.__init__(self)

	def v_open(self, address, username, password):
		self.address=as_string(address)
		self.server=SOAPpy.WSDL.Proxy("http://%s/vdom.wsdl"%self.address)
		self.username=as_string(username)
		self.password=as_string(password)
		response=self.server.open_session(self.username, md5.new(self.password).hexdigest())
		# <Session>
		#   <SessionId><![CDATA[...]]></SessionId>
		#   <SessionKey><![CDATA[...]]></SessionKey>
		#   <HashString><![CDATA[...]]></HashString>
		# </Session>
		# <Hostname></Hostname>
		# <Username>root</Username>
		# <ServerVersion>x.x.xxxx</ServerVersion>
		match=v_vdombox.session_id_regex.search(response)
		if match is None:
			raise errors.invalid_procedure_call(name=u"open")
		self.session_id=match.group(1)
		match=v_vdombox.session_key_regex.search(response)
		if match is None:
			raise errors.invalid_procedure_call(name=u"open")
		self.session_key=match.group(1)
		match=v_vdombox.hash_string_regex.search(response)
		if match is None:
			raise errors.invalid_procedure_call(name=u"open")
		self.hash_string=match.group(1)
		self.index=None
		self.protector=VDOM_session_protector(self.hash_string)

	def v_close(self):
		self.server.close_session(self.session_id)

	def v_invoke(self, name, *arguments):
		self.session_key=self.protector.next_session_key(self.session_key)
		self.index=0 if self.index is None else self.index+1
		try:
			handler=getattr(self.server, as_string(name))
		except AttributeError:
			raise errors.invalid_procedure_call(name=u"invoke")
		arguments=tuple(as_string(argument) for argument in arguments)
		response=handler(self.session_id, "%s_%s"%(self.session_key, self.index), *arguments)
		# ...
		# <Key>...</Key>
		response=u"<response>%s</response>"%response
		match=v_vdombox.key_regex.search(response)
		if match:
			response=response[:match.start(1)]
		return string(response)
