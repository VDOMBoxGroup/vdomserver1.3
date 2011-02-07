
import SOAPpy, re, sys
from hashlib import md5
from SOAPpy import WSDL
import base64,zlib
## =============================================================================================

# session protector class
class VDOM_session_protector:
	"""class used to protect web services from unauthorized access"""

	def __init__(self, hash_str):
		"""constructor"""
		self.__hash = hash_str

	def next_session_key(self, session_key):
		"""generate next session key"""
		## verify hashcode
		if self.__hash == "":
			raise VDOM_exception("Hash code is empty")

		for idx in xrange(len(self.__hash)):
			i = self.__hash[idx]
			if not str(i).isdigit():
				raise VDOM_exception("Hash code contains non-digit letter \"%c\"" % str(i))
		result = 0
		for idx in xrange(len(self.__hash)):
			i = self.__hash[idx]
			result += int(self.__calc_hash(session_key, int(i)))
		return ("0"*10 + str(result)[0:10])[-10:]

	def __calc_hash(self, session_key, val):
		"""calculate hash"""
		result = ""
		if val == 1:
			return ("00" + str(int(session_key[0:5]) % 97))[-2:]
		elif val == 2:
			for i in range(1, len(session_key)):
				result = result + session_key[i*(-1)]
			return str(result + session_key[0])
		elif val == 3:
			return session_key[-5:] + session_key[0:5]
		elif val == 4:
			num  = 0
			for i in range(1, 9):
				num += int(session_key[i]) + 41
			return str(num)
		elif val == 5:
			ch = ""
			num = 0
			for i in range(len(session_key)):
				ch = chr(ord(session_key[i]) ^ 43)
				if not ch.isdigit():
					ch = str(ord(ch))
				num += int(ch)
			return str(num)
		else:
			return str(int(session_key) + val)

def load_file(filename):
	file=open(filename, "rb")
	resource=file.read()
	file.close()
	return resource
## =============================================================================================
#########CONFIG#########
name = r"C:\WORK\VDOM\Server\app\resources\5d79eb7c-23a7-4f47-8e80-32f020032f84\new_2a8a6b2e-37ed-4d45-ab1a-ac340ef649aa"
app_id = "5d79eb7c-23a7-4f47-8e80-32f020032f84"
res_id = "39b1aafa-8d0a-42dd-b6a0-9ae02356d3aa"
wsdlFile = 'http://127.0.0.1/vdom.wsdl'
#########END CONFIG#####
server = WSDL.Proxy(wsdlFile)               
pwd = md5("root").hexdigest()
aaa = server.open_session('root', pwd)
print aaa


rex = re.compile("\<SessionId\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionId\>").search(aaa, 1)
print str(rex.group(1))
sid = str(rex.group(1))

rex = re.compile("\<SessionKey\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionKey\>").search(aaa, 1)
print str(rex.group(1))
skey = str(rex.group(1))

rex = re.compile("\<HashString\>\<\!\[CDATA\[(\S+)\]\]\>\<\/HashString\>").search(aaa, 1)
print str(rex.group(1))
hash_string = str(rex.group(1))



obj = VDOM_session_protector(hash_string)
skey = obj.next_session_key(skey)


aaa = server.update_resource(sid, skey+"_0", app_id,res_id,base64.b64encode(zlib.compress(load_file(name))))

print aaa

sys.exit(0)

