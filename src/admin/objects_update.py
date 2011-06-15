
import os, tempfile, traceback, shutil, sys
from cgi import escape
from utils.exception import VDOM_exception
import managers

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	error = ""
	args = request.arguments().arguments()
	if "typefile" in args and "" != args["typefile"][0]:
		# perform installation
		try:
			tmpfilename = request.files["typefile"][0].name
			# test
			type_id = managers.xml_manager.test_type(tmpfilename)
			if type_id:
				# load type
				managers.xml_manager.unload_type(type_id)
				ret = managers.xml_manager.load_type(tmpfilename)
				modulename = "module_%s"%type_id.replace('-','_')
				if modulename in sys.modules:
					sys.modules.pop(modulename)
				managers.source_cache.clear_cache()
				#for app_id in managers.xml_manager.get_applications():
				#	app = managers.xml_manager.get_application(app_id)
				#	for obj in app.get_objects().itervalues():
				#		obj.invalidate()
				error = "OK, new type is applied immediately"
			else:
				error = "Incorrect file"
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Type update: %s";</script>' % escape(error, quote=True))
		except Exception, e:
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Type update: Error. %s";</script>' % escape(str(e), quote=True))
			request.write(traceback.format_exc())

	request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>VirtualHost</title>
<style type="text/css">
.Texte {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000; }
.Style2 {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000; }
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}
.Texte-liens {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	font-size: 10px;
}
</style>
</head>

<body>
 <p class="Texte"><a href="config.py">Configuration</a><a href="menuAppli.html"></a> &gt; <a href="objects.py">Objects</a> &gt; Update</p>
<center>
<form method="post" action="/objects-update.py" enctype="multipart/form-data">
      <table border="0">
        <tr>
          <td>&nbsp;</td>
          <td class="Style2"><div align="right">VDOM type xml file : 
          </div></td>
          <td><input type="file" name="typefile" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"/>
          </td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td><input type="submit" value="Update" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
    </table>
</form>
</center>
</body>
</html>""")
