
import os, re
from src.util.system import get_vfs_users
from src.util.exception import VDOM_exception

rexp_ban = [re.compile("^debug$", re.IGNORECASE)]

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Waiting for action";</script>')

	args = request.arguments().arguments()
	ll = get_vfs_users()
	if "newname" in args and args["newname"][0] and args["newname"][0] not in ll:
		ban = False
		x = args["newname"][0]
		for r in rexp_ban:
			if r.match(x):
				ban = True
				break
		if not ban:
			f = os.popen('/sbin/vfs_adduser "%s"' % x)
			z = f.read()
			f.close()
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="User has been added";</script>')
		else:
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="User name is incorrect";</script>')
	elif "deluser" in args and args["deluser"][0] in ll:
		f = os.popen('/sbin/vfs_deluser "%s"' % args["deluser"][0])
		z = f.read()
		f.close()
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="User has been removed";</script>')

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
<p class="Texte">VFS users</p>""")
	ll = get_vfs_users()
	request.write("""<div class="Texte">""")
	for s in ll:
		request.write("""<a href="/vfs_update.py?user=%s">%s</a><br>""" % (s, s))
	request.write("""<br><form name="form1" method="post" action="">
<input type="text" name="newname"/>
<input type="submit" value="Create user" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"/>
</form>""")
	request.write("</div>")
	request.write("""</body>
</html>""")
