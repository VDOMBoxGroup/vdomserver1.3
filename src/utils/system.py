import sys, socket, json




LINUX = sys.platform.startswith("linux")
FREEBSD = sys.platform.startswith("frebsd")
WIN = sys.platform.startswith("win")

if  LINUX:
	from utils.system_linux import *
elif FREEBSD:
	from utils.system_freebsd import *
elif WIN:
	from utils.system_windows import *
else:
	from utils.system_freebsd import *



direct = VDOM_CONFIG["STORAGE-DIRECTORY"] + "/socket"
s = None
try:
	s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
except:
	pass
def console_debug(data):
	l = os.listdir(direct)
	for item in l:
		p = os.path.join(direct, item)
		err = False
		try:
			s.sendto(data, p)
		except:
			err = True
		if err:
			try:
				os.remove(p)
			except:
				pass
	try:
		sess = managers.request_manager.get_request().session()
		d = sess.value("debug_data")
		if d is None:
			d = []
		d.append(data)
		sess.value("debug_data", d)
	except:
		pass


def set_virtual_card( user, password, guid ):
	shost, sl, sp = "partner.vdom-box-international.com", "card", "card"
	f = open('/etc/opt/virtcard', 'w')
	f.write( """%s %s %s %s %s %s""" % (shost, sl, sp, user, password, guid) )
	f.close()
	
	#a = send_to_card_and_wait("""vcard host """ +  json.dumps([ shost, sl, sp ]), "vcard_error")
	return send_to_card_and_wait("""vcard setup """ +  json.dumps([ user, password, guid ]), "vcard_error", 30, 0.5)

def login_virtual_card( user, password):
	if "vcard_systemlist" in system_options:
		del system_options["vcard_systemlist"]
	a = send_to_card_and_wait("vcard login " + json.dumps([ user, password ]), "vcard_error", 30, 0.5)
	systems = system_options.get("vcard_systemlist", None)
	if not systems:
		raise Exception(system_options.get("vcard_error", "Connection to partners timeout"))
	return [ (key, value) for key, value in systems.iteritems() ]


	


import managers
from utils.exception import VDOM_exception
from utils.card_connect import send_to_card,send_to_card_and_wait
