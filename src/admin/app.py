
import src.managers

def run(request):

	#s = src.managers.vdom_memory.new_session()
	#a = s.get_application("10000000-0000-0000-0000-000000000000")
	#print str(a.objects_list)

	passed = False

	sess = request.session()

	if sess.value("appmngmtok"):
		passed = True

	args = request.arguments().arguments()
	if not passed and "user" in args and "password" in args:
		user = src.managers.user_manager.match_user(args["user"][0], args["password"][0])
		if user and src.managers.acl_manager.check_membership(user.login, "ManagementLogin"):
			passed = True
			sess["appmngmtok"] = 1
			#sess["username"] = args["user"][0]	# TODO: fix
			sess.set_user(args["user"][0], args["password"][0], md5 = False)


	if passed:
		request.write("""
<html>
<head>
<title>VDOM Server</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<style type="text/css">
<!--
.titresystem {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	font-size: 16px;
}
.Titre-haut {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	font-size: 12px;
	color: #FFFFFF;
}
.languettes {
	font-family: Arial, Helvetica, sans-serif;
	font-size: 10px;
	color: #FFFFFF;
}
.Copright {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	font-size: 10px;
	color: #666666;
}
.control {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	font-size: 10px;
	color: #CC0000;
}
.Texte {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	font-size: 12px;
}a:visited {  color: #000000; text-decoration: none}
a:link {  color: #000000; text-decoration: none}
a:hover {  color: #000000; text-decoration: none}
-->
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
<!-- DEBUT DU SCRIPT Help-->
<SCRIPT LANGUAGE="JavaScript">
function ChangeMessage(message,champ)
  {
  if(document.getElementById)
    document.getElementById(champ).innerHTML = message;
  }
</SCRIPT>
<!-- FIN DU SCRIPT help-->
</head>
<body bgcolor="#FFFFFF" leftmargin="0" topmargin="0" marginwidth="0" marginheight="0" onLoad="MM_preloadImages('images/bt-g-users_s.png','images/bt-g-config_s.png','images/bt-g-application_s.png','images/shared-documents_s.png','images/bt-g-log_s.png','images/bt-reeboot_s.gif','images/bt-shutdown_s.gif')">


<center>
<table id="Tableau_01" width="900" height="700" border="0" cellpadding="0" cellspacing="0">
  <tr>
		<td width="900" height="90" colspan="2" valign="top" background="images/bando-haut.jpg" >
        <table width="900" height="82" border="0" cellpadding="0" cellspacing="0">
          <tr>
            <td width="27" height="15">&nbsp;</td>
            <td width="352" height="15">&nbsp;</td>
            <td width="380" height="15">&nbsp;</td>
            <td width="141" height="15">&nbsp;</td>
          </tr>
          <tr>
            <td height="29">&nbsp;</td>
            <td><span class="titresystem"><a href="/system">VDOM Server | Main</a></span></td>
            <td>&nbsp;</td>
            <td>&nbsp;</td>
          </tr>
          <tr>
            <td>&nbsp;</td>
            <td>&nbsp;</td>
            <td align="right" valign="bottom">
            <table width="150" border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td><img src="images/fr.jpg" width="25" height="17"></td>
                <td><img src="images/rus.jpg" width="25" height="17"></td>
                <td><img src="images/bul.jpg" width="25" height="17"></td>
                <td><img src="images/eng.jpg" width="25" height="17"></td>
                <td><img src="images/ch.jpg" width="25" height="17"></td>
              </tr>
            </table></td>
            <td>&nbsp;</td>
          </tr>
        </table></td>
	</tr>
	<tr>
	  <td width="885" height="551" background="images/fond.jpg" >
        <table  width="98%" height="538" border="0" cellspacing="0" cellpadding="0">
          <tr>
            <td width="4" >&nbsp;</td>
            <td width="107" rowspan="3" background="images/cadre-general.jpg"><table id="Tableau_01" width="107" height="538" border="0" cellpadding="0" cellspacing="0">
	<tr>
		<td width="107" height="22" align="center" valign="middle"><span class="Titre-haut">General</span></td>
	</tr>
	<tr>
		<td width="107" height="20" class="languettes">&nbsp;</td>
	</tr>
	<tr>
		<td width="107" height="68" class="languettes" ><a href="/users.py" target="options" onMouseOver="MM_swapImage('Users','','images/bt-g-users_s.png',1);ChangeMessage('You will find here the Management of users and groups, you can add modify or delete each category, and manage rights','help_text')" onMouseOut="MM_swapImgRestore();ChangeMessage('','help_text')"><img src="images/bt-g-users.png" alt="Users" name="Users" width="107" height="68" border="0"></a></td>
	</tr>
	<tr>
		<td width="107" height="13" align="center" background="images/languette.png" class="languettes"><span class="languettes">Users</span></td>
	</tr>
	<tr>
		<td width="107" height="14" class="languettes">			</td>
	</tr>
	<tr>
		<td  width="107" height="68" class="languettes"><a href="/config.py" target="options" onMouseOver="MM_swapImage('Config','','images/bt-g-config_s.png',1);ChangeMessage('Configuration of the box','help_text')" onMouseOut="MM_swapImgRestore();ChangeMessage('','help_text')"><img src="images/bt-g-config.png" alt="Configuration" name="Config" width="107" height="68" border="0"></a></td>
	</tr>
	<tr>
		<td width="107" height="13" align="center" background="images/languette.png" class="languettes">Configuration</td>
	</tr>
	<tr>
		<td width="107" height="14" class="languettes">&nbsp;</td>
	</tr>
	<tr>
		<td width="107" height="68" class="languettes" ><a href="/menuappli.py" target="options" onMouseOver="MM_swapImage('Appli','','images/bt-g-application_s.png',1);ChangeMessage('You will find here Application management, to Install, Unninstall, Export and manage the virtual host','help_text')" onMouseOut="MM_swapImgRestore();ChangeMessage('','help_text')"><img src="images/bt-g-application.png" alt="Application" name="Appli" width="107" height="68" border="0"></a></td>
	</tr>
	<tr>
		<td width="107" height="13" align="center" background="images/languette.png" class="languettes">Application</td>
	</tr>
	<tr>
		<td width="107" height="23" class="languettes" >&nbsp;</td>
	</tr>
	<tr>
		<td width="107" height="68" class="languettes"><a href="/vfs.py" target="options" onMouseOver="MM_swapImage('Database','','images/shared-documents_s.png',1);ChangeMessage('You will find here the virtual file system management','help_text')" onMouseOut="MM_swapImgRestore();ChangeMessage('','help_text')"><img src="images/shared-documents.png" alt="VFS" name="Database" width="107" height="68" border="0"></a></td>
	</tr>
	<tr>
		<td width="107" height="13" align="center" background="images/languette.png" class="languettes">VFS</td>
	</tr>
	<tr>
		<td width="107" height="19" class="languettes">&nbsp;</td>
	</tr>
	<tr>
		<td width="107" height="67" class="languettes"><a href="/log.py" target="options" onMouseOver="MM_swapImage('Log','','images/bt-g-log_s.png',1);ChangeMessage('You will find here the server log, the users log and the debug mode','help_text')" onMouseOut="MM_swapImgRestore();ChangeMessage('','help_text')"><img src="images/bt-g-log.png" name="Log" width="107" height="67" border="0"></a></td>
	</tr>
	<tr>
		<td  width="107" height="13" align="center" background="images/languette.png" class="languettes">Log</td>
	</tr>
	<tr>
		<td width="107" height="19" class="languettes" ></td>
	</tr>
</table>
</td>
            <td width="753" colspan="3" rowspan="3" align="center" valign="top" ><table width="660" border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td height="10" colspan="5"></td>
              </tr>
              <tr>
                <td height="275" colspan="5" valign="top" background="images/cadre-options.png">
                <table width="100%" height="158" border="0" cellspacing="0" cellpadding="0">
                  <tr>
                    <td width="10" height="20" class="Titre-haut">&nbsp;</td>
                    <td width="650" class="Titre-haut">Options</td>
                  </tr>
                  <tr>
                    <td height="255" colspan="2" align="center" valign="top">
                    <IFRAME name="options" BORDER=0 ALLOWTRANSPARENCY="true" FRAMEBORDER=NO SCROLLING="auto" HEIGHT="253" WIDTH="652" SRC="/options.py"></IFRAME>
                    </td>
                  </tr>
                </table></td>
              </tr>
              <tr>
                <td height="20" colspan="5"></td>
              </tr>
              <tr>
                <td height="134" colspan="5" valign="top" background="images/cadre-info.png">
                <table width="100%" height="133" border="0" cellspacing="0" cellpadding="0">
                  <tr>
                    <td width="10" height="18" class="Titre-haut"></td>
                    <td width="650" valign="top" class="Titre-haut">Server Information</td>
                  </tr>
                  <tr>
                    <td height="114" colspan="2" align="center" valign="top">
                    <IFRAME name="server" BORDER=0 ALLOWTRANSPARENCY="true" FRAMEBORDER=NO SCROLLING=AUTO HEIGHT="112" WIDTH="652" SRC="/serverinfo.py"></IFRAME>
                    </td>
                  </tr>
                </table></td>
              </tr>
              <tr>
                <td height="26" colspan="5">&nbsp;</td>
              </tr>
              <tr>
                <td width="440" height="72" valign="top" background="images/cadre-aide.png">
                <table width="100%" height="72" border="0" cellspacing="0" cellpadding="0">
                  <tr>
                    <td width="10" height="2" class="Titre-haut"></td>
                    <td colspan="2" valign="top" class="Titre-haut">Help</td>
                  </tr>
                  <tr>
                    <td height="52" rowspan="3" align="left" valign="top"></td>
                    <td width="419" height="3" align="left" valign="middle"></td>
                    <td width="11" rowspan="3" align="left" valign="top">&nbsp;</td>
                  </tr>
                  <tr>
                    <td align="left" valign="middle"><div class="Texte" ID=help_text></div></td>
                  </tr>
                  <tr>
                    <td height="2" align="left" valign="middle"></td>
                  </tr>
                </table></td>
                <td width="26">&nbsp;</td>
                <td width="22">&nbsp;</td>
                <td width="153" height="72" valign="top" background="images/cadre-control.png">
                <table width="100%" height="72" border="0" cellspacing="0" cellpadding="0">
                  <tr>
                    <td width="5%" height="20" class="Titre-haut">&nbsp;</td>
                    <td width="95%" valign="top" class="Titre-haut">Server Control</td>
                  </tr>
                  <tr>
                    <td height="52" colspan="2" align="center" valign="middle"><table width="100%" border="0" cellspacing="0" cellpadding="0">
                      <tr>
                        <td width="50%" align="center" valign="middle"><a href="/reboot.py" target="server" onMouseOver="MM_swapImage('reboot','','images/bt-reeboot_s.gif',1);ChangeMessage('You can reboot the server here','help_text')" onMouseOut="MM_swapImgRestore();ChangeMessage('','help_text')"><img src="images/bt-reeboot.jpg" alt="Reboot" name="reboot" width="25" height="26" border="0"></a></td>
                        <td width="50%" align="center" valign="middle"><a href="/shutdown.py" target="server" onMouseOver="MM_swapImage('shutdown','','images/bt-shutdown_s.gif',1);ChangeMessage('You can shutdown the server here','help_text')" onMouseOut="MM_swapImgRestore();ChangeMessage('','help_text')"><img src="images/bt-shutdown.jpg" alt="Shutdown" name="shutdown" width="24" height="24" border="0"></a></td>
                      </tr>
                      <tr>
                        <td width="50%" align="center" valign="middle"><span class="control">Reboot</span></td>
                        <td width="50%" align="center" valign="middle" class="control">Shutdown</td>
                      </tr>
                    </table></td>
                  </tr>
                </table></td>
                <td width="19">&nbsp;</td>
              </tr>
              
            </table></td>
          </tr>
          <tr>
            <td>&nbsp;</td>
          </tr>
          <tr>
            <td>&nbsp;</td>
          </tr>
        </table>
      </td>
<td width="15" height="551" background="images/trait-drt.jpg">&nbsp;</td>
	</tr>
	<tr>
		<td width="900" height="59" colspan="2" align="right" valign="top" background="images/trait-bas.jpg"><span class="Copright"><br>
	      Copyright 2008 - all rights reserved - VDOM BOX International&nbsp;<br>
	    www.vdom-box-international.com&nbsp;</span></td>
	</tr>
</table>
</center>
</body>
</html>""")
	else:
		request.redirect("/system")
