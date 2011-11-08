
def run(request):
	request.write("""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Document sans nom</title>
<style type="text/css">
<!--
.Titre-system {font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif}
.Txt {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	font-size: 12px;
}
-->
</style>
</head>

<body>
<center>
<table width="800" height="600" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td align="center" valign="middle" background="Images/fond-loggin.jpg">
    <table width="392" height="233" border="0" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center" valign="middle" background="Images/cadre-form-loggin.png">
        <table width="391" height="232" border="0" cellspacing="0" cellpadding="0">
          <tr>
            <td height="50"><span class="Titre-system">VDOM Server | system Login</span></td>
          </tr>
          <tr>
            <td>
            <form name="form1" method="post" action="/app.py">
            <table width="391" border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td width="71" height="100" rowspan="4">&nbsp;</td>
                <td align="right" valign="bottom" bgcolor="#CCCCCC">&nbsp;</td>
                <td align="left" valign="bottom" bgcolor="#CCCCCC">&nbsp;</td>
                <td width="71" height="100" rowspan="4">&nbsp;</td>
              </tr>
              <tr>
                <td width="86" height="25" align="right" valign="middle" bgcolor="#CCCCCC"><span class="Txt">Login : &nbsp;</span></td>
                <td width="163" height="25" align="left" valign="middle" bgcolor="#CCCCCC">
                  <input name="user" type="text" id="textfield" style="border-color:#CCCCCC; border-style:solid;width:142px"></td>
                </tr>
              <tr>
                <td height="25" align="right" valign="middle" bgcolor="#CCCCCC" class="Txt">Password : &nbsp;</td>
                <td height="25" align="left" valign="middle" bgcolor="#CCCCCC">
                <input name="password" type="password" id="textfield2" style="border-color:#CCCCCC; border-style:solid;width:142px"></td>
              </tr>
              <tr>
                <td align="right" valign="top" bgcolor="#CCCCCC" class="Txt">&nbsp;</td>
                <td align="left" valign="top" bgcolor="#CCCCCC">
                    <input style="border-color:#CCCCCC; border-style:solid" type="submit" name="Submit" id="Submit" value="Login">
                </td>
              </tr>
              <tr>
                <td width="71">&nbsp;</td>
                <td height="25" colspan="2">&nbsp; </td>
                <td width="71">&nbsp;</td>
              </tr>
            </table>
            </form>
            </td>
          </tr>
        </table></td>
      </tr>
    </table></td>
  </tr>
</table>
</center>
</body>
</html>""")
