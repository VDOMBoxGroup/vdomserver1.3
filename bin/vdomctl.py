#!/usr/bin/python

"""
VDOM http server control utility
"""

import sys
import os
import socket

sys.path.append("..")

from src.config import VDOM_CONFIG

if len(sys.argv) != 2:

	print """
Usage: python vdomctl.py command

where
	command is the command that will be sent to the server

currently supported commands are:
	stop
	restart
	clean
"""

	sys.exit()

port = VDOM_CONFIG["SERVER-LOCALHOST-PORT"]

def srv_ctl(command):
	"""send command to server localhost socket"""
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.sendto(command, ('localhost', port))

def stop_server():
	"""stops server by sending the stop command to server localhost socket"""
	print("Stopping server on localhost:%d" % port)
	srv_ctl("stop")
	print("Done")

def restart_server():
	"""restarts server by sending the restart command to server localhost socket"""
	print("Restarting server on localhost:%d" % port)
	srv_ctl("restart")
	print("Done")

def clean():
	"""stop server and remove pidfile"""
	stop_server()
	print("Removing \"%s\"" % VDOM_CONFIG["SERVER-PIDFILE"])
	try: os.remove(VDOM_CONFIG["SERVER-PIDFILE"])
	except: pass
	print("Done")

if sys.argv[1] == "stop":
	stop_server()

if sys.argv[1] == "restart":
	restart_server()

if sys.argv[1] == "clean":
	clean()
