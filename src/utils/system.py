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
	if os.path.exists(direct):
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



def set_virtual_card_key( system_key ):
	return send_to_card_and_wait("""vcard licensekey """ +  json.dumps(system_key), "vcard_error", 30, 0.5)


def set_virtual_card( user, password, guid ):
	#a = send_to_card_and_wait("""vcard host """ +  json.dumps([ shost, sl, sp ]), "vcard_error")
	return send_to_card_and_wait("""vcard setup """ +  json.dumps([ user, password, guid ]), "vcard_error", 30, 0.5)

def login_virtual_card( user, password):
	if "vcard_systemlist" in system_options:
		del system_options["vcard_systemlist"]
	a = send_to_card_and_wait("vcard login " + json.dumps([ user, password ]), "vcard_error", 30, 0.5)
	systems = system_options.get("vcard_systemlist", None)
	if systems is None:
		raise Exception(system_options.get("vcard_error", "Connection to partners timeout"))
	not_sorted = [ (key, value) for key, value in systems.iteritems() ]
	return sorted( not_sorted, cmp=lambda x,y: cmp(x[1], y[1]) )


def set_system_name(name):
	system_options["system_name"] = name
	managers.file_manager.write_file(os.path.join(VDOM_CONFIG["SERVER-INFORMATION-DIRECTORY"], "system_name"), system_options["system_name"])

def set_server_state(state):
	#system_options["server_state"] = state
	managers.file_manager.write_file(os.path.join(VDOM_CONFIG["SERVER-INFORMATION-DIRECTORY"], "server_status"), state)

def set_card_state(state=""):
	if state:
		system_options["card_state"] = state
	managers.file_manager.write_file(os.path.join(VDOM_CONFIG["SERVER-INFORMATION-DIRECTORY"], "cardprocess_status"), system_options["card_state"])

def set_loaded_applications(app_list):
	from cStringIO import StringIO
	buff = StringIO()
	#system_options["applications"] = app_list
	for app_id, app_obj in app_list.items():
		buff.write("%s (%s)\n" % (app_obj.name, app_id))
	managers.file_manager.write_file(os.path.join(VDOM_CONFIG["SERVER-INFORMATION-DIRECTORY"], "loaded_applications"), buff.getvalue())
	buff.close()

import managers
from utils.exception import VDOM_exception
from utils.card_connect import send_to_card,send_to_card_and_wait
