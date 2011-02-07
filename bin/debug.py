#!/usr/bin/python

"""
debug module
"""

import sys, time, os, thread, socket, shutil, select

sys.path.append("..")

from src.config import VDOM_CONFIG

def debug_listener():
	direct = VDOM_CONFIG["STORAGE-DIRECTORY"] + "/socket/socket"
	n = 0
	try:
		while True:
			os.stat(direct + str(n))
			n += 1
	except:
		pass
	name = direct + str(n)
	_s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	_s.bind(name)
	bufsize = _s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) + 1
	while True:
		try:
			ss = [_s]
			ret = select.select(ss, [], [])
			ret = ret[0]
			for r in ret:
				if r is _s:
					(string, address) = _s.recvfrom(bufsize)
					print time.strftime("%d %b %Y %H:%M:%S", time.gmtime()), ">>>"
					try:
						print string
					except:
						print "Output error"
					print '-'*80
		except Exception, e:
			print str(e)
			time.sleep(1)

thread.start_new_thread(debug_listener, ())

#from actions import actions_on_shutdown

print "VDOM server debug"
while True:
	try:
		x = raw_input()
	except KeyboardInterrupt, k:
		print "Keyboard interrupt"
		actions_on_shutdown()
		os._exit(0)
