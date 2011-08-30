
import os, tempfile, traceback, shutil, re
from utils.exception import VDOM_exception
from storage.storage import VDOM_config
from cgi import escape

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	error = ""
	args = request.arguments().arguments()
	_send = False

	pis_login = ""
	pis_password = ""
	pis_system_guid = ""
	if "pis_login" in args and "pis_password" in args and "pis_system_guid" in args:
		try:
			from utils.system import set_virtual_card
			pis_login = args["pis_login"]
			pis_password = args["pis_password"]
			pis_system_guid = args["pis_system_guid"]
			set_virtual_card(pis_login,pis_password,pis_system_guid)
			error = "Please restart server to apply changes"
		except Exception, e:
			error = "Error: " + str(e) + "<br>\n"
		error = '<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Virtual card configuration: %s";</script>' % escape(error, quote=True)

	request.write("""<html xmlns="http://www.w3.org/1999/xhtml">
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
%s
</head>

<body>
<center>
<p align="left"><span class="Texte"><a href="config.py">Configuration</a> &gt; Virtual Card</span></p>
<form method="post" action="" enctype="multipart/form-data">
      <table border="0">
        <tr>
          <td class="Style2"><div align="right">PIS login : 
          </div></td>
          <td><input type="text" name="pis_login" value="%s"/>
          </td>
	</tr>
	</tr>
          <td class="Style2"><div align="right">PIS password :
          </div></td>
          <td><input type="password" name="pis_password" value="%s"/>
          </td>
        </tr>
        <tr>
          <td class="Style2"><div align="right">System guid: 
          </div></td>
          <td><input type="text" name="pis_system_guid" value="%s"/>
          </td>
	</tr>
        <tr>
          <td>&nbsp;</td>
          <td align="left"><input type="submit" value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
    </table>
</form></center></body></html>""" % (error, pis_login, pis_password, pis_system_guid))

