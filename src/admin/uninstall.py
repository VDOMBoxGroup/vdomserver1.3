
import os, tempfile, traceback
import managers
from utils.exception import VDOM_exception
from utils.app_management import uninstall_application

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	args = request.arguments().arguments()
	applst = managers.xml_manager.get_applications()
	vh = request.server().virtual_hosting()
	p = (None, None)
	remove_db = True if "remove_db" in args else False
	remove_ldap = True if "remove_ldap" in args else False
	remove_storage = True if "remove_storage" in args else False
	remove_res = True if "remove_res" in args else False
	for a in args.keys():
		if a:
			aid = "-".join(a.split("_"))
			if aid in applst:
				# perform uninstallation
				p = uninstall_application(aid, remove_db, remove_res, remove_storage, remove_ldap)
				# remove vhosts
				for s in vh.get_sites():
					if vh.get_site(s) == aid:
						vh.set_site(s, None)
	if p[0]:
		if p[1] != "":
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Application has been uninstalled with warnings:\n%s";</script>'%p[1])
		else:
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Application has been uninstalled";</script>')
	elif False == p[0]:
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="%s";</script>' % p[1])

	applst = managers.xml_manager.get_applications()

	request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Uninstall</title>
<style type="text/css">

.Texte {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	font-size: 12px;
	color: #000000;
}
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}
</style>
</head>

<body>
<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; UnInstall </p>
<table width="100%" height="85%" border="0">
   <tr>
     <td>
""")
	request.write('<form method=post action="/uninstall.py" enctype="multipart/form-data">')
	request.write('<table border="0">')
	for appid in applst:
		obj = managers.xml_manager.get_application(appid)
		a = "_".join(appid.split("-"))
		request.write('<tr><td width="123">&nbsp;</td><td><input type=checkbox name=%s value=%s>%s</input></td></tr>' % (a, "1", "%s (%s)" % (obj.name.encode("utf-8"), appid)))
	request.write('<tr><td width="123">&nbsp;</td><td>')
	request.write('<div id="remove_parts" style="font-size: 13px; text-align: center;"><input type=checkbox name=remove_db checked>Remove Databases</input><input type=checkbox name=remove_res checked>Remove Resourses</input><input type=checkbox name=remove_ldap checked>Remove LDAP</input> \
	<input type=checkbox name=remove_storage checked>Remove Storage</input></div>')
	request.write('<input type=submit value="Remove" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;">')
	request.write('</td></tr></table>')
	request.write('</form>')
	request.write("""</td>
   </tr>
 </table>
</body>
</html>""")
