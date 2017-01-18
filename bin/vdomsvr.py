#!/usr/bin/python

import datetime, time
# http://bugs.python.org/issue7980
datetime.datetime.strptime('2012-01-01', '%Y-%m-%d')
time.strptime('2012-01-01', '%Y-%m-%d')

import sys, gettext, os
#import encodings.utf_16, encodings.utf_16_be, encodings.utf_16_le, encodings.utf_7, encodings.utf_8, encodings.utf_8_sig
#import xmlrpclib

gettext.install("vdom2")
sys.path.insert(0, '../src')

#import wingdbstub
from utils import codecs
from utils.card_connect import send_to_card
import utils.obsolete
#Seting 10% to progressbar
from utils.system import set_card_state

send_to_card("booting 10")

import managers

from server import VDOM_server
#Seting 20% to progressbar
send_to_card("booting 20")

from log import VDOM_log_manager
from storage import VDOM_storage
from file_access import VDOM_file_manager, VDOM_share
from resource import VDOM_resource_manager, VDOM_resource_editor
from database import VDOM_database_manager
from source import VDOM_source_swap, VDOM_source_cache, VDOM_compiler, VDOM_dispatcher
from security import VDOM_acl_manager, VDOM_user_manager
from web import VDOM_vhosting
from request import VDOM_request_manager
from engine import VDOM_engine
from module import VDOM_module_manager
from session import VDOM_session_manager
from memory import VDOM_xml_manager
from mailing import VDOM_email_manager
from soap import VDOM_soap_server
from managment import VDOM_server_manager
from scheduler import VDOM_scheduler_manager
from task import VDOM_task_manager
from backup import VDOM_backup_manager
from webdav_server import VDOM_webdav_manager

try:
	managers.register("server", VDOM_server)
	managers.register("log_manager", VDOM_log_manager)
	managers.register("storage", VDOM_storage)
	managers.register("file_manager", VDOM_file_manager)
	managers.register("file_share",	VDOM_share)
	managers.register("resource_manager", VDOM_resource_manager)
	managers.register("resource_editor", VDOM_resource_editor)
	managers.register("database_manager", VDOM_database_manager)
	managers.register("source_swap", VDOM_source_swap)
	managers.register("source_cache", VDOM_source_cache)
	managers.register("compiler", VDOM_compiler)
	managers.register("dispatcher", VDOM_dispatcher)
	managers.register("acl_manager", VDOM_acl_manager)
	managers.register("user_manager", VDOM_user_manager)
	managers.register("virtual_hosts", VDOM_vhosting)
	managers.register("request_manager", VDOM_request_manager)
	managers.register("engine", VDOM_engine)
	managers.register("module_manager", VDOM_module_manager)
	managers.register("session_manager", VDOM_session_manager)
	managers.register("scheduler_manager", VDOM_scheduler_manager)
	managers.register("xml_manager", VDOM_xml_manager)
	managers.register("email_manager", VDOM_email_manager)
	managers.register("soap_server", VDOM_soap_server)
	managers.register("server_manager", VDOM_server_manager)	
	managers.register("task_manager", VDOM_task_manager)	
	managers.register("backup_manager", VDOM_backup_manager)
	managers.register("webdav_manager", VDOM_webdav_manager)

	if sys.platform.startswith("linux") and VDOM_CONFIG_1["DEBUG"] == "1":
		from utils.system_linux import open_debug_port
		open_debug_port()
	set_card_state()
	if sys.argv and "--unittest" in sys.argv:
		from unittest import TestLoader, TextTestRunner
		loader=TestLoader()
		suite=loader.discover(start_dir="..\\src\\vscript", pattern="test*.py", top_level_dir="..\\src")
		TextTestRunner(verbosity=2).run(suite)
	else:
		managers.server.start()
	#managers.file_manager.write_file(os.path.join(VDOM_CONFIG["SERVER-INFORMATION-DIRECTORY"], "virtcard_name"), system_options)
except:
	from traceback import print_exc
	sys.stderr.write("\n")
	print_exc()
	from utils.tracing import show_threads_trace
	show_threads_trace(details=None)
finally:
	import threading
	count=threading.active_count()
	if count>1:
		sys.stderr.write("\n")
		from utils.tracing import show_threads_trace
		show_threads_trace(details=None)
		daemons=tuple(thread for thread in threading.enumerate() if thread.daemon)
		if count-len(daemons)>1:
			sys.stderr.write("\nForce exit\n")
			os._exit(0)
