import sys, socket




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
	shost, sl, sp = ("partner.vdom-box-international.com", "card", "card")
	
	f = open('/etc/opt/virtcard', 'w')
	f.write( """%s %s %s %s %s %s""" % (shost, sl, sp, user, password, guid) )
	f.close()
	
	return send_to_card_and_wait("""virtualcard %s %s %s %s %s %s""" % (shost, sl, sp, user, password, guid), "carderror")

def login_virtual_card( user, password):
	if user == "1":
		return [("guid1","name1"),("guid2","name2"), ("guid3","name3")]
	else:
		raise VDOM_exception ("Virtual card connection failed")
	
	


import managers
from utils.exception import VDOM_exception
from utils.card_connect import send_to_card,send_to_card_and_wait
