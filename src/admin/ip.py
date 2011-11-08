
import os, tempfile, traceback, shutil, re
from utils.exception import VDOM_exception
from utils.system import *
from soap.wsdl import gen_wsdl
# from server.local_server import send_network
from storage.storage import VDOM_config

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	error = ""
	args = request.arguments().arguments()
	_send = False

	rexp1 = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", re.IGNORECASE | re.DOTALL)

	if "ipaddr" in args and "" != args["ipaddr"][0] and "netmask" in args and "" != args["netmask"][0]:
		try:
			if None != rexp1.match(args["ipaddr"][0]) and None != rexp1.match(args["netmask"][0]):
				(_i_old, _m_old) = get_ip_and_mask()

				set_ip_and_mask(args["ipaddr"][0], args["netmask"][0])

				(_i, _m) = get_ip_and_mask()
				if _i == args["ipaddr"][0] and _m == args["netmask"][0]:
					f = open("/etc/ip", "w")
					f.write(args["ipaddr"][0] + " netmask " + args["netmask"][0])
					f.close()
				_send = True
		except Exception, e:
			error += "Error: " + str(e) + "<br>\n"

	if "pdns" in args and "sdns" in args:
		try:
			set_dns(args["pdns"][0], args["sdns"][0])
			_send = True
		except Exception, e:
			error += "Error: " + str(e) + "<br>\n"

	if "gateway" in args and "" != args["gateway"][0]:
		try:
			_old = get_default_gateway()
			_new = args["gateway"][0]
			if _new != _old:
				set_default_gateway(_new)
				f = open("/etc/gateway", "w")
				f.write(_new)
				f.close()
				_send = True
		except Exception, e:
			error += "Error: " + str(e) + "<br>\n"

	# CARD INTERFACE TEMPORARILY REMOVED
	# if _send:	
	#	send_network() 

	(the_ip, the_mask) = get_ip_and_mask()
	if not the_ip or not the_mask:
		the_ip = ""
		the_mask = ""
	the_gate = get_default_gateway()
	if not the_gate:
		the_gate = ""

	(the_pdns, the_sdns) = get_dns()

	smtpaddr = ""
	smtpport = ""
	smtplogin = ""

	if "smtpaddr" in args and "smtpport" in args and "" != args["smtpport"][0] and "smtplogin" in args:
		try:
			smtpaddr = args["smtpaddr"][0]
			smtpport = args["smtpport"][0]
			smtplogin = args["smtplogin"][0]
			cf = VDOM_config()
			cf.set_opt_sync("SMTP-SERVER-ADDRESS", smtpaddr)
			cf.set_opt_sync("SMTP-SERVER-PORT", int(smtpport))
			cf.set_opt_sync("SMTP-SERVER-USER", smtplogin)
		except Exception, e:
			error += "Error: " + str(e) + "<br>\n"

	if "smtppassword" in args:
		try:
			smtppassword = args["smtppassword"][0]
			cf = VDOM_config()
			cf.set_opt_sync("SMTP-SERVER-PASSWORD", smtppassword)
		except Exception, e:
			error += "Error: " + str(e) + "<br>\n"

	cf = VDOM_config()
	smtpaddr = cf.get_opt("SMTP-SERVER-ADDRESS")
	if None == smtpaddr:
		smtpaddr = ""
	smtpport = str(cf.get_opt("SMTP-SERVER-PORT"))
	if None == smtpport:
		smtpport = ""
	smtplogin = cf.get_opt("SMTP-SERVER-USER")
	if None == smtplogin:
		smtplogin = ""

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
<p align="left"><span class="Texte"><a href="config.py">Configuration</a> &gt; IP</span></p>
<p align="center">%s</p>
<form method="post" action="" enctype="multipart/form-data">
      <table border="0">
        <tr>
          <td class="Style2"><div align="right">IP address : 
          </div></td>
          <td><input type="text" name="ipaddr" value="%s"/>
          </td>
        </tr>
        <tr>
          <td class="Style2"><div align="right">Network mask : 
          </div></td>
          <td><input type="text" name="netmask" value="%s"/>
          </td>
        </tr>
        <tr>
          <td class="Style2"><div align="right">Gateway : 
          </div></td>
          <td><input type="text" name="gateway" value="%s"/>
          </td>
        </tr>
        <tr>
          <td class="Style2"><div align="right">Primary DNS : 
          </div></td>
          <td><input type="text" name="pdns" value="%s"/>
          </td>
        </tr>
        <tr>
          <td class="Style2"><div align="right">Secondary DNS : 
          </div></td>
          <td><input type="text" name="sdns" value="%s"/>
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
          <td class="Style2"><div align="right">SMTP server address : 
          </div></td>
          <td><input type="text" name="smtpaddr" value="%s"/>
          </td>
	</tr>
	</tr>
          <td class="Style2"><div align="right">port :
          </div></td>
          <td><input type="text" name="smtpport" value="%s"/>
          </td>
        </tr>
        <tr>
          <td class="Style2"><div align="right">SMTP login : 
          </div></td>
          <td><input type="text" name="smtplogin" value="%s"/>
          </td>
	</tr>
        <tr>
          <td>&nbsp;</td>
          <td align="left"><input type="submit" value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
    </table>
</form>""" % (error, the_ip, the_mask, the_gate, the_pdns, the_sdns, smtpaddr, smtpport, smtplogin))

	request.write("""<form method="post" action="">
      <table border="0"><tr>
    <TD class="Style2"><div align="right">SMTP Password :&nbsp;</div></TD>
    <TD><INPUT value="" type="password" maxLength="20" name="smtppassword"></TD>
    <TD align="right"><input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="submit" name="button4" id="button4" value="Set password"/></td>
  </tr></table>""")

	request.write("""</center></body></html>""")
