
import os, tempfile, traceback
from cgi import escape
from utils.exception import VDOM_exception
from utils.app_management import import_application

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	args = request.arguments().arguments()
	if "appfile" in args and "appfile" in request.files and "vhname" in args and "format" in args and "" != args["appfile"][0] and "" != args["vhname"][0] and "" != args["format"][0]:
		# perform installation
		#request.write('Installing...<br><br>')
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Installing...";</script>')
		#request.write(str(args) + '<br><br>')
		vhname = args["vhname"][0].lower()
		ok = True
		for c in vhname:
			if not (c.isalnum() or c in ".-"):
				ok = False
		vh = request.server().virtual_hosting()
		if not ok:
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Incorrect virtual host name";</script>')
		elif "" != vhname and vh.get_site(vhname):
			#request.write('Virtual host name "%s" already exists' % vhname)
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Virtual host name \'%s\' already exists";</script>' % vhname)
		else:
			try:
				# #request.write(tmpfilename + "<br>")
				request.files["appfile"][0].delete = False
				request.files["appfile"][0].close()
				# call import function
				outp = import_application(request.files["appfile"][0].name,args["format"][0])
				if None != outp[0] and "" != outp[0]:
					#request.write("OK, application id = %s" % outp)
					request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="OK, application id = %s";</script>' % outp[0])
					if "" != vhname and ok:
						vh.set_site(vhname, outp[0])	# outp[0] contains the application ID
				elif "" == outp[0]:
					#request.write("This application seems to be already installed")
					request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="This application seems to be already installed";</script>')
				else:
					#request.write("Installation error")
					request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Installation error: %s";</script>' % escape(outp[1], quote=True))
			except Exception, e:
				traceback.print_exc()
				request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Error: ' + escape(str(e), quote=True) + '<br>";</script>')

	elif "appfile" in args and "vhname" in args and "format" in args:
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Incorrect parameters";</script>')
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
<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; Install </p>
 <table width="100%" height="85%" border="0">
   <tr>
     <td>
<form method="post" action="/install.py" enctype="multipart/form-data">
      <table width="511" border="0">
        <tr>
          <td width="43">&nbsp;</td>
          <td width="192" class="Style2"><div align="right">Application file or zip archive : 
          </div></td>
          <td width="262"><input style="font-family: Tahoma, Arial; font-size:x-small; border-width:1px; border-color:black;" type="file" name="appfile"/>
          </td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td class="Style2"><div align="right">Format :
          </div></td>
          <td class="Style2"><select name="format">
            <option value="xml">xml</option>
            <option value="zip">zip</option>
          </select>
		  </td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td class="Style2"><div align="right">Virtual host name :
            
          </div>
          <label> </label></td>
          <td><input type="text" name="vhname"/></td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td><input type="submit" value="Install" onclick="LoadImgWait();" style="font-family: Tahoma, Arial; font-size:x-small; border-width:1px; border-color:black;"></td>
        </tr>
    </table>
</form>
</td>
   </tr>
 </table>
</body>
</html>""")
