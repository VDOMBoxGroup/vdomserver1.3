
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
	if "typefile" in args and "typeid" in args and "" != args["typefile"][0] and "" != args["typeid"][0]:
		# perform installation
		type_id = "-".join(args["typeid"][0].split("_"))
		tmpfilename = ""
		try:
			# save file
			tmpfilename = tempfile.mkstemp("", "", VDOM_CONFIG["TEMP-DIRECTORY"])
			os.close(tmpfilename[0])
			tmpfilename = tmpfilename[1]
			tmpfile = open(tmpfilename, "wb")
			tmpfile.write(args["typefile"][0])
			tmpfile.close()
			# test
			ret = managers.xml_manager.test_type(tmpfilename)
			if ret == type_id:
				# load type
				ret = managers.xml_manager.load_type(tmpfilename)
				# ret[1] is a type object
				shutil.copyfile(tmpfilename, VDOM_CONFIG["TYPES-LOCATION"] + "/" + ret[1].name.lower() + ".xml")
				error = "OK, restart your VDOM Box to use the new type"
			else:
				error = "Incorrect file or selected type"
		except Exception, e:
			request.write("Error: " + str(e) + "<br>")
			request.write(traceback.format_exc())
		try:
			os.remove(tmpfilename)
		except Exception, e:
			pass

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
""")

	l = managers.xml_manager.get_types()
	cont = ""
	ll = []
	for type_id in l:
		a = "_".join(type_id.split("-"))
		obj = managers.xml_manager.get_type(type_id)
		ll.append(("%s (%s, version %s)" % (obj.name, type_id, obj.version), a))
	ll.sort()
	for item in ll:
		cont += "<option value=%s>%s</option>" % (item[1], item[0])

	request.write("""<center>
<p align="center">%s</p>
<form method="post" action="/objects-update.py" enctype="multipart/form-data">
      <table border="0">
        <tr>
          <td>&nbsp;</td>
          <td class="Style2"><div align="right">Update type : 
          </div></td>
          <td><select name="typeid">%s</select>
          </td>
        </tr>
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
</html>""" % (error, cont))
