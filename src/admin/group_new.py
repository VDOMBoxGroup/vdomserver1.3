
import managers
from util.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")
	else:
		args = request.arguments().arguments()
		error = ""
		if "group_name" in  args and "description" in args and "" != args["group_name"][0]:
			name = args["group_name"][0]
			descr = args["description"][0]
			try:
				managers.user_manager.create_group(name, descr)
			except Exception, e:
				error = str(e)

		request.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Options</title>
<style type="text/css">
<!--
.Texte-page {
	font-family: Tahoma;
	font-weight: normal;
	font-size: 12px;
}
.Texte {	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	color: #000000;
	font-size: 14px
}
a:link {
	color: #000000;
}
a:visited {
	color: #000000;
}
-->
</style>
</head>

<body>
<p><span class="Texte"><a href="users.py">Users</a> &gt; Add profile</span></p>
<p align="center">%s</p>
<form name="form1" method="post" action="">
<table align="center" cellpadding="0" cellspacing="0">
  <TR>
    <TD align="right"><span class="Texte-page">Group name:</span></TD>
    <TD><INPUT style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" maxLength="50" size="30" name="group_name">
      

       
      <strong>*</strong> </TD>
  </TR>
  <TR>
    <TD style="vertical-align: top;" align="right"><span class="Texte-page">Description:</span></TD>
    <TD><textarea style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" cols="50" rows="5" name="description"></textarea>
    </TD>
  </TR>
  <TR>
    <TD align="right"><label></label>
      <label></label></TD>
    <TD><input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="submit" name="button2" id="button2" value="OK">
      <input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="reset" name="button" id="button" value="Reset"></TD>
  </TR>
</table>
<br>
</form>
</body>
</html>""" % error)
