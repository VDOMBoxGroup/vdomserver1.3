
import os
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Install</title>
<style type="text/css">
.Texte {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000; }
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}
</style>
</head>
<body>
<p class="Texte"><a href="config.py">Configuration</a> &gt; Initialize hard disk </p>
<table width="100%" height="85%" border="0">
   <tr>
     <td>
       <table border="0">
        <tr>
""")

	args = request.arguments().arguments()
	if "init" in args:
		f = open("/etc/inithdd", "wt")
		f.close()
		request.write('<script type="text/javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Rebooting server";</script>')
		f = os.popen("reboot")
		outp = f.read()
		f.close()

	else:
		request.write("""
          <td width="50" height="82" >&nbsp;</td>
          <td width="236" height="82" class="Texte">Initialize hard disk and reboot the server</td>
          <td width="200" height="82" class="Texte"><input type="button" value="Proceed" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" onclick="document.location='/inithdd.py?init'"/></td>
""")

	request.write("""
        </tr>
    </table>
</td></tr>
 </table>
</body>
</html>
""")
