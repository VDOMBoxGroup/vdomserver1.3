
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")
	else:
		if system_options["firmware"] == 'N/A':
			ssh = False
			vcard = False
			inithdd = False
			updatescreen = False
		elif system_options["firmware"].startswith("virtcard"):
			ssh = True
			vcard = True
			inithdd = True
			updatescreen = False
		else:#box with smartcard
			ssh = True
			vcard = False
			inithdd = True
			updatescreen = True
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

<body onload="MM_preloadImages('images/bt-objects-new_s.jpg','images/bt-track.jpg','images/ip-address_s.jpg','images/date_s.gif', 'images/acces-distance_s.jpg', 'images/screen_upgrade_s.gif', 'images/initialize_hard_disk_s.gif')">
<center>
<p align="left" class="Texte">Configuration </p>
<table width="565" border="0">
  <tr>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="ip.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('Ip','','Images/ip-address_s.jpg',1)"><img src="Images/ip-address.jpg" alt="IP" name="Ip" border="0" id="Ip" /></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="ssl_server.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('ssl','','Images/server_ssl_1.gif',1)"><img src="Images/server_ssl_0.png" alt="SSL" name="ssl" border="0" id="ssl" /></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="date.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('Date','','Images/date_s.gif',1)"><img src="Images/date.jpg" alt="Date" name="Date" border="0" id="Date" /></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="track.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('track','','images/bt-track_s.gif',1)"><img src="images/bt-track.jpg" alt="Track" name="track" border="0" id="track" /></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="objects.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('Objects','','Images/bt-objects-new_s.jpg',1)"><img src="Images/bt-objects-new.jpg" alt="Objects" name="Objects" border="0" id="Objects" /></a></div></td>
    <td><div align="center"></div></td>
    """)
		if ssh:
			request.write("""<td><div align="center"><a href="ssh.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('ssh','','images/acces-distance_s.jpg',1)"><img src="images/acces-distance.gif" alt="Remote access" name="ssh" border="0" id="ssh" /></a></div></td>
    <td><div align="center"></div></td>
    """)
		if vcard:
			request.write("""<td><div align="center"><a href="vcard.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('vcard','','images/virt_card_1.png',1)"><img src="images/virt_card_0.png" alt="Virtual card" name="vcard" border="0" id="vcard" /></a></div></td>
    <td><div align="center"></div></td>
    """)
		if updatescreen:
			request.write("""<td><div align="center"><a href="scrupg.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('screen','','images/screen_upgrade_s.gif',1)"><img src="images/screen_upgrade.jpg" alt="Screen upgrade" name="screen" border="0" id="screen" /></a></div></td>
    <td><div align="center"></div></td>
    """)
		if inithdd:
			request.write("""<td><div align="center"><a href="inithdd.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('inithdd','','images/initialize_hard_disk_s.gif',1)"><img src="images/initialize_hard_disk.jpg" alt="Initialize hard disk" name="inithdd" border="0" id="inithdd" /></a></div></td>
    <td><div align="center"></div></td>
    """)
		request.write("""</tr>
  <tr>
    <td>&nbsp;</td>
    <td valign="top"><div align="center" class="Texte Style2" onmouseover="MM_swapImage('Ip','','Images/ip-address_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="ip.py" class="Texte-liens">IP Address</a></div></td>
    <td>&nbsp;</td>
    <td valign="top"><div align="center" class="Texte Style2" onmouseover="MM_swapImage('ssl','','Images/server_ssl_1.gif',1)" onmouseout="MM_swapImgRestore()"><a href="ssl_server.py" class="Texte-liens">SSL Server</a></div></td>
    <td>&nbsp;</td>
    <td valign="top"><div align="center" class="Texte-liens" onmouseover="MM_swapImage('Date','','Images/date_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="date.py">Date</a></div></td>
    <td>&nbsp;</td>
    <td><div align="center" class="Texte-liens" onmouseover="MM_swapImage('track','','images/bt-track_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="track.py">Track</a></div></td>
    <td>&nbsp;</td>
    <td><div align="center" class="Texte-liens" onmouseover="MM_swapImage('Objects','','Images/bt-objects-new_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="objects.py">Types</a></div></td>
    <td>&nbsp;</td>
    """)
		if ssh:
			request.write("""<td><div align="center" class="Texte-liens" onmouseover="MM_swapImage('ssh','','images/acces-distance_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="ssh.py">Remote access</a></div></td>
    <td>&nbsp;</td>
    """)
		if vcard:
			request.write("""<td><div align="center" class="Texte-liens" onmouseover="MM_swapImage('vcard','','images/virt_card_1.png',1)" onmouseout="MM_swapImgRestore()"><a href="vcard.py">Virtual card</a></div></td>
    <td>&nbsp;</td>
    """)
		if updatescreen:
			request.write("""<td><div align="center" class="Texte-liens" onmouseover="MM_swapImage('screen','','images/screen_upgrade_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="scrupg.py">Screen upgrade</a></div></td>
    <td>&nbsp;</td>
    """)
		if inithdd:
			request.write("""<td><div align="center" class="Texte-liens" onmouseover="MM_swapImage('inithdd','','images/initialize_hard_disk_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="inithdd.py">Initialize hard disk</a></div></td>
    <td>&nbsp;</td>
    """)
		request.write("""</tr>
</table>
</center>
</body>
</html>""")
