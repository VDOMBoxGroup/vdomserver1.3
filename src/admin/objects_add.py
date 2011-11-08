
import os, tempfile, traceback, shutil
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
			ret = managers.xml_manager.test_type(tmpfilename)
			if None == ret:
				# load type
				ret = managers.xml_manager.load_type(tmpfilename)
				# ret[1] is a type object
				newfname = VDOM_CONFIG["TYPES-LOCATION"] + "/" + ret[1].name.lower() + ".xml"
				shutil.copyfile(tmpfilename, newfname)
				managers.xml_manager.unload_type(ret[1].id)
				managers.xml_manager.load_type(newfname)
				error = "OK, restart your VDOM Box to use the new type"
			else:
				error = "This type is already installed"
		except Exception, e:
			request.write("Error: " + str(e) + "<br>")
			debug(traceback.format_exc())

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
 <p class="Texte"><a href="config.py">Configuration</a><a href="menuAppli.html"></a> &gt; <a href="objects.py">Objects</a> &gt; Add</p>""")
	request.write("""<center>
<p align="center">%s</p>
<form method="post" action="" enctype="multipart/form-data">
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
          <td><input type="submit" value="Install" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
    </table>
</form>
</center>
</body>
</html>""" % error)
