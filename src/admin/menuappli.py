
from utils.exception import VDOM_exception

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
.txt-liens {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #FF0000;
	font-size: 10px;
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
</head>

<body onload="MM_preloadImages('images/bt-install_s.gif','images/bt-uninstall_s.gif','images/bt-track_s.gif','images/bt-export_s.gif','images/bt-virtualhost_s.jpg','Images/bt-objects_s.gif')">
<center>
  <p align="left" class="Texte">Application Management </p>
  <table width="565" border="0">
  <tr>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="install.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('install','','images/bt-install_s.gif',1)"><img src="images/bt-install.jpg" alt="Install" name="install" border="0" id="Image6" /></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="uninstall.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('uninstall','','images/bt-uninstall_s.gif',1)"><img src="images/bt-uninstall.jpg" alt="Uninstall" name="uninstall" border="0" id="uninstall" /></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="update.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('update','','images/bt-update_s.gif',1)"><img src="images/bt-update.jpg" alt="Update" name="update" border="0" id="update" /></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="export.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('export','','images/bt-export_s.gif',1)"><img src="images/bt-export.jpg" alt="Export" name="export" border="0" id="export" /></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="virtualhost.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('virtualhost','','images/bt-virtualhost_s.jpg',1)"><img src="images/bt-virtualhost.jpg" alt="Virtual Host" name="virtualhost" border="0" id="virtualhost" /></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="appbackup.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('appbackup','','images/bt-appbackup_s.gif',1)"><img src="images/bt-appbackup.jpg" alt="Applications backup" name="appbackup" border="0" id="appbackup" /></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="apprestore.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('apprestore','','images/bt-apprestore_s.gif',1)"><img src="images/bt-apprestore.jpg" alt="Applications restore" name="apprestore" border="0" id="apprestore" /></a></div></td>
    <td><div align="center"></div></td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td valign="top"><div align="center" class="Texte Style2" onmouseover="MM_swapImage('install','','images/bt-install_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="install.py" class="txt-liens">Install</a></div></td>
    <td>&nbsp;</td>
    <td valign="top"><div align="center" class="txt-liens" onmouseover="MM_swapImage('uninstall','','images/bt-uninstall_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="uninstall.py">Uninstall</a></div></td>
    <td>&nbsp;</td>
    <td valign="top"><div align="center" class="txt-liens" onmouseover="MM_swapImage('update','','images/bt-update_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="update.py">Update</a></div></td>
    <td>&nbsp;</td>
    <td valign="top"><div align="center" class="txt-liens" onmouseover="MM_swapImage('export','','images/bt-export_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="export.py">Export</a></div></td>
    <td>&nbsp;</td>
    <td valign="top"><div align="center" class="txt-liens" onmouseover="MM_swapImage('virtualhost','','images/bt-virtualhost_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="virtualhost.py">Virtual Host</a></div></td>
    <td>&nbsp;</td>
    <td valign="top"><div align="center" class="txt-liens" onmouseover="MM_swapImage('appbackup','','images/bt-appbackup_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="appbackup.py">Applications backup</a></div></td>
    <td>&nbsp;</td>
    <td valign="top"><div align="center" class="txt-liens" onmouseover="MM_swapImage('apprestore','','images/bt-apprestore_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="apprestore.py">Applications restore</a></div></td>
    <td>&nbsp;</td>
  </tr>
</table>
</center>
</body>
</html>""")
