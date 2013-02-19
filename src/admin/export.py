
import os, tempfile, traceback, shutil, time, re
from utils.exception import VDOM_exception
from utils.system import get_external_drives, device_exists, mount_device, umount_device
import managers

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	applist = managers.xml_manager.get_applications()
	pathval = ""

	args = request.arguments().arguments()
	if "appl" in args and "format" in args and "" != args["appl"][0] and "" != args["format"][0] and "device" in args and "none" == args["device"][0]:
		# create temp path
		path = tempfile.mkdtemp("", "", VDOM_CONFIG["TEMP-DIRECTORY"])
		appl = args["appl"][0]
		format = args["format"][0].lower()
		embedtypes = bool(args["embedtypes"][0] == "1") if "embedtypes" in args else False
		f = None
		if appl in applist and format in ["xml", "zip"]:
			try:
				managers.xml_manager.export_application(appl, format, path, embedtypes)
				toread = os.path.join(path, appl)
				a = managers.xml_manager.get_application(appl)
				name = a.name
				ver = ""
				if a.version: ver = "_ver_%s" % re.sub('\D', '_', a.version)
				request.add_header("Content-Type", "application/octet-stream");
				request.add_header("Content-Disposition", "attachment; filename=%s%s.%s" % (name, ver, format));
				toread = ".".join([toread, format])
				f = open(toread, "rb")
				request.set_nocache()
				while True:
					data = f.read(65536)
					if not data:
						break
					request.write(data)
				f.close()
				f = None
			except Exception, e:
				#request.write("Error: " + str(e) + "<br>")
				#request.write(traceback.format_exc())
				traceback.print_exc(file=debugfile)
			finally:
				if f:
					f.close()
				shutil.rmtree(path)
		else:
			request.write("Incorrect arguments<br><br>")
	else:
		if "appl" in args and "format" in args and "" != args["appl"][0] and "" != args["format"][0] and "device" in args and "none" != args["device"][0] and "" != args["device"][0]:
			path = tempfile.mkdtemp("", "", VDOM_CONFIG["TEMP-DIRECTORY"])
			appl = args["appl"][0]
			format = args["format"][0].lower()
			dev = args["device"][0]
			embedtypes = bool(args["embedtypes"][0] == "1") if "embedtypes" in args else False
			if appl in applist and format in ["xml", "zip"] and device_exists(dev):
				try:
					managers.xml_manager.export_application(appl, format, path, embedtypes)
					fname = os.path.join(path, appl)
					fname += ("." + format)
					mountpoint=mount_device(dev)
					shutil.copyfile(fname, "%s/%s" % (mountpoint, appl + "_" + str(int(time.time())) + "." + format))
					time.sleep(1)
					umount_device(dev)
				except Exception, e:
					#request.write("Error: " + str(e) + "<br>")
					#request.write(traceback.format_exc())
					traceback.print_exc(file=debugfile)
				finally:
					shutil.rmtree(path)
			else:
				request.write("Incorrect arguments<br><br>")

		request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Export</title>
<style type="text/css">
.Texte {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000; }
.Style2 {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000; }
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}
</style>

<script type="text/javascript" language="JavaScript">
function zzzz(e) {
	var isIE  = (navigator.appVersion.indexOf("MSIE") != -1) ? true : false;
	if(isIE)
	{
		e.returnValue=false;
		e.cancelBubble=true;
	}
	else
	{
		e.preventDefault();
		e.stopPropagation();
	}
	document.getElementById('theform').style.display='none';
	document.getElementById('theimage').innerHTML='<center><img src="images/loading.gif"/></center>';
	document.getElementById('theserver').src='http://mail.ru';
	return false;
}
</script>
</head>

<body>
<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; Export </p>
 <table width="100%" height="85%" border="0">
   <tr>
     <td>
""")
		request.write("""<div id="theimage"></div><div id="theform"><form method="post" action="/export.py" target="options" enctype="multipart/form-data"><span class="Style2">
	<table width="511" border="0"><tr><td width="36">&nbsp;</td><td width="131"></td></tr>
	<tr><td>&nbsp;</td><td><div align="right" class="Style2">Application&nbsp;:</div></td>""")
		cont = ""
		for a in applist:
			obj = managers.xml_manager.get_application(a)
			cont += "<option value=%s>%s</option>" % (a, "%s (%s)" % (obj.name.encode("utf-8"), a))
		drives = get_external_drives()
		devs = """<option value="none">None</option>"""
		devs += "".join( [ """<option  value="%(device)s">Usb disk %(label)s</option>""" % dev for dev in drives ] )

		request.write("""<td class="Style2"><select name=appl>%s</select></td></tr>
	<tr><td>&nbsp;</td><td><div align="right" class="Style2">Format&nbsp;:</div></td>
	<td class="Style2"><select name="format"><option value=xml>xml</option><option value=zip>zip</option></select></td></tr>

	<tr><td>&nbsp;</td><td><div align="right" class="Style2">To device&nbsp;:</div></td>
	<td class="Style2"><select name="device">%s</select></td></tr>
	
	<tr><td>&nbsp;</td><td><div align="right" class="Style2">Embed types in xml&nbsp;:</div></td>
	<td class="Style2"><input name="embedtypes" type="checkbox" value="1"></input></td></tr>
	
	<tr><td>&nbsp;</td><td>&nbsp;</td><td><input type=submit value="Export" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td></tr>
	</table></span></form></div>""" % (cont, devs))
		request.write("""</td>
   </tr>
 </table>
</body>
</html>""")
