
import src.managers
from src.util.exception import VDOM_exception

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")
	else:
		args = request.arguments().arguments()
		error = ""
		first_name = ""
		last_name = ""
		login = ""
		password = ""
		slevel = ""
		email = ""
		group = ""
		if "last_name" in args and "first_name" in args and "login" in args and "password" in args and "slevel" in args and "email" in args and "group" in args and "" != args["last_name"][0] and "" != args["first_name"][0] and "" != args["login"][0] and "" != args["password"][0]:
			first_name = args["first_name"][0]
			last_name = args["last_name"][0]
			login = args["login"][0]
			password = args["password"][0]
			slevel = args["slevel"][0]
			email = args["email"][0]
			group = args["group"][0]
			try:
				obj = src.managers.user_manager.create_user(login, password, first_name, last_name, email, slevel)
				if "" != group:
					gr = src.managers.user_manager.get_user_by_id(group)
					if gr:
						obj.member_of.append(gr.login)
			except Exception, e:
				error = str(e)
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="The new user is created";</script>')
		else:
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Waiting for action";</script>')

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
	font-size: 12px
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
<p><span class="Texte"><a href="users.py">Users</a> &gt; Add user</span></p>
<form name="form1" method="post" action="">
<table align="center" cellpadding="2" cellspacing="0">
  <tr><td colspan="4" class="Texte-page"><b><font color="red">&nbsp;%s</font></b></td></tr>
  <TR>
    <TD align="right"><span class="Texte-page">Last name :&nbsp;</span></TD>
    <TD><INPUT value="%s" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="test" maxLength="50" size="20" name="last_name"><strong>*</strong> </TD>
    <TD align="right"><span class="Texte-page">First name :&nbsp;</span></TD>
    <TD><INPUT value="%s" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="test" maxLength="50" size="20" name="first_name"><strong>*</strong> </TD>
  </TR>
  <TR>
    <TD align="right"><span class="Texte-page">Login :&nbsp;</span></TD>
    <TD><INPUT value="%s" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="test" maxLength="20" name="login"><strong>*</strong> </TD>
    <TD align="right"><span class="Texte-page">Password :&nbsp;</span></TD>
    <TD><INPUT value="%s" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="password" maxLength="20" value="" name="password"><strong>*</strong> </TD>
  </TR>
  <TR>
    <TD align="right"><span class="Texte-page">E-Mail :&nbsp;</span></TD>
    <TD colsapn="3"><INPUT value="%s" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" name="email" size="30"></TD>
  </TR>
  <TR>
    <TD align="right"><span class="Texte-page">Security level :&nbsp;</span></TD>
    <TD><INPUT value="%s" style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" maxLength="20" name="slevel"></TD>
  </TR>""" % (error, first_name, last_name, login, password, email, slevel))

		cont = "<option value=\"\"></option>"
		groups = src.managers.user_manager.get_all_groups()
		for g in groups:
			if group == g.id:
				slctd = "selected"
			else:
				slctd = ""
			cont += "<option value=""%s"" %s>%s</option>" % (g.id, slctd, g.login)

		request.write("""<TR>
    <TD align="right"><span class="Texte-page">Group :&nbsp;</span></TD>
    <TD style="border: solid 1px white; vertical-align: middle;"><select name="group">%s</select>""" % cont)

		request.write("""</td></tr>
""")

		request.write("""<TR>
    	<td></td>
	<TD align="right"><input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="submit" name="button2" id="button2" value="OK"></td>
	<td><input style="font-family:Arial; font-size:x-small; border-width:1px; border-color:black;" type="reset" name="button" id="button" value="Reset"></TD>
	</td>
  </TR>
</table>
</form>
</body>
</html>""")
