import os, traceback, time
from utils.exception import VDOM_exception
from utils.system import *
import managers
from utils.system import get_external_drives



def run2(request, basedir):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	args = request.arguments().arguments()
	sm = managers.server_manager
	msg = ""

	if "id" in args and "" != args["id"][0] and "file" in args and "" != args["file"][0]:
		app_id = "-".join(args["id"][0].split("_"))
		file = args["file"][0]
		sm.restore_application(app_id, os.path.join(basedir, app_id, file))
		msg = "OK"

	if "sharebackup" in args and "device" in args:
		dev = args["device"][0]
		sm.sharerestore(dev)


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

<script type="text/javascript">
function LoadImgWait(){
	document.getElementById('Imgload').style.display='';
	parent.server.document.getElementById("MsgSvrInfo").innerHTML="Copying files from external device...";
}
</script>

</head>

<body>
<div id="Imgload" style="position:absolute; z-index:100; top:0px; left:0px; width:100%; height:100%; background-color:#FFFFFF; display:none" align="center"><br><br><img src="/images/loading.gif" border="0"></div>

<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; Restore</p>
""")
	request.write("""%s
<table width="100%%" height="85%%" border="0">
""" % msg)

	if "id" not in args or "" == args["id"][0]:
		request.write('<tr><td width="123">&nbsp;</td><td align="center" class="Texte">Select application to restore</td></tr>')
		l = os.listdir(basedir)
		for appid in l:
			name = "name unknown"
			try:
				obj = managers.xml_manager.get_application(appid)
				name = obj.name.encode("utf-8")
			except: pass
			a = "_".join(appid.split("-"))
			request.write('<tr><td width="123">&nbsp;</td><td class="Texte"><a href="/apprestore.py?id=%s">%s</a></td></tr>' % (a, "%s (%s)" % (name, appid)))
		request.write('<tr><td width="123">&nbsp;</td><td></td></tr>')
	elif "file" not in args or "" == args["file"][0]:
		app_id = "-".join(args["id"][0].split("_"))
		request.write('<tr><td width="40">&nbsp;</td><td align="center" class="Texte">Select backup file</td></tr>')
		l = os.listdir(os.path.join(basedir, app_id))
		for fname in l:
			info = os.stat(os.path.join(basedir, app_id, fname))
			date = time.ctime(info.st_mtime)
			request.write('<tr><td width="40">&nbsp;</td><td class="Texte"><a href="/apprestore.py?id=%s&file=%s">%s</a></td></tr>' % (args["id"][0], fname, "%s (%s)" % (fname, date)))
		request.write('<tr><td width="40">&nbsp;</td><td></td></tr>')
	
	
	request.write( "</table>" )
	
	drives = get_external_drives()
	devs = """<option value="none">None</option>"""
	devs += "".join( [ """<option %(selected)s value="%(device)s">Usb disk %(label)s</option>""" % {
			"selected": "selected" if dev["device"] == sm.backup_dev else "",
			"device": dev["device"],
			"label": dev["label"]
			} for dev in drives ] )
	request.write('<form onsubmit="LoadImgWait();" method=post action="/apprestore.py" enctype="multipart/form-data">')
	request.write('<table border="0" width="500"')
	request.write('<tr><td width="123">&nbsp;</td><td align="center" class="Texte">Box VFS backup</td></tr>')
	request.write('<tr><td width="123">&nbsp;</td><td class="Texte"> From device: <select name=device>%s</select></td></tr>' % devs)
	request.write('<tr><td width="123">&nbsp;</td><td>');
	request.write('<input type=submit name="sharebackup" value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;">')
	request.write('</td></tr></table>')
	request.write('</form>')
	


	request.write("""
</body>
</html>""")

def run(request):
	basedir = VDOM_CONFIG["BACKUP-DIRECTORY"]
	sm = managers.server_manager
	if sm.backup_dev and device_exists(sm.backup_dev):
		mountpoint = mount_device(sm.backup_dev)
		basedir = os.path.join(mountpoint, "vdombackup")
		try: os.makedirs(basedir)
		except: pass
	try:
		run2(request, basedir)
	except:
		if sm.backup_dev and device_exists(sm.backup_dev):
			umount_device(sm.backup_dev)
		raise
	if sm.backup_dev and device_exists(sm.backup_dev):
		umount_device(sm.backup_dev)
