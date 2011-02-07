
from src.util.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")
	else:
		request.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Document sans nom</title>
<style type="text/css">

.Texte {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 14px
}
a:visited {  color: #FF0000; text-decoration: none}
a:link {  color: #FF0000; text-decoration: none}
a:hover {  color: #000000; text-decoration: none}
.Texte-liens {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #FF0000;
	font-size: 10px;
}
</style>
<script type="text/javascript">
<!--
function MM_findObj(n, d) { //v4.01
  var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
    d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
  if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
  for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document);
  if(!x && d.getElementById) x=d.getElementById(n); return x;
}
function MM_preloadImages() { //v3.0
  var d=document; if(d.images){ if(!d.MM_p) d.MM_p=new Array();
    var i,j=d.MM_p.length,a=MM_preloadImages.arguments; for(i=0; i<a.length; i++)
    if (a[i].indexOf("#")!=0){ d.MM_p[j]=new Image; d.MM_p[j++].src=a[i];}}
}
function MM_swapImgRestore() { //v3.0
  var i,x,a=document.MM_sr; for(i=0;a&&i<a.length&&(x=a[i])&&x.oSrc;i++) x.src=x.oSrc;
}
function MM_swapImage() { //v3.0
  var i,j=0,x,a=MM_swapImage.arguments; document.MM_sr=new Array; for(i=0;i<(a.length-2);i+=3)
   if ((x=MM_findObj(a[i]))!=null){document.MM_sr[j++]=x; if(!x.oSrc) x.oSrc=x.src; x.src=a[i+2];}
}
//-->
</script>
</head>

<body onload="MM_preloadImages('Images/bt-server-log_s.gif','Images/bt-bug-log_s.gif','Images/bt-user-log_s.gif')">
<center>
<p align="left" class="Texte">Log </p>
<table width="565" border="0">
  <tr>
    <td>&nbsp;</td>
    <td width="108"><div align="center"><a href="log-server.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('server','','Images/bt-server-log_s.gif',1)"><img src="Images/bt-server-log.jpg" alt="Server" name="server" width="100" height="100" border="0" id="server" /></a></div></td>
    <td>&nbsp;</td>
    <td width="119"><div align="center"><a href="log-bug.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('bug','','Images/bt-bug-log_s.gif',1)"><img src="Images/bt-bug-log.jpg" alt="Bug" name="bug" width="100" height="100" border="0" id="bug" /></a></div></td>
    <td>&nbsp;</td>
    <td width="101"><div align="center"><a href="log-users.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('users','','Images/bt-user-log_s.gif',1)"><img src="Images/bt-user-log.jpg" alt="Users" name="users" width="100" height="100" border="0" id="users" /></a></div></td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td width="108" valign="top"><div align="center" class="Texte Style2" onmouseover="MM_swapImage('server','','Images/bt-server-log_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="log-server.py" class="Texte-liens">Server</a></div></td>
    <td>&nbsp;</td>
    <td width="119" valign="top"><div align="center" class="Texte-liens" onmouseover="MM_swapImage('bug','','Images/bt-bug-log_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="log-bug.py">Bug</a></div></td>
    <td>&nbsp;</td>
    <td width="101" valign="top"><div align="center" class="Texte-liens" onmouseover="MM_swapImage('users','','Images/bt-user-log_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="log-users.py">Users</a></div></td>
    <td>&nbsp;</td>
  </tr>
</table>
</center>
</body>
</html>""")
