
import managers
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")
	else:
		Delgrp = 0
		args = request.arguments().arguments()
		for uid in args.keys():
			u = managers.user_manager.get_user_by_id(uid)
			if u:
				managers.user_manager.remove_user(u.login)
				request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="The group %s is removed";</script>' % u.login)
				Delgrp = 1
		if Delgrp != 1:	
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
<p class="Texte"><a href="users.py">Users</a> &gt; Delete profile</p>
<div style="overflow:auto; width:630px; height:210px; border:0px #000000 solid;">
<table width="100%" border="0" align="center" cellspacing="0" cellpadding="0">
   <tr>
     <td align="center" class="Texte">""")
	request.write('<form method=post action="" enctype="multipart/form-data">')
	userlist = managers.user_manager.get_all_groups()
	for u in userlist:
		s = ""
		if u.system:
			s = "disabled"
		request.write('<tr><td align="right"><input type=checkbox name="%s" value="%s" %s></td>' % (u.id, "1", s))
		request.write('<td class="Texte">')
		if u.system:
			request.write('<b>')
		request.write('%s' % u.login)
		if u.system:
			request.write('</b>')
		request.write('</td></tr>')
	request.write('<tr><td align="center" colspan="2"><input type=submit value="Remove" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td></tr>')
	request.write('</form>')
	request.write("""</table></div>
</body>
</html>""")
