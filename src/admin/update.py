
import os, tempfile, traceback
from cgi import escape
from util.exception import VDOM_exception
from util.app_management import update_application

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	args = request.arguments().arguments()
	if "appfile" in args and "" != args["appfile"][0]:
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Updating...";</script>')
		tmpfilename = ""
		try:
			# save file
			tmpfilename = tempfile.mkstemp(".xml", "", VDOM_CONFIG["TEMP-DIRECTORY"])
			os.close(tmpfilename[0])
			tmpfilename = tmpfilename[1]
			tmpfile = open(tmpfilename, "wb")
			tmpfile.write(args["appfile"][0])
			tmpfile.close()
			# call update function
			outp = update_application(tmpfilename, request.server().virtual_hosting())
			if None != outp[0] and "" != outp[0]:
				request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="OK, application id = %s";</script>' % outp[0])
			else:
				request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Update error";</script>')
		except Exception, e:
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Error: ' + escape(str(e), quote=True) + '<br>";</script>')
			traceback.print_exc(file=debugfile)
		try:
			os.remove(tmpfilename)
		except Exception, e:
			pass
	else:
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="";</script>')

	request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Install</title>
<style type="text/css">
.Texte {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000; }
.Style2 {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size: 12px; color: #000000; }
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}
</style>
<script language="javascript">
function LoadImgWait(){
	document.getElementById('Imgload').style.display='';
	parent.server.document.getElementById("MsgSvrInfo").innerHTML="Installing...";
}
</script>
</head>

<body>
<div id="Imgload" style="position:absolute; z-index:100; top:0px; left:0px; width:100%; height:100%; background-color:#FFFFFF; display:none" align="center"><br><br><img src="/images/loading.gif" border="0"></div>
<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; Update </p>
 <table width="100%" height="85%" border="0">
   <tr>
     <td>
<form method="post" action="/update.py" enctype="multipart/form-data">
      <table width="511" border="0">
        <tr>
          <td width="43">&nbsp;</td>
          <td width="192" class="Style2"><div align="right">Application xml file : 
          </div></td>
          <td width="262"><input style="font-family: Tahoma, Arial; font-size:x-small; border-width:1px; border-color:black;" type="file" name="appfile"/>
          </td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td><input type="submit" value="Update" onclick="LoadImgWait();" style="font-family: Tahoma, Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
    </table>
</form>
</td>
   </tr>
 </table>
</body>
</html>""")
