
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
	show_form = ""
	if "init" in args:
		os.system( "/usr/local/etc/init.d/card_process restart" )
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Reinitializing Virtcard process...";</script>')
	elif "pis_login" in args and "pis_password" in args:
		try:
			from utils.system import login_virtual_card
			pis_login = args["pis_login"][0]
			pis_password = args["pis_password"][0]
			syst_list = login_virtual_card(pis_login,pis_password)
			sess.value("s_pis_login",pis_login) 
			sess.value("s_pis_password",pis_password)
			systems = "".join(["<option value=%s>%s</option>" %(s_id, s_name) for (s_id, s_name) in syst_list])
			show_form = template_systems % (systems,)
		except Exception as e:
			error = unicode(e) + u"\n"
			show_form = template_login
			
	elif "system_key" in args:
		try:
			from utils.system import set_virtual_card_key
			system_key = args["system_key"][0]
			error = set_virtual_card_key(system_key)
			if not error:
				error = "Timeout"
		except Exception as e:
			error = unicode(e) + u"\n"
			show_form = template_login
		show_form = template_login

	elif "pis_system_guid" in args and sess.value("s_pis_login") and sess.value("s_pis_password"):
		try:
			from utils.system import set_virtual_card_key
			pis_login = sess.value("s_pis_login")
			pis_password = sess.value("s_pis_password")
			pis_system_guid = args["pis_system_guid"][0]
			error = set_virtual_card_key(pis_system_guid)
			if not error:
				error = "Timeout"
		except Exception as e:
			error = unicode(e) + u"\n"
			show_form = template_login
		show_form = template_login
	else:
		show_form = template_login
	error = u'<script type="text/javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Virtual card configuration: %s";</script>' % escape(error.strip(), quote=True)
	request.write((template_page%(error,show_form)).encode("utf-8"))
	
	
template_login = u"""<form method="post" action="" enctype="multipart/form-data">
      <table border="0">
        <tr>
          <td class="Style2"><div align="right">PIS login : 
          </div></td>
          <td><input type="text" name="pis_login" value=""/>
          </td>
	</tr>
	</tr>
          <td class="Style2"><div align="right">PIS password :
          </div></td>
          <td><input type="password" name="pis_password" value=""/>
          </td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td align="left"><input type="submit" value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
    </table>
</form>

<form method="post" action="" enctype="multipart/form-data">
      <table border="0">
        <tr>
          <td class="Style2"><div align="right">License key : 
          </div></td>
          <td><input type="text" name="system_key" value=""/>
          </td>
	</tr>
        <tr>
          <td>&nbsp;</td>
          <td align="left"><input type="submit" value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
         <tr>
          <td height="82" class="Texte">Reinitialize Virtcard</td>
          <td height="82" class="Texte"><input type="button" value="Proceed" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" onclick="if(confirm('Do you want to reinitialize Virtcard process? ')){document.location='/vcard.py?init';}"/></td>
        </tr>
    </table>
</form>

<form method="post" action="" enctype="multipart/form-data">
      <table border="0">
         <tr>
          <td height="82" class="Texte">Reinitialize Virtcard</td>
          <td height="82" class="Texte"><input type="button" value="Proceed" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" onclick="if(confirm('Do you want to reinitialize Virtcard process? ')){document.location='/vcard.py?init';}"/></td>
        </tr>
    </table>
</form>

"""

template_systems = u"""<form method="post" action="" enctype="multipart/form-data">
      <table border="0">
        <tr>
          <td class="Style2"><div align="right">System guid: 
          </div></td>
          <td><select name=pis_system_guid>%s</select>
          </td>
	</tr>
        <tr>
          <td>&nbsp;</td>
          <td align="left"><input type="submit" value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
    </table>
</form>
"""
template_page = u"""<html xmlns="http://www.w3.org/1999/xhtml">
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
%s</center></body></html>"""