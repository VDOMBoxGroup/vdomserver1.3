
import os, traceback
import managers
from utils.system import get_external_drives
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	args = request.arguments().arguments()
	applst = managers.xml_manager.get_applications()
	sm = managers.server_manager

	if "history" in args and "" != args["history"][0] and "interval" in args and "" != args["interval"][0] and "device" in args:
		hist_i = int(args["history"][0])
		int_i = int(args["interval"][0])
		dev = args["device"][0]
		l = []
		for a in args.keys():
			aid = "-".join(a.split("_"))
			if aid in applst:
				l.append(aid)
		sm.cancel_backup()
		sm.configure_backup(l, hist_i, int_i, dev)
	if "sharebackup" in args and "device" in args:
		dev = args["device"][0]
		sm.sharebackup(dev)
		
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

<script language="javascript">
function LoadImgWait(){
	document.getElementById('Imgload').style.display='';
	parent.server.document.getElementById("MsgSvrInfo").innerHTML="Copying files to external device...";
}
</script>
</head>

<body>


<div id="Imgload" style="position:absolute; z-index:100; top:0px; left:0px; width:100%; height:100%; background-color:#FFFFFF; display:none" align="center"><br><br><img src="/images/loading.gif" border="0"></div>

<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; Backup</p>
<table width="100%" height="85%" border="0">
   <tr>
     <td>
""")
	request.write('<form method=post action="/appbackup.py" enctype="multipart/form-data">')
	request.write('<table border="0" width="500">')
	request.write('<tr><td width="123">&nbsp;</td><td align="center" class="Texte">Select applications to backup</td></tr>')
	for appid in applst:
		obj = managers.xml_manager.get_application(appid)
		a = "_".join(appid.split("-"))
		sss = ""
		if appid in sm.backup_app:
			sss = "checked"
		request.write('<tr><td width="123">&nbsp;</td><td class="Texte"><input type=checkbox name=%s value=%s %s>%s</input></td></tr>' % (a, "1", sss, "%s (%s)" % (obj.name.encode("utf-8"), appid)))
	devs = ""
	drives = get_external_drives()
	devs += """<option value="none">None</option>"""
	devs += "".join( [ """<option %(selected)s value="%(device)s">Usb disk %(label)s</option>""" % {
			"selected": "selected" if dev["device"] == sm.backup_dev else "",
			"device": dev["device"],
			"label": dev["label"]
			} for dev in drives ] )
			
	request.write('<tr><td width="123">&nbsp;</td><td class="Texte">History: <input type=text name=history value="%s"/></td></tr>' % str(sm.history))
	request.write('<tr><td width="123">&nbsp;</td><td class="Texte">Interval (min): <input type=text name=interval value="%s"/></td></tr>' % str(sm.interval))
	request.write('<tr><td width="123">&nbsp;</td><td class="Texte">To device: <select name=device>%s</select></td></tr>' % devs)
	request.write('<tr><td width="123">&nbsp;</td><td>');
	request.write('<input type=submit value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;">')
	request.write('</td></tr></table>')
	request.write('</form>')
	request.write("""</td>
   </tr>""")
	
	request.write('<form method="post" onsubmit="LoadImgWait();" action="/appbackup.py" enctype="multipart/form-data">')
	request.write('<table border="0" width="500"')
	request.write('<tr><td width="123">&nbsp;</td><td align="center" class="Texte">Box VFS backup</td></tr>')
	request.write('<tr><td width="123">&nbsp;</td><td class="Texte">To device: <select name=device>%s</select></td></tr>' % devs)
	request.write('<tr><td width="123">&nbsp;</td><td>');
	request.write('<input type="submit" name="sharebackup" value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;">')
	request.write('</td></tr></table>')
	request.write('</form>')
	request.write("""</td>
   </tr>
 </table>
</body>
</html>""")
