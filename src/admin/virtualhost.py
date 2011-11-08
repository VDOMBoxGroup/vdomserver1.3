
import os, tempfile, traceback
import managers
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	args = request.arguments().arguments()
	vh = request.server().virtual_hosting()
	sites = vh.get_sites()
	allapp = managers.xml_manager.get_applications()

	if "newvhostsite" in args and "newvhost" in args:
		#add new record
		newvhost = args["newvhost"][0]
		ok = True
		for c in newvhost:
			if not (c.isalnum() or c in ".-"):
				ok = False
		if ok and newvhost is not "":
			newvhostsite = args["newvhostsite"][0]
			if "" != newvhost and newvhostsite in allapp:
				vh.set_site(newvhost, newvhostsite)
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Waiting for action";</script>')
		else:
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Incorrect virtual host name";</script>')
	else:
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Waiting for action";</script>')

	sites = vh.get_sites()

	for a in args.keys():
		if a in sites:
			val = args[a][0]
			if "" == val:
				vh.set_site(a, None)
			else:
				vh.set_site(a, val)

	if "defsite" in args:
		s = args["defsite"][0]
		if s:
			vh.set_def_site(s)
		else:
			vh.set_def_site(None)

	sites = vh.get_sites()
	defsite = vh.get_def_site()

	#request.write(str(args))
	request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>VirtualHost</title>
<style type="text/css">
.Texte {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000; }
.Style2 {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size: 11px; color: #000000; }
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}
</style>

</head>

<body topmargin="2">
<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; Virtual Host </p>
<div style="overflow:auto; width:632px; height:216px; border:0px #000000 solid;">
<table width="100%" height="85%" border="0">""")
	request.write('<form method=post action="/virtualhost.py" enctype="multipart/form-data">')
	request.write('')
	for site in sites:
		siteid = vh.get_site(site)
		obj = None
		try: obj = managers.xml_manager.get_application(siteid)
		except:
			if site != 0: vh.set_site(site, None)
			continue
		cont = "<option value=%s>%s</option>" % (siteid, "%s (%s)" % (obj.name.encode("utf-8"), siteid))
		for a in allapp:
			if a != siteid:
				obj = managers.xml_manager.get_application(a)
				cont += "<option value=%s>%s</option>" % (a, "%s (%s)" % (obj.name.encode("utf-8"), a))
		cont += "<option value="">Nothing</option>"
		request.write('<tr><td align="right" class="Style2">Name %s maps to :</td>\n<td><select name=%s style="font-size: 11px; font-family:tahoma">%s</select></td></tr>\n' % (site, site, cont))
	request.write('<tr><td colspan="2" align="center"><input type=submit value="Save" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td></tr>')
	request.write('</form>')
	request.write('<form method=post action="/virtualhost.py" enctype="multipart/form-data">')
	request.write('<tr><td align="right" class="Style2">Create new record </td><td><input type=text name=newvhost size="50" style="font-size: 11px; font-family:tahoma"></td>')
	request.write('<tr><td align="right" class="Style2">and map to</td>')
	cont = ""
	for a in allapp:
		obj = managers.xml_manager.get_application(a)
		cont += "<option value=%s>%s</option>" % (a, "%s (%s)" % (obj.name.encode("utf-8"), a))
	request.write('<td><select name=newvhostsite style="font-size: 11px; font-family:tahoma">%s</select></td></tr>' % cont)
	request.write('<tr><td colspan="2" align="center"><input type=submit value="Add" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td></tr>')
	request.write('</form>')
	request.write('<form method=post action="/virtualhost.py" enctype="multipart/form-data">')
	request.write('<tr><td align="right" class="Style2">Default application :</td>')
	cont = ""
	if not defsite:
		cont = "<option value="">Not set</option>"
	else:
		try:
			obj = managers.xml_manager.get_application(defsite)
			cont = "<option value=%s>%s</option>" % (defsite, "%s (%s)" % (obj.name.encode("utf-8"), defsite))
		except:
			defsite = ""
			vh.set_def_site(None)
			cont = ""
	for a in allapp:
		if a == defsite:
			continue
		obj = managers.xml_manager.get_application(a)
		cont += "<option value=%s>%s</option>" % (a, "%s (%s)" % (obj.name.encode("utf-8"), a))
	if defsite:
		cont += "<option value="">Not set</option>"
	request.write('<td><select name=defsite style="font-size: 11px; font-family:tahoma">%s</select></td></tr>' % cont)
	request.write('<tr><td colspan="2" align="center"><input type=submit value="Save" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td></tr>')
	request.write('</form>')
	request.write("""</table>
</div>
</body>
</html>""")
