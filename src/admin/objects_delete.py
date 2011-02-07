
import os
from src.util.exception import VDOM_exception
import src.xml

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	error = ""

	args = request.arguments().arguments()
	applst = src.xml.xml_manager.get_types()
	p = False
	for a in args.keys():
		if a:
			aid = "-".join(a.split("_"))
			if aid in applst:
				try:
					obj = src.xml.xml_manager.get_type(aid)
					fname = os.path.split(obj.filename)[1]
					os.remove(os.path.join(VDOM_CONFIG["TYPES-LOCATION"], fname))
					p = True
				except Exception, e:
					pass
	if p: error = "Done, restart your VDOM Box for the changes to take effect"

	request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>VirtualHost</title>
<style type="text/css">
.Texte {font-family: Tahoma, Helvetica, Verdana, Arial, sans-serif; font-size: 12px; color: #000000; }
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
function MM_preloadImages() { //v3.0
  var d=document; if(d.images){ if(!d.MM_p) d.MM_p=new Array();
    var i,j=d.MM_p.length,a=MM_preloadImages.arguments; for(i=0; i<a.length; i++)
    if (a[i].indexOf("#")!=0){ d.MM_p[j]=new Image; d.MM_p[j++].src=a[i];}}
}
//-->
</script>
</head>

<body>
 <p class="Texte"><a href="config.py">Configuration</a><a href="menuAppli.html"></a> &gt; <a href="objects.py">Objects</a> &gt; Delete</p>
<center>""")

	l1 = os.listdir(VDOM_CONFIG["SOURCE-TYPES-LOCATION"])
	l2 = os.listdir(VDOM_CONFIG["TYPES-LOCATION"])
	l = src.xml.xml_manager.get_types()
	ll = []
	for type_id in l:
		obj = src.xml.xml_manager.get_type(type_id)
		fname = os.path.split(obj.filename)[1]
		if fname in l1 or fname not in l2:
			continue
		a = "_".join(type_id.split("-"))
		ll.append(("%s (%s, version %s)" % (obj.name, type_id, obj.version), a))
	ll.sort()
	request.write("""<p align="center">%s</p>""" % error)
	request.write('<form method=post action="" enctype="multipart/form-data">')
	request.write('<table border="0">')
	for item in ll:
		request.write('<tr><td>&nbsp;</td><td class="Texte"><input type=checkbox name=%s value=%s>%s</input></td></tr>' % (item[1], "1", item[0]))
	request.write('<tr><td>&nbsp;</td><td class="Texte">');
	request.write('<input type=submit value="Remove" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;">')
	request.write('</td></tr></table>')
	request.write('</form>')
	request.write("""</center></body></html>""")
