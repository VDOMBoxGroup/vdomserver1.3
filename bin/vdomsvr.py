#!/usr/bin/python

"""
main module to run VDOM HTTP Server
"""

import sys, time, os, thread, socket, gettext, shutil, stat, __builtin__
import encodings.utf_16, encodings.utf_16_be, encodings.utf_16_le, encodings.utf_7, encodings.utf_8, encodings.utf_8_sig
import xmlrpclib

sys.path.append("..\src")

from config import *
__builtin__.VDOM_CONFIG = VDOM_CONFIG
__builtin__.VDOM_CONFIG_1 = VDOM_CONFIG_1

# logger
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

sys.path.append(VDOM_CONFIG["LIB-DIRECTORY"])

try: os.makedirs(VDOM_CONFIG["TYPES-LOCATION"])
except: pass
try: os.makedirs(VDOM_CONFIG["TEMP-DIRECTORY"] + "/types")
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
os.chmod(VDOM_CONFIG["STORAGE-DIRECTORY"] + "/socket", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

f = open(os.path.join(VDOM_CONFIG["STORAGE-DIRECTORY"], "lib", "__init__.py"), "wt")
f.close()

from storage.storage import VDOM_config
from util.system import console_debug
import managers
import log
import util.email1

gettext.install("vdom2")

# debug
tags = managers.storage.read_object("DEBUG-TAGS")
if not tags:
	tags = []
def my_debug(_data, tag="", console=None):
	global tags
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
#	print app.xml_manager.obj_count

def decrease_objects_count(app):
	if app:
		app.xml_manager.modify_objects_count(-1)
#	print app.xml_manager.obj_count

__builtin__.debug = my_debug
__builtin__.debugfile = my_debugfile()
__builtin__.increase_objects_count = increase_objects_count
__builtin__.decrease_objects_count = decrease_objects_count
__builtin__.system_options = {"server_license_type": "0",	# online server, 1=development
				"firmware" : "N/A",
				"card_state" : "0",	# 0 - no card, 1 - card ok
				"object_amount" : "1500"}


def watcher():
	while True:
		try:
			data = raw_input()
			exec data
		except EOFError:
			print "Keyboard interrupt"
			#actions_on_shutdown()
			os._exit(0)
		except Exception, e:
			print e

# verify that server is not running
# attempt to establish a connection on server address or localhost
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

if not sys.platform.startswith("freebsd") and not sys.platform.startswith("linux") and 'WINGDB_ACTIVE' not in os.environ:
	thread.start_new_thread(watcher, ())

# copy types
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

# initialize vscript engine

import vscript.prepare

# handle imports to support application libraries

import threading, imp, pkgutil

class metaimporter(object):
	def find_module(self, fullname, path=None):
		#print "[MetaImporter] Search for %s (%s)"%(fullname, path)
		application=getattr(threading.currentThread(), "application", None)
		if application is None:
			return None
		
		if not fullname.startswith(application):
			return None
		
		if fullname == application:
			#load application
			search_path=[VDOM_CONFIG["LIB-DIRECTORY"]]
			try:
				file, pathname, description=imp.find_module(fullname, search_path)
			except ImportError, error:
				return None
			return pkgutil.ImpLoader(fullname, file, pathname, description)
		elif fullname.find(".") != -1:
			#load library
			(app_module, library) = fullname.split(".",1)
			search_path=["%s/%s"%(VDOM_CONFIG["LIB-DIRECTORY"],app_module)]
			try:
				file, pathname, description=imp.find_module(library, search_path)
			except ImportError, error:
				return None
			return pkgutil.ImpLoader(fullname, file, pathname, description)
		else:
			return None

sys.meta_path.append(metaimporter())

# initialize server

import log
import storage
import file_access
import resource
import database
import source
import security
import request
import engine
import module
import session
import soap


import vdom_memory_client
from server.server import VDOM_server

#from actions import actions_on_shutdown

#if not request_object.session().on_start_executed and _a.global_actions["session"]["sessiononstart"].code:
#				src!.engine.engine.special(_a, _a.global_actions["session"]["sessiononstart"])
#				request_object.session().on_start_executed = True

# create server object instance and start the server

while True:
	print "Creating VDOM server"
	server = VDOM_server()
	server.start()
	try:
		if server.server.restart:
			server = None
			time.sleep(2)
			continue
	except:
		pass
	finally:
		#actions_on_shutdown()
		pass
	os._exit(0)
