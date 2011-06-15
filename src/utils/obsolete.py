
import __builtin__, sys, os,  time, thread, socket, shutil, stat

from config import VDOM_CONFIG, VDOM_CONFIG_1
__builtin__.VDOM_CONFIG = VDOM_CONFIG
__builtin__.VDOM_CONFIG_1 = VDOM_CONFIG_1

import managers
from utils.system import console_debug

# install debug and licensing

#overriding server ports
print ("Server run params: vdomsvr.py -p SERVER-PORT LOCAL-PORT CARD-PORT LOGGER-PORT -c vdom.cfg")
if sys.argv:
	for i in range(len(sys.argv)):
		if sys.argv[i] == "-p" and i+1<len (sys.argv):
			portlist = sys.argv[i+1:]
			confkeys = ("SERVER-PORT", "SERVER-LOCALHOST-PORT","LOCALHOST-CARD-PORT","LOCALHOST-LOGGER-PORT")
			for j in range(min(len(portlist),len(confkeys))):
				if not portlist[j].isdigit():
					break
				VDOM_CONFIG[confkeys[j]] = int(portlist[j])
			break
		if sys.argv[i] == "-c" and i+1<len (sys.argv):
			if os.path.isfile(sys.argv[i+1]):
				import ConfigParser
				config = ConfigParser.SafeConfigParser()
				config.read(sys.argv[i+1])
				for key in VDOM_CONFIG:
					if config.has_option("VdomConfig", key):
						if type(VDOM_CONFIG[key]) is int:
							VDOM_CONFIG[key] = config.getint("VdomConfig", key)
						else:
							VDOM_CONFIG[key] = config.get("VdomConfig", key)
					



if sys.platform.startswith("freebsd") or sys.platform.startswith("linux"):
	try:
		f = open(VDOM_CONFIG["LOGGER-PIDFILE"], "r")
		pid = f.read()
		f.close()
		os.system("kill " + pid)
		time.sleep(1)
	except: pass
	i = os.spawnl(os.P_NOWAIT, "logger")
	f = open(VDOM_CONFIG["LOGGER-PIDFILE"], "w")
	f.write(str(i))
	f.close()

def send_to_log(data):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.sendto(data, ('localhost', VDOM_CONFIG["LOCALHOST-LOGGER-PORT"]))
	except:
		pass

if sys.platform.startswith("freebsd") or sys.platform.startswith("linux"):
	time.sleep(1)
	send_to_log(str(VDOM_CONFIG["LOG-FILE-COUNT"]))
	send_to_log(str(VDOM_CONFIG["LOG-FILE-SIZE"]))
	send_to_log(VDOM_CONFIG["LOG-DIRECTORY"])

tags=None

def my_debug(_data, tag="", console=None):
	global tags
	from storage.storage import VDOM_config
	if tags is None:
		import managers
		tags=managers.storage.read_object("DEBUG-TAGS") or []
	debug_on = True
	if "1" != VDOM_CONFIG_1["DEBUG"]:
		debug_on = False
	data = ""
	if isinstance(_data, unicode):
		data = _data.encode("utf-8")
	else:
		data = str(_data)
	if console is not None:
		console_debug(data)
	cf = VDOM_config()
	if not debug_on:
		return
	_tag = s = ""
	if tag:
		_tag = tag.lower()
		if _tag not in tags:
			tags.append(_tag)
			managers.storage.write_object_async("DEBUG-TAGS", tags)
			cf.set_opt_sync("DEBUG-ENABLE-TAG-" + _tag, "1")
	x = time.strftime("%d %b %Y %H:%M:%S", time.gmtime())
	prep = "%s thread %4d" % (x, thread.get_ident())
	en_tag = VDOM_CONFIG_1["DEBUG-ENABLE-TAGS"]
	if "1" == en_tag and "" != tag and "1" == cf.get_opt("DEBUG-ENABLE-TAG-" + _tag):
		prep += " [%s]: " % _tag
	else:
		prep += ": "
	s = ("\n" + prep).join(data.split("\n"))
	sys.stderr.write(prep + s + "\n")
	send_to_log(prep + s + "\n")

class my_debugfile:

	def write(self, some):
		my_debug(some)

def increase_objects_count(app):
	if app:
		app.xml_manager.modify_objects_count(1)

def decrease_objects_count(app):
	if app:
		app.xml_manager.modify_objects_count(-1)

__builtin__.debug = my_debug
__builtin__.debugfile = my_debugfile()
__builtin__.increase_objects_count = increase_objects_count
__builtin__.decrease_objects_count = decrease_objects_count
__builtin__.system_options = {"server_license_type": "0",	# online server, 1=development
				"firmware" : "N/A",
				"card_state" : "0",	# 0 - no card, 1 - card ok
				"object_amount" : "1500"}

# verify that server is not running

addr_try = VDOM_CONFIG["SERVER-ADDRESS"]
if addr_try == "":
	addr_try = "localhost"
sock = socket.socket()
ok = False
try:
	sock.connect((addr_try, VDOM_CONFIG["SERVER-PORT"]))
except:
	# exception means connection failed, thus server should not be running
	ok = True
	print "Tried", addr_try, ":", VDOM_CONFIG["SERVER-PORT"], "- no response"
sock.close()
if not ok:
	print(_("Server is already running"))
	print "Got response on", addr_try, ":", VDOM_CONFIG["SERVER-PORT"]
	os._exit(0)

# enforce directory structure

try: os.makedirs(VDOM_CONFIG["TYPES-LOCATION"])
except: pass
try: os.makedirs(VDOM_CONFIG["FILE-ACCESS-DIRECTORY"] + "/applications")
except: pass
try: os.makedirs(VDOM_CONFIG["SOURCE-MODULES-DIRECTORY"])
except: pass
try: os.makedirs(VDOM_CONFIG["LOG-DIRECTORY"])
except: pass
try: os.makedirs(VDOM_CONFIG["BACKUP-DIRECTORY"])
except: pass
try: os.rmdir(VDOM_CONFIG["STORAGE-DIRECTORY"] + "/socket")
except: pass
try: os.makedirs(VDOM_CONFIG["STORAGE-DIRECTORY"] + "/socket")
except: pass
try: os.makedirs(VDOM_CONFIG["LIB-DIRECTORY"])
except: pass

# change directory access rights

os.chmod(VDOM_CONFIG["STORAGE-DIRECTORY"] + "/socket", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

# enforce lib module

f = open(os.path.join(VDOM_CONFIG["STORAGE-DIRECTORY"], "lib", "__init__.py"), "wt")
f.close()

# copy types to hard drive

print "Copying VDOM types to hard drive...",
_from = VDOM_CONFIG["SOURCE-TYPES-LOCATION"]
_to = VDOM_CONFIG["TYPES-LOCATION"]
from_files = os.listdir(_from)
to_files = os.listdir(_to)
for item in from_files:
	if "xml" != item.split(".")[-1]:
		continue
	if item in to_files:
		stat_from = os.stat(_from + "/" + item)
		stat_to = os.stat(_to + "/" + item)
		if stat_from[8] <= stat_to[8]:
			continue
	shutil.copy2(_from + "/" + item, _to + "/" + item)
if not os.path.exists(VDOM_CONFIG["APPLICATION-XML-TEMPLATE"]):
	shutil.copy2("app_template.xml", VDOM_CONFIG["APPLICATION-XML-TEMPLATE"])
print "Done"