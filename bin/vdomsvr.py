#!/usr/bin/python

import sys, gettext, os
#import encodings.utf_16, encodings.utf_16_be, encodings.utf_16_le, encodings.utf_7, encodings.utf_8, encodings.utf_8_sig
#import xmlrpclib

gettext.install("vdom2")
sys.path.append("../src")

import utils.obsolete

import managers
from server import VDOM_server
from log import VDOM_log_manager
from storage import VDOM_storage
from file_access import VDOM_file_manager, VDOM_share
from resource import VDOM_resource_manager, VDOM_resource_editor
from database import VDOM_database_manager
from source import VDOM_source_swap, VDOM_source_cache, VDOM_compiler, VDOM_dispatcher
from security import VDOM_acl_manager, VDOM_user_manager
from request import VDOM_request_manager
from engine import VDOM_engine
from module import VDOM_module_manager
from session import VDOM_session_manager
from memory import VDOM_xml_manager
from mailing import VDOM_email_manager
from soap import VDOM_soap_server
from managment import VDOM_server_manager

managers.register("server", VDOM_server)
managers.register("log_manager", VDOM_log_manager)
managers.register("storage", VDOM_storage)
managers.register("file_manager", VDOM_file_manager)
managers.register("file_share", VDOM_share)
managers.register("resource_manager", VDOM_resource_manager)
managers.register("resource_editor", VDOM_resource_editor)
managers.register("database_manager", VDOM_database_manager)
managers.register("source_swap", VDOM_source_swap)
managers.register("source_cache", VDOM_source_cache)
managers.register("compiler", VDOM_compiler)
managers.register("dispatcher", VDOM_dispatcher)
managers.register("acl_manager", VDOM_acl_manager)
managers.register("user_manager", VDOM_user_manager)
managers.register("request_manager", VDOM_request_manager)
managers.register("engine", VDOM_engine)
managers.register("module_manager", VDOM_module_manager)
managers.register("session_manager", VDOM_session_manager)
managers.register("xml_manager", VDOM_xml_manager)
managers.register("email_manager", VDOM_email_manager)
managers.register("soap_server", VDOM_soap_server)
managers.register("server_manager", VDOM_server_manager)

managers.server.start()

from utils.tracing import show_threads_trace
show_threads_trace()

os._exit(0)
