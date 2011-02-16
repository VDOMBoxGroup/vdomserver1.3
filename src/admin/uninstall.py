
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
	p = True
	for a in args.keys():
		if a:
			aid = "-".join(a.split("_"))
			if aid in applst:
				# perform uninstallation
				p = uninstall_application(aid)
				# remove vhosts
				for s in vh.get_sites():
					if vh.get_site(s) == aid:
						vh.set_site(s, None)
	if not p:
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Application has been uninstalled";</script>')
	elif True != p:
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="%s";</script>' % p)

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
	request.write('<tr><td width="123">&nbsp;</td><td>');
	request.write('<input type=submit value="Remove" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;">')
	request.write('</td></tr></table>')
	request.write('</form>')
	request.write("""</td>
   </tr>
 </table>
</body>
</html>""")
