import sys, socket


LINUX = sys.platform.startswith("linux")
FREEBSD = sys.platform.startswith("frebsd")


if  LINUX:
	from utils.system_linux import *
elif FREEBSD:
	from utils.system_freebsd import *
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

import managers
