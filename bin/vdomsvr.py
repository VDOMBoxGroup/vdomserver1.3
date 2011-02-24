#!/usr/bin/python

"""
main module to run VDOM HTTP Server
"""

import __builtin__, sys, gettext, os
#import encodings.utf_16, encodings.utf_16_be, encodings.utf_16_le, encodings.utf_7, encodings.utf_8, encodings.utf_8_sig
#import xmlrpclib

gettext.install("vdom2")

sys.path.append("../src")

from config import VDOM_CONFIG, VDOM_CONFIG_1
__builtin__.VDOM_CONFIG = VDOM_CONFIG
__builtin__.VDOM_CONFIG_1 = VDOM_CONFIG_1

sys.path.append(VDOM_CONFIG["LIB-DIRECTORY"])

import utils.console

# obsolete initialization code

import utils.obsolete

# initialize vscript engine

import vscript.prepare

# handle imports to support application libraries

from server.metaimporter import VDOM_metaimporter
sys.meta_path.append(VDOM_metaimporter())

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

import utils.email1

from server.server import VDOM_box_server

server=VDOM_box_server()
server.start()

from utils.server import VDOM_thread, VDOM_daemon
from utils.tracing import show_active_threads, show_active_threads_stack, show_threads_trace

print
#show_active_threads()
#show_active_threads_stack()
show_threads_trace()

os._exit(0)
