import sys, socket
from xml.dom.minidom import parseString
from cStringIO import StringIO

server="10.45.0.188" 
port=10101
frame=64*1024
timeout=10
request="<action name=\"state\"/>" 

if len(sys.argv)>1:
#    if sys.argv[1]=="-p":
#        request="<action name=\"ping\"/>" 
#    elif sys.argv[1]=="-t":
#        if len(sys.argv)>2:
#            request="<action name=\"state\"><option name=\"thread\">%s</option></action>"%sys.argv[2]
#    elif sys.argv[1]=="-o":
#        request="<action name=\"analyse\"><option name=\"objects\"/></action>" 
#    elif sys.argv[1]=="-g":
#        request="<action name=\"analyse\"><option name=\"garbage\"/></action>" 
    if sys.argv[1]=="-a":
        if len(sys.argv)>2:
            server=sys.argv[2]

res_buf = StringIO()
mbuffer = StringIO()
res_buf.write("<ThreadWatcher>")
sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(timeout)
sock.sendto(request, (server, port))
while 1:
    try:
        if mbuffer.getvalue().endswith("</reply>"):
            break
        data, address = sock.recvfrom(frame)
        if not data: break
        mbuffer.write(data)
    except socket.timeout:
        break
message = mbuffer.getvalue()
mbuffer.close()
document = parseString(message)
nodeList = document.getElementsByTagName("thread")
threadList = []
for node in nodeList:
    threadName = node.getAttribute("name")
    if threadName.startswith("Thread-"):
        threadID = node.getAttribute("id")
        threadList.append(threadID)
for thread_id in threadList:
    request = "<action name=\"state\"><option name=\"thread\">%s</option></action>"%thread_id
    try:
        sock.sendto(request, (server, port))
        message, address=sock.recvfrom(frame)
        if not message:
            message = ""
    except:
        message = ""
    res_buf.write(message)
res_buf.write("</ThreadWatcher>")
pre_res = res_buf.getvalue()
res_buf.close()
document = parseString(pre_res)
nodeList = document.getElementsByTagName("thread")
res_buf = StringIO()
res_buf.write("<reply>")
for node in nodeList:
    res_buf.write("""
    <thread id=%s name=%s
       """%(node.getAttribute("id"), node.getAttribute("name")))
    stackNode = node.firstChild
    frame = stackNode.lastChild
    res_buf.write(frame.toxml())
    res_buf.write("""
    </thread>""")
res_buf.write("\n</reply>")
result = res_buf.getvalue()
res_buf.close()
print result
