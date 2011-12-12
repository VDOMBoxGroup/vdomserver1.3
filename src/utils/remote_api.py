import SOAPpy, md5, re, sys
from SOAPpy import WSDL
from soap.soaputils import VDOM_session_protector



session_id_re = re.compile("\<SessionId\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionId\>")
session_key_re = re.compile("\<SessionKey\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionKey\>")
hash_string_re = re.compile("\<HashString\>\<\!\[CDATA\[(\S+)\]\]\>\<\/HashString\>")
key_re = re.compile("\<Key\>(\S+)_\d+\<\/Key\>")


class VDOMService:

	def __init__(self, url, login, md5hexpass, application_id):
		self._url 				= url
		self._login 			= login
		self._md5hexpass 		= md5hexpass
		self._application_id 	= application_id

		self._request_num 		= 0
		self._skey 				= None
		self._sid 				= None
		self._skey 				= None

		#self._server 	= SOAPpy.SOAPProxy("https://%s:443/SOAP"%url,namespace="http://services.vdom.net/VDOMServices")
		self._server 	= SOAPpy.SOAPProxy("http://%s/SOAP"%url,namespace="http://services.vdom.net/VDOMServices")
		self._protector = None



	@classmethod
	def connect(self, url, login, md5_hexpass, application_id):
		service = VDOMService(url, login, md5_hexpass, application_id)
		return service.open_session()




	def open_session(self):
		login_result = self._server.open_session(self._login, self._md5hexpass)

		self._sid = str(session_id_re.search(login_result, 1).group(1))
		skey = str(session_key_re.search(login_result, 1).group(1))
		hash_string = str(hash_string_re.search(login_result, 1).group(1))

		self._protector = VDOM_session_protector(hash_string)
		self._skey = self._protector.next_session_key(skey)

		return self



	def call(self, container_id, action_name, xml_data):
		xml_param = "<Arguments><CallType>server_action</CallType></Arguments>"
		ret = self._server.remote_call(self._sid,"%s_%i"%(self._skey,self._request_num),self._application_id, container_id,action_name, xml_param, xml_data)
		try:
			server_skey = str(key_re.search(ret, 1).group(1))
		except:
			raise VDOMServiceCallError(str(ret))

		#assert (server_skey == self._skey)

		self._skey = self._protector.next_session_key(self._skey)
		self._request_num+=1
		return ret.replace("\n<Key>%s_%s</Key>" % (server_skey, str(self._request_num-1)), "")

	def remote(self, method, params = [], no_app_id = False):
		if params:
			ret = getattr(self._server,method)(self._sid,"%s_%i"%(self._skey,self._request_num),self._application_id, *params)
		elif no_app_id:
			ret = getattr(self._server,method)(self._sid,"%s_%i"%(self._skey,self._request_num))
		else:
			ret = getattr(self._server,method)(self._sid,"%s_%i"%(self._skey,self._request_num),self._application_id)
		try:
			server_skey = str(key_re.search(ret, 1).group(1))
		except:
			raise VDOMServiceCallError(str(ret))

		#assert (server_skey == self._skey)

		self._skey = self._protector.next_session_key(self._skey)
		self._request_num+=1
		return ret.replace("\n<Key>%s_%s</Key>" % (server_skey, str(self._request_num-1)), "")

VDOM_service = VDOMService


