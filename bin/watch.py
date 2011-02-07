#!/usr/bin/python

import sys, time, os, thread, socket, shutil, select

sys.path.append("..")

from src.config import VDOM_CONFIG

card_port = 4444

def send_to_card(msg):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.sendto(msg, ('localhost', int(card_port)))

def watcher():
	f = False
	while True:
		addr_try = VDOM_CONFIG["SERVER-ADDRESS"]
		if addr_try == "":
			addr_try = "localhost"
		sock = socket.socket()
		sock.settimeout(10.0)
		ok = True
		try:
			sock.connect((addr_try, VDOM_CONFIG["SERVER-PORT"]))
		except:
			ok = False
		sock.close()
		if ok:
			f = True
		if not ok and f:
			print "Restarting server"
			send_to_card("offline")
			# try to kill server process
			try:
				pidfile = open(VDOM_CONFIG["SERVER-PIDFILE"], "rt")
				pid = pidfile.read()
				pidfile.close()
				os.system("kill " + pid)
				time.sleep(1)
			except:
				print "Error"
			os.system("/usr/sbin/start-stop-daemon --start -b --chdir /vdom/bin --exec /vdom/bin/vdomsvr")
			time.sleep(1)
			send_to_card("booting")
			f = False
			time.sleep(30)
		else:
#			print "Server ok"
			time.sleep(10)

watcher()
