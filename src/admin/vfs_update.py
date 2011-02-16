
import os
from utils.system import get_vfs_users
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Waiting for action";</script>')

	args = request.arguments().arguments()
	ll = get_vfs_users()
	if "passw" in args and "user" in args and args["user"][0] in ll:
		f = os.popen('/sbin/vfs_passwd "%s" "%s"' % (args["user"][0], args["passw"][0]))
		z = f.read()
		f.close()
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Password has been set";</script>')

	request.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>VFS</title>
<style type="text/css">
<!--
.Texte {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 12px
}
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}
-->
</style>
</head>

<body topmargin="2">
<p class="Texte"><a href="vfs.py">VFS users</a> &gt; Update</p><br>""")

	users = get_vfs_users()
	request.write("""<div class="Texte">""")
	if "user" in args and args["user"][0] in users:
		x = args["user"][0]
		request.write(x)
		request.write("<br>")
		request.write("""<form name="form1" method="post" action="">
<input type="password" name="passw"/>
<input type="submit" value="Set password" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"/>
<input value="%s" type="hidden" name="user"/>
</form>""" % x)
		request.write("""<form name="form2" method="post" action="vfs.py">
<input type="submit" value="Delete" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"/>
<input value="%s" type="hidden" name="deluser">
</form>""" % x)

#	f = os.popen("/sbin/vfs_users")
#	userlist = f.read()
#	f.close()
	request.write("</div>")
	request.write("""</body>
</html>""")
