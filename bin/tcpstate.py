
import sys, socket, select, time, re


address="127.0.0.1"
port=10101
frame=64*1024
timeout=0.5
request="<action name=\"state\"/>"
pattern=re.compile("\s*(?:<reply>.+</reply>|<reply/>)\s*", re.DOTALL)
handler=lambda message: None


def decode(input, errors='strict'):
	decode_regex=re.compile("(?:&#(\d{1,5});)|(?:&#x(\d{1,5});)|(&\w{1,8};)")
	decode_table={"&lt;": "<", "&gt;": ">", "&quot;": "\"", "&apos;": "'", "&amp;": "&"}
	def substitute(match):
		code, xcode, entity=match.group(1, 2, 3)
		return unichr(int(code)) if code else unichr(int(xcode, 16)) if xcode else decode_table.get(entity, entity)
	output=decode_regex.sub(substitute, input)
	return output

def graph(message):
	pattern=re.compile("<reply><graph>(?P<graph>.+)</graph></reply>", re.DOTALL)
	match=pattern.match(message)
	if match:
		graph=decode(match.group("graph"))
		with open("graph.dot", "w+") as file:
			file.write(graph)


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
	elif sys.argv[1]=="-gb":
		request="<action name=\"query\"><option name=\"garbage\">%s</option></action>"
	elif sys.argv[1]=="-rr":
		if len(sys.argv)>2:
			request="<action name=\"query\"><option name=\"referrers\">%s</option></action>"%sys.argv[2]
	elif sys.argv[1]=="-rn":
		if len(sys.argv)>2:
			request="<action name=\"query\"><option name=\"referents\">%s</option></action>"%sys.argv[2]
	elif sys.argv[1]=="-g":
		if len(sys.argv)>2:
			request="<action name=\"query\"><option name=\"graph\">%s</option></action>"%sys.argv[2]
			handler=graph
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


sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(timeout)
sock.connect((address, port))
sock.send(request)
message=""
while True:
	reading, writing, erratic=select.select((sock,), (), (), timeout)
	if reading:
		chunk=sock.recv(frame)
		message+=chunk
		if pattern.match(message):
			break
print message
handler(message)
