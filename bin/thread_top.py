# coding=utf-8
import sys, socket, time, msvcrt, os
from xml.dom.minidom import parseString
from cStringIO import StringIO

server="10.45.0.188" 
port=10101
frame=64*1024
timeout=31*86400
request="<action name=\"state\"/>" 

if len(sys.argv)>1:
	if sys.argv[1]=="-a":
		if len(sys.argv)>2:
			server=sys.argv[2]

sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(timeout)

while True:
	if msvcrt.kbhit():                  # Нажата ли клавиша?
		key = ord(msvcrt.getch())   # Какая клавиша нажата?
		if key == 13:               # если Enter:
			sys.exit()
	res_buf = StringIO()
	sock.sendto(request, (server, port))
	message, address=sock.recvfrom(frame)
	document = parseString(message)
	nodeList = document.getElementsByTagName("thread")
	for node in nodeList:
		res_buf.write("%s\n"%node.toxml())
	os.system('cls')
	print res_buf.getvalue()
	res_buf.close()
	time.sleep(1.5)