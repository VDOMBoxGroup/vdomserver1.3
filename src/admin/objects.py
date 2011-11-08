
from utils.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")
	else:
		request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>VirtualHost</title>
<style type="text/css">
.Texte {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000; }
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}
.Texte-liens {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
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

<body onLoad="MM_preloadImages('Images/bt-objects-add_s.jpg','Images/bt-objects-delete_s.jpg')">
 <p class="Texte"><a href="config.py">Configuration</a><a href="menuAppli.html"></a> &gt; Objects </p>
<center>
<table width="565" border="0">
  <tr>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="objects-add.py" onMouseOut="MM_swapImgRestore()" onMouseOver="MM_swapImage('add2','','Images/bt-objects-add_s.jpg',1)"><img src="Images/bt-objects-add.jpg" alt="Add" name="add2" width="108" height="100" border="0"></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="objects-update.py" onMouseOut="MM_swapImgRestore()" onMouseOver="MM_swapImage('update','','Images/bt-objects_s.gif',1)"><img src="Images/bt-objects.jpg" alt="update" name="update" width="108" height="100" border="0" id="update" /></a></div></td>
    <td><div align="center"></div></td>
    <td><div align="center"><a href="objects-delete.py" onMouseOut="MM_swapImgRestore()" onMouseOver="MM_swapImage('delete2','','Images/bt-objects-delete_s.jpg',1)"><img src="Images/bt-objects-delete.jpg" alt="Delete" name="delete2" width="108" height="100" border="0"></a></div></td>
    <td><div align="center"></div></td>
    </tr>
  <tr>
    <td>&nbsp;</td>
    <td valign="top"><div align="center" onmouseover="MM_swapImage('add2','','Images/bt-objects-add_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="objects-add.py" class="Texte-liens">Add</a></div></td>
    <td><span class="Style3"></span></td>
    <td valign="top"><div align="center" class="Texte-liens" onmouseover="MM_swapImage('update','','Images/bt-objects_s.gif',1)" onmouseout="MM_swapImgRestore()"><a href="objects-update.py">Update</a></div></td>
    <td><span class="Style3"></span></td>
    <td valign="top"><div align="center" class="Texte-liens" onmouseover="MM_swapImage('delete2','','Images/bt-objects-delete_s.jpg',1)" onmouseout="MM_swapImgRestore()"><a href="objects-delete.py">Delete</a></div></td>
    <td><span class="Style3"></span></td>
    </tr>
</table>
</center>
</body>
</html>""")
