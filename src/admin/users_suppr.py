
import managers
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")
	else:
		DelUser = 0
		args = request.arguments().arguments()
		for uid in args.keys():
			u = managers.user_manager.get_user_by_id(uid)
			if u:
				managers.user_manager.remove_user(u.login)
				request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="The user %s is removed";</script>' % u.login)
				DelUser = 1
		if DelUser != 1:	
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Waiting for action";</script>')

		request.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Options</title>
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
<p class="Texte"><a href="users.py">Users</a> &gt; Delete user</p>
<div style="overflow:auto; width:630px; height:210px; border:0px #000000 solid;">
<table width="100%" border="0" align="center" cellspacing="0" cellpadding="0">""")
	request.write('<form method=post action="" enctype="multipart/form-data">')
	userlist = managers.user_manager.get_all_users()
	for u in userlist:
		s = ""
		if u.system:
			s = "disabled"
		request.write('<tr><td align="right"><input type=checkbox name="%s" value="%s" %s /></td>' % (u.id, "1", s))
		request.write('<td class="Texte">')
		if u.system:
			request.write('<b>')
		request.write('%s (%s %s)' % (u.login, u.first_name, u.last_name))
		if u.system:
			request.write('</b>')
		request.write('</td></tr>')
	request.write('<tr><td colspan="2" align="center"><input type=submit value="Remove" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td></tr>')
	request.write('</form>')
	request.write("""</table></div>
</body>
</html>""")
