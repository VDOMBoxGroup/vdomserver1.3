import sys, socket

address="10.45.0.188"#"37.59.192.245"#"127.0.0.1" 
port=10101
frame=64*1024
timeout=10
request="<action name=\"state\"/>" 

if len(sys.argv)>1:
    if sys.argv[1]=="-p":
        request="<action name=\"ping\"/>" 
    elif sys.argv[1]=="-t":
        if len(sys.argv)>2:
            request="<action name=\"state\"><option name=\"thread\">%s</option></action>"%sys.argv[2]
    elif sys.argv[1]=="-o":
        request="<action name=\"analyse\"><option name=\"objects\"/></action>" 
    elif sys.argv[1]=="-g":
        request="<action name=\"analyse\"><option name=\"garbage\"/></action>" 
    elif sys.argv[1]=="-a":
        if len(sys.argv)>2:
            address=sys.argv[2]
sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(timeout)
sock.sendto(request, (address, port))
message, address=sock.recvfrom(frame)
print message