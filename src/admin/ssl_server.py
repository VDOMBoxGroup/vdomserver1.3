import os, traceback
import managers

def run(request):
        sess = request.session()
        if not sess.value("appmngmtok"):
                request.write("Authentication failed")
                raise VDOM_exception("Authentication failed")
        
	args = request.arguments().arguments()
        ssl_on = True
	if "del_keys" in args: ssl_on = False
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
		request.write("""<body>
<p class="Texte"><a href="config.py">Configuration</a> &gt; SSL Server </p>
<table width="100%" height="85%" border="0">
   <tr>
     <td>
       <table border="0">
        <tr>
          <td width="50" height="82" >&nbsp;</td>
          <td width="86" height="82" class="Texte"><a href="/ssl_server.py?modify"><img src="images/bt-on.jpg" width="86" height="82" border="0"></a></td>
          <td width="200" height="82" class="Texte">SSL : activated</td>
        </tr>
    </table>
</td>""")
	else:
		request.write("""<body>
<p class="Texte"><a href="config.py">Configuration</a> &gt; SSL Server </p>
<table width="100%" height="85%" border="0">
   <tr>
     <td>
       <table border="0">
        <tr>
          <td width="50" height="82" >&nbsp;</td>
          <td width="86" height="82" class="Texte"><a href="/ssl_server.py?modify"><img src="images/bt-off.jpg" width="86" height="82" border="0"></a></td>
          <td width="200" height="82" class="Texte">SSL : deactivated</td>
        </tr>
    </table>
</td>""")
        request.write("""<td>
<p class="Texte"><a href="ssl_server.py?del_keys">delete keys</a></p>""")
	if ssl_on:
		request.write("""
<form method=post action="/track.py" enctype="multipart/form-data">
      <table border="0">
        <tr>
	  <td class="Texte"><div align="right">key :
	  </div></td>
	  <td><input name="key" type="file" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"/>
          </td>
        </tr>""")
		request.write("""
        <tr>
	  <td class="Texte"><div align="right">cert :
	  </div></td>
	  <td><input name="cert" type="file" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"/>
          </td>
        </tr>""")
		request.write("""
        <tr>
	  <td class="Texte"><div align="right">ca :
	  </div></td>
	  <td><input name="ca" type="file" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"/>
          </td>
        </tr>""")
		request.write("""
	<tr>
	  <td><input name="btn_tags" type=submit value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
	</tr>  
      </table>
</form>""")
	request.write("""</td>
</tr>
</table>
</body>
</html>""")