
import os, tempfile, traceback, shutil, re
from utils.exception import VDOM_exception
from utils.system import *
from soap.wsdl import gen_wsdl
from local_server.local_server import send_network
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

	if "hostname" in args:
		try:
			set_hostname(args["hostname"][0])
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
	if _send:
		send_network()

	(the_ip, the_mask) = get_ip_and_mask()
	if not the_ip or not the_mask:
		the_ip = ""
		the_mask = ""
	the_gate = get_default_gateway()
	if not the_gate:
		the_gate = ""

	(the_pdns, the_sdns) = get_dns()
	
	the_hostname = get_hostname()
	if not the_hostname:
		the_hostname = ""

	smtpaddr = ""
	smtpport = ""
	smtplogin = ""
	smtpsender = ""
	smtpoverssl = 0

	if "smtpaddr" in args and "smtpport" in args and "smtplogin" in args:
		try:
			smtpaddr = args["smtpaddr"][0]
			smtpport = args["smtpport"][0] or 0
			smtplogin = args["smtplogin"][0]
			cf = VDOM_config()
			cf.set_opt_sync("SMTP-SERVER-ADDRESS", smtpaddr)
			cf.set_opt_sync("SMTP-SERVER-PORT", int(smtpport))
			cf.set_opt_sync("SMTP-SERVER-USER", smtplogin)
			if "smtpsender" in args:
				smtpsender = args["smtpsender"][0]
				cf.set_opt_sync("SMTP-SERVER-SENDER", smtpsender)
			
			if "use_ssl" in args:
				if args["use_ssl"][0] == "ssl": smtpoverssl = 1
				elif args["use_ssl"][0] == "tls": smtpoverssl = 2
				else: smtpoverssl = 0
				cf.set_opt_sync("SMTP-OVER-SSL", smtpoverssl)
				
			err_msg = managers.email_manager.check_connection()
			if err_msg:
				request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="%s";</script>' % unicode(err_msg))
			else:
				request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="SMTP Connection is OK";</script>')
		except Exception, e:
			error += "Error: " + str(e) + "<br>\n"
		

	if "setsmtppassword" in args:
		try:
			smtppassword = args["smtppassword"][0] if "smtppassword" in args else ""
			cf = VDOM_config()
			cf.set_opt_sync("SMTP-SERVER-PASSWORD", smtppassword)
		except Exception, e:
			error += "Error: " + str(e) + "<br>\n"

	nosll = ""
	usessl = ""	
	usetls = ""
	
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
		
	smtpsender = cf.get_opt("SMTP-SERVER-SENDER")
	if None == smtpsender:
		smtpsender = ""
	smtpoverssl = cf.get_opt("SMTP-OVER-SSL")
	if not smtpoverssl:
		nosll = 'checked="checked"'
	elif 1 == smtpoverssl:
		usessl = 'checked="checked"'
	elif 2 == smtpoverssl:
		usetls = 'checked="checked"'

	proxyaddr, proxyport, proxylogin, proxypass = ("", "", "", "")
	
	if "set_proxy" in args:
		if "proxyaddr" in args and "proxyport" in args and "" != args["proxyaddr"][0] and "" != args["proxyport"][0]:
				proxyaddr = args["proxyaddr"][0]
				proxyport = args["proxyport"][0]
				if "proxylogin" in args:
					proxylogin = args["proxylogin"][0]
					if "proxypass" in args:
						proxypass = args["proxypass"][0]	
		set_proxy(proxyaddr, proxyport, proxylogin, proxypass)
	
	
	proxyaddr, proxyport, proxylogin, proxypass = get_proxy()
	
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
          <td class="Style2"><div align="right">Hostname : 
          </div></td>
          <td><input type="text" name="hostname" value="%s"/>
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
          <td class="Style2"><div align="right">SMTP sender : 
          </div></td>
          <td><input type="text" name="smtpsender" value="%s"/>
          </td>
	</tr>
	<tr>
          <td class="Style2"><div align="right">No secure connection : 
          </div></td>
          <td><input type="radio" name="use_ssl" value="nossl" %s />
          </td>
	</tr>
	<tr>
          <td class="Style2"><div align="right">Use SSLv23 : 
          </div></td>
          <td><input type="radio" name="use_ssl" value="ssl" %s />
          </td>
	</tr>
	<tr>
          <td class="Style2"><div align="right">Use TLS : 
          </div></td>
          <td><input type="radio" name="use_ssl" value="tls" %s />
          </td>
	</tr>
        <tr>
          <td>&nbsp;</td>
          <td align="left"><input type="submit" value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
    </table>
</form>""" % (error, the_ip, the_mask, the_gate, the_pdns, the_sdns, the_hostname, smtpaddr, smtpport, smtplogin, smtpsender, nosll, usessl, usetls))

	request.write("""<form method="post" action="">
      <table border="0"><tr>
    <TD class="Style2"><div align="right">SMTP Password :&nbsp;</div></TD>
    <TD><INPUT value="" type="password" maxLength="20" name="smtppassword"></TD>
    <TD align="right"><input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="submit" name="setsmtppassword" id="button4" value="Set password"/></td>
  </tr></table>""")
	request.write("""<form method="post" action="" enctype="multipart/form-data">
      <table border="0">
        <tr>
          <td class="Style2"><div align="right">Proxy server address : 
          </div></td>
          <td><input type="text" name="proxyaddr" value="%s"/>
          </td>
	</tr>
	</tr>
          <td class="Style2"><div align="right">Port :
          </div></td>
          <td><input type="text" name="proxyport" value="%s"/>
          </td>
        </tr>
        <tr>
          <td class="Style2"><div align="right">Login : 
          </div></td>
          <td><input type="text" name="proxylogin" value="%s"/>
          </td>
	</tr>
	<tr>
          <td class="Style2"><div align="right">Password : 
          </div></td>
          <td><input type="password" name="proxypass" value="%s"/>
          </td>
	</tr>
        <tr>
          <td>&nbsp;</td>
          <td align="left"><input type="submit" name="set_proxy" value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
    </table>
</form>""" % (proxyaddr, proxyport, proxylogin, proxypass))

	request.write("""</center></body></html>""")
