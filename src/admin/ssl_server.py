import os, traceback
import managers
from storage.storage import VDOM_config
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	args = request.arguments().arguments()
	cf = VDOM_config()
	msg = ""
	if "modify" in args:
		if args["modify"][0] == "1":
			if not managers.file_manager.exists(managers.file_manager.CERTIFICATES,None, None, "server.cert") or \
			   not managers.file_manager.exists(managers.file_manager.CERTIFICATES,None, None, "server.pem"):
				msg = "You have not defined needed certificate files"
				cf.set_opt_sync("ENABLE-SSL", "0")
				VDOM_CONFIG_1["ENABLE-SSL"] = "0"				
			else:
				cf.set_opt_sync("ENABLE-SSL", "1")
				VDOM_CONFIG_1["ENABLE-SSL"] = "1"
				managers.server.start_secure_server()
				msg = "SSL Server is turned on."# Please reboot to apply changes."
		
		elif args["modify"][0] == "0":
			cf.set_opt_sync("ENABLE-SSL", "0")
			VDOM_CONFIG_1["ENABLE-SSL"] = "0"
			managers.server.stop_secure_server()
			msg = "SSL Server is turned off."# Please reboot to apply changes."
	elif "btn_upload_certs" in args:
		msg = ""
		if "key" in request.files:
			managers.file_manager.write(managers.file_manager.CERTIFICATES,None, None, "server.pem",request.files["key"][0])
			msg += "You installed private key file.<br/>"
		if "cert" in request.files:
			managers.file_manager.write(managers.file_manager.CERTIFICATES,None, None, "server.cert",request.files["cert"][0])
			msg += "You installed public certificate file.<br/>"
		if "ca" in request.files:
			managers.file_manager.write(managers.file_manager.CERTIFICATES,None, None, "ca.cert",request.files["ca"][0])
			msg += "You installed public certification authority file(CA, chain certificate).<br/>"
		
		msg += "Make sure that you installed all files of certificate before turning SSL on."
		
	ssl_on = True if cf.get_opt("ENABLE-SSL") == "1" else False
	if "del_keys" in args: 
		ssl_on = False
		cf.set_opt_sync("ENABLE-SSL", "0")
		VDOM_CONFIG_1["ENABLE-SSL"] = "0"		
		if managers.file_manager.exists(managers.file_manager.CERTIFICATES,None, None, "server.cert"):
			managers.file_manager.delete(managers.file_manager.CERTIFICATES,None, None, "server.cert")
		if managers.file_manager.exists(managers.file_manager.CERTIFICATES,None, None, "server.pem"):
			managers.file_manager.delete(managers.file_manager.CERTIFICATES,None, None, "server.pem")		
		if managers.file_manager.exists(managers.file_manager.CERTIFICATES,None, None, "ca.cert"):
			managers.file_manager.delete(managers.file_manager.CERTIFICATES,None, None, "ca.cert")	
		msg = "You removed your certificates files. SSL Server is turned off. Please reboot to apply changes."

	error = '<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="%s";</script>'%msg if msg else ""
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
<script type="text/javascript">
<!--
function MM_swapImgRestore() { //v3.0
  var i,x,a=document.MM_sr; for(i=0;a&&i<a.length&&(x=a[i])&&x.oSrc;i++) x.src=x.oSrc;
}
function MM_preloadImages() { //v3.0
  var d=document; if(d.images){ if(!d.MM_p) d.MM_p=new Array();
    var i,j=d.MM_p.length,a=MM_preloadImages.arguments; for(i=0; i<a.length; i++)
    if (a[i].indexOf("#")!=0){ d.MM_p[j]=new Image; d.MM_p[j++].src=a[i];}}
}

function MM_findObj(n, d) { //v4.01
  var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
    d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
  if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
  for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document);
  if(!x && d.getElementById) x=d.getElementById(n); return x;
}

function MM_swapImage() { //v3.0
  var i,j=0,x,a=MM_swapImage.arguments; document.MM_sr=new Array; for(i=0;i<(a.length-2);i+=3)
   if ((x=MM_findObj(a[i]))!=null){document.MM_sr[j++]=x; if(!x.oSrc) x.oSrc=x.src; x.src=a[i+2];}
}
//-->
</script>
</head>""")
	if ssl_on:
		request.write("""<body>{error}
<p class="Texte"><a href="config.py">Configuration</a> &gt; SSL Server </p>
<table width="100%" height="85%" border="0">
   <tr>
     <td>
       <table border="0">
        <tr>
          <td width="50" height="82" >&nbsp;</td>
          <td width="86" height="82" class="Texte"><a href="/ssl_server.py?modify=0"><img src="images/bt-on.jpg" width="86" height="82" border="0"></a></td>
          <td width="200" height="82" class="Texte">SSL : activated</td>
        </tr>
    </table>
</td>""".format(error=error))
	else:
		request.write("""<body>{error}
<p class="Texte"><a href="config.py">Configuration</a> &gt; SSL Server </p>
<table width="100%" height="85%" border="0">
   <tr>
     <td>
       <table border="0">
        <tr>
          <td width="50" height="82" >&nbsp;</td>
          <td width="86" height="82" class="Texte"><a href="/ssl_server.py?modify=1"><img src="images/bt-off.jpg" width="86" height="82" border="0"></a></td>
          <td width="200" height="82" class="Texte">SSL : deactivated</td>
        </tr>
    </table>
</td>""".format(error=error))
	if not ssl_on:	
		request.write("""<td>
<p class="Texte"><a href="ssl_server.py?del_keys">delete keys</a></p>
<form method=post action="/ssl_server.py" enctype="multipart/form-data">
      <table border="0">
        <tr>
	  <td class="Texte"><div align="right">key :
	  </div></td>
	  <td><input name="key" type="file" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"/>
          </td>
        </tr>
        <tr>
	  <td class="Texte"><div align="right">cert :
	  </div></td>
	  <td><input name="cert" type="file" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"/>
          </td>
        </tr>
        <tr>
	  <td class="Texte"><div align="right">ca :
	  </div></td>
	  <td><input name="ca" type="file" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"/>
          </td>
        </tr>
	<tr>
	  <td><input name="btn_upload_certs" type=submit value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
	</tr>  
      </table>
</form>""")
	request.write("""</td>
</tr>
</table>
</body>
</html>""")