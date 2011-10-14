
import os, tempfile, traceback, shutil, re
from utils.exception import VDOM_exception
from utils.system import get_date_and_time

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	error = ""
	args = request.arguments().arguments()
	if "datestr" in args and "" != args["datestr"][0]:
		try:
			s = args["datestr"][0]
			#s = s.replace(" ", "-")
			if not re.match( "^([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})$", s):
				raise Exception("Wrong Date format!")
			f = os.popen("""date -s  "%s" """ % (s))
			outp = f.read()
			f.close()

			f = os.popen("hwclock -w")
			outp = f.read()
			f.close()

		except Exception, e:
			error = "Error: " + str(e)

	the_date = get_date_and_time()
	if None == the_date:
		the_date = ""

	request.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Document sans nom</title>
<style type="text/css">
a:link {
	color: #000000
}
a:hover {  color: #000000; text-decoration: none}
a:visited {
	color: #000000;
}
.Texte-liens {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 10px;
}
.Texte {	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 14px;
}
.Style2 {	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 14px;
}
</style>
</head>

<body>
<center>
<p align="left"><span class="Texte"><a href="config.py">Configuration</a> &gt; Date</span></p>
<p align="center">%s</p>
<form method="post" action="" enctype="multipart/form-data">
      <table border="0">
        <tr>
          <td class="Style2"><div align="right">Date : 
          </div></td>
          <td><input type="text" name="datestr" value="%s"/>
          </td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td align="left"><input type="submit" value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
    </table>
</form>
</center>
</body>
</html>""" % (error, the_date))
