
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")
	else:
		request.write("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>VDOM Server - Users</title>
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
body {
	margin-left: 0px;
	margin-top: 6px;
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

<body onload="MM_preloadImages('images/update-user_s.jpg','images/delete-user_s.jpg','images/add-user_s.jpg','images/update-grp_s.jpg','images/delete-grp_s.jpg','images/add-grp_s.jpg')">
<center>
<table width="635" border="0" cellspacing="3" cellpadding="0">
  <tr>
    <td width="635" height="110" align="right" valign="bottom" background="images/fond-profils.jpg"><table width="500" border="0">
      <tr>
        <td>&nbsp;</td>
        <td valign="top"><div align="center"><a href="group-new.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('AddGRP','','images/add-grp_s.jpg',1)"><img src="images/add-grp.jpg" alt="Add" name="AddGRP" width="50" height="50" border="0" id="AddGRP" /></a></div></td>
        <td>&nbsp;</td>
        <td valign="top"><div align="center"><a href="grp-modif.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('updateGRP','','images/update-grp_s.jpg',1)"><img src="images/update-grp.jpg" alt="update" name="updateGRP" width="50" height="50" border="0" id="updateGRP'" /></a></div></td>
        <td>&nbsp;</td>
        <td valign="top"><div align="center"><a href="grp-suppr.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('DeleteGRP','','images/delete-grp_s.jpg',1)"><img src="images/delete-grp.jpg" alt="Delete" name="DeleteGRP" width="50" height="50" border="0" id="DeleteGRP" /></a></div></td>
        <td>&nbsp;</td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td valign="top"><div align="center" class="Texte Style2" onmouseover="MM_swapImage('AddGRP','','images/add-grp_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="group-new.py" class="Texte-liens">Add</a></div></td>
        <td>&nbsp;</td>
        <td valign="top"><div align="center" class="Texte-liens" onmouseover="MM_swapImage('updateGRP','','images/update-grp_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="users-modif.py">Update</a></div></td>
        <td>&nbsp;</td>
        <td valign="top"><div align="center" class="Texte-liens" onmouseover="MM_swapImage('DeleteGRP','','images/delete-grp_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="grp-suppr.py">Delete</a></div></td>
        <td>&nbsp;</td>
      </tr>
    </table></td>
  </tr>
  <tr>
    <td width="635" height="110" align="right" valign="bottom" background="images/fond-users.jpg"><table width="500" border="0">
      <tr>
        <td>&nbsp;</td>
        <td><div align="center"><a href="users-ajout.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('Add','','images/add-user_s.jpg',1)"><img src="images/add-user.jpg" alt="Add" name="Add" width="50" height="50" border="0" id="add" /></a></div></td>
        <td>&nbsp;</td>
        <td><div align="center"><a href="users-modif.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('update','','images/update-user_s.jpg',1)"><img src="images/update-user.jpg" alt="update" name="update" width="50" height="50" border="0" id="update" /></a></div></td>
        <td>&nbsp;</td>
        <td><div align="center"><a href="users-suppr.py" onmouseout="MM_swapImgRestore()" onmouseover="MM_swapImage('users','','images/delete-user_s.jpg',1)"><img src="images/delete-user.jpg" alt="Delete" name="Delete" width="50" height="50" border="0" id="users" /></a></div></td>
        <td>&nbsp;</td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td valign="top"><div align="center" class="Texte Style2" onmouseover="MM_swapImage('Add','','images/add-user_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="users-ajout.py" class="Texte-liens">Add</a></div></td>
        <td>&nbsp;</td>
        <td valign="top"><div align="center" class="Texte-liens" onmouseover="MM_swapImage('update','','images/update-user_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="users-modif.py">Update</a></div></td>
        <td>&nbsp;</td>
        <td valign="top"><div align="center" class="Texte-liens" onmouseover="MM_swapImage('Delete','','images/delete-user_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="users-suppr.py">Delete</a></div></td>
        <td>&nbsp;</td>
      </tr>
    </table></td>
  </tr>
</table>
</center>
</body>
</html>

""")
