
import sys, socket


address="127.0.0.1"
port=10101
frame=64*1024
timeout=1
request="<action name=\"state\"/>"


if len(sys.argv)>1:
	if sys.argv[1]=="-p":
		request="<action name=\"ping\"/>"
	elif sys.argv[1]=="-th":
		if len(sys.argv)>2:
			request="<action name=\"state\"><option name=\"thread\">%s</option></action>"%sys.argv[2]
	elif sys.argv[1]=="-ob":
		if len(sys.argv)>2:
			request="<action name=\"state\"><option name=\"object\">%s</option></action>"%sys.argv[2]
	elif sys.argv[1]=="-ao":
		request="<action name=\"analyse\"><option name=\"objects\"/></action>"
	elif sys.argv[1]=="-ag":
		request="<action name=\"analyse\"><option name=\"garbage\"/></action>"
	elif sys.argv[1]=="-q":
		if len(sys.argv)>2:
			request="<action name=\"query\"><option name=\"objects\">%s</option></action>"%sys.argv[2]
	elif sys.argv[1]=="-g":
		if len(sys.argv)>2:
			request="<action name=\"query\"><option name=\"garbage\">%s</option></action>"%sys.argv[2]
	elif sys.argv[1]=="-rr":
		if len(sys.argv)>2:
			request="<action name=\"query\"><option name=\"referrers\">%s</option></action>"%sys.argv[2]
	elif sys.argv[1]=="-rn":
		if len(sys.argv)>2:
			request="<action name=\"query\"><option name=\"referents\">%s</option></action>"%sys.argv[2]
	elif sys.argv[1]=="-r":
		if len(sys.argv)>3:
			request="<action name=\"intrude\"><option name=\"raise\">%s</option><option name=\"thread\">%s</option></action>"% \
				(sys.argv[2], sys.argv[3])
	elif sys.argv[1]=="-s":
		if len(sys.argv)>2:
			request="<action name=\"intrude\"><option name=\"stop\"/><option name=\"thread\">%s</option></action>"%sys.argv[2]
	elif sys.argv[1]=="-a":
		if len(sys.argv)>2:
			address=sys.argv[2]


sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(timeout)
sock.sendto(request, (address, port))
message, address=sock.recvfrom(frame)
print message
