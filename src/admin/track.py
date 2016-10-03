
import managers
from storage.storage import VDOM_config
from utils.exception import VDOM_exception
from utils.system_linux import open_debug_port, close_debug_port

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

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

	cf = VDOM_config()
	modify = False

	args = request.arguments().arguments()
	if "modify" in args:
		modify = True

	if "btn_tags" in args:
		if "enable_tags" in args:
			cf.set_opt_sync("DEBUG-ENABLE-TAGS", "1")
			VDOM_CONFIG_1["DEBUG-ENABLE-TAGS"] = "1"
		else:
			cf.set_opt_sync("DEBUG-ENABLE-TAGS", "0")
			VDOM_CONFIG_1["DEBUG-ENABLE-TAGS"] = "0"
		if "enable_page_debug" in args:
			cf.set_opt_sync("ENABLE-PAGE-DEBUG", "1")
			VDOM_CONFIG_1["ENABLE-PAGE-DEBUG"] = "1"
		else:
			cf.set_opt_sync("ENABLE-PAGE-DEBUG", "0")
			VDOM_CONFIG_1["ENABLE-PAGE-DEBUG"] = "0"
		#tags = managers.storage.read_object("DEBUG-TAGS")
		#if not tags:
		#	tags = []
		#	#managers.storage.write_object("DEBUG-TAGS", tags)
		#for a in args.keys():
		#	if a.startswith("enable_tag_"):
		#		k = a[11:]
		#		if k in tags:
		#			tags.remove(k)
		#		#cf.set_opt_sync("DEBUG-ENABLE-TAG-" + k, "1")
		#for key in tags:
		#	cf.set_opt_sync("DEBUG-ENABLE-TAG-" + key, "0")

	opt = cf.get_opt("DEBUG")
	toset = ""
	if ("0" == opt and modify) or ("0" != opt and not modify):
		toset = "1"
#		request.write("Debug is now ON")
		request.write("""<body>
<p class="Texte"><a href="config.py">Configuration</a><a href="menuAppli.html"></a> &gt; Track </p>
<table width="100%" height="85%" border="0">
   <tr>
     <td>
       <table border="0">
        <tr>
          <td width="50" height="82" >&nbsp;</td>
          <td width="86" height="82" class="Texte"><a href="/track.py?modify"><img src="images/bt-on.jpg" width="86" height="82" border="0"></a></td>
          <td width="200" height="82" class="Texte">Output track : activated</td>
        </tr>
    </table>
</td>""")

	else:
		toset = "0"
#		request.write("Debug is now OFF")
		request.write("""<body>
<p class="Texte"><a href="config.py">Configuration</a><a href="menuAppli.html"></a> &gt; Track </p>
<table width="100%" height="85%" border="0">
   <tr>
     <td>
      <table border="0">
        <tr>
          <td width="50" height="82" >&nbsp;</td>
          <td width="86" height="82" class="Texte"><a href="/track.py?modify"><img src="images/bt-off.jpg" width="86" height="82" border="0"></a></td>
          <td width="200" height="82" class="Texte">Output track : deactivated</td>
        </tr>
      </table>
     </td>""")
	if "0" == opt and modify:
		open_debug_port()
	elif "0" != opt and modify:
		close_debug_port()
	en_tag = cf.get_opt("DEBUG-ENABLE-TAGS")
	s = ""
	if "1" == en_tag:
		s = "checked"
	request.write("""<td>
<form method=post action="/track.py" enctype="multipart/form-data">
      <table border="0">
        <tr>
	  <td class="Texte"><input type=checkbox name="enable_tags" value="1" %s>Enable debug tags</input></td>
        </tr>
""" % s)

	page_debug = cf.get_opt("ENABLE-PAGE-DEBUG")
	s = ""
	if "1" == page_debug:
		s = "checked"
	request.write("""
        <tr>
	  <td class="Texte"><input type=checkbox name="enable_page_debug" value="1" %s>Enable debug in browser</input></td>
        </tr>
""" % s)

	#tags = managers.storage.read_object("DEBUG-TAGS")
	#if not tags:
		#tags = []
		#managers.storage.write_object("DEBUG-TAGS", tags)
	#for key in cf.get_keys():
		#if key.startswith("DEBUG-ENABLE-TAG-") and "1" == cf.get_opt(key):
			#k = key[17:]
			#if k in tags:
				#tags.remove(k)
			#request.write("""<tr>
	  #<td><input type=checkbox name="enable_tag_%s" value="1" checked>%s</input></td>
        #</tr>
#""" % (k, k))

	#for key in tags:
		#request.write("""<tr>
	  #<td><input type=checkbox name="enable_tag_%s" value="1">%s</input></td>
        #</tr>
#""" % (key, key))

	#request.write("""<tr><td>
#<input name="btn_tags" type=submit value="OK" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;">
#</td></tr></table></form></td>""")	

	request.write("""</tr>
 </table>
</body>
</html>
""")

	if modify:
		cf.set_opt("DEBUG", toset)
		VDOM_CONFIG_1["DEBUG"] = toset
