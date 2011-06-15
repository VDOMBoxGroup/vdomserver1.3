
from utils.exception import VDOM_exception
import managers
from utils.system import get_ip_and_mask, get_date_and_time, get_free_space, get_hd_size, get_default_gateway
from version import VDOM_server_version

def run(request):

	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")
	else:
		(_ip, _msk) = get_ip_and_mask()
		param = {}
		param["ip"] = _ip
		param["mask"] = _msk
		param["gate"] = get_default_gateway()
		param["date"] = None
		param["time"] = None
		param["firmware"] = system_options["firmware"]
		param["objlim"] = system_options["object_amount"]
		param["obj"] = managers.xml_manager.obj_count
		param["_o"] = int(100.0 * managers.xml_manager.obj_count / int(system_options["object_amount"])) if int(system_options["object_amount"]) != 0 else 100
		param["ver"] = VDOM_server_version
		if "0" == system_options["server_license_type"]:
			param["usage"] = "Online server"
		else:
			param["usage"] = "Development server"
		param["hd"] = get_free_space()
		param["hdsize"] = 1 + int(get_hd_size())
		param["_h"] = 100 - int(100.0 * param["hd"] / param["hdsize"])
		the_date = get_date_and_time()
		if None != the_date:
			param["date"] = the_date.split(" ")[0]
			param["time"] = the_date.split(" ")[-1]
		param["boximg"] = "box-v-v.jpg"
		if "0" == system_options["card_state"]:
			param["boximg"] = "box-v-r.jpg"
		request.write("""
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Options</title>
<style type="text/css">
<!--
body {
	margin-top: 2px;
	margin-right: 0px;
	margin-bottom: 0px;
}
.Texte {
	font-family: Verdana, Arial, Helvetica, sans-serif;
	font-size: 12px;
}
-->
</style>
</head>
<body>
<center>
<table width="630" style="border-collapse:collapse;" cellpadding="0" cellspacing="0" border="0">
    <tr>
        <td width="385" align="left" height="83"><img src="images/%(boximg)s" border="0"></td>
        <td width="17" height="83">&nbsp;</td>
        <td width="226" height="83">
            <table cellspacing="0" style="border-collapse:collapse;" cellpadding="0" height="83">
                <tr>
                    <td width="207" background="images/cadre-network.jpg" height="22" style="border-width:0; border-color:black; border-style:solid;"></td>
                </tr>
                <tr>
                    <td width="207" background="images/cadre-bas.jpg" height="60" valign="top">
                        <table border="0" width="204" height="60">
                            <tr>
                                <td width="75" class="Texte" align="right">IP :</td>
                                <td class="Texte">%(ip)s</td>
                            </tr>
                            <tr>
                                <td width="75" class="Texte" align="right">Mask :</td>
                                <td class="Texte">%(mask)s</td>
                            </tr>
                            <tr>
                                <td width="75" class="Texte" align="right">Gateway :</td>
                                <td class="Texte">%(gate)s</td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td width="385" align="left" height="83">
            <table border="0" width="409">
                <tr>
                    <td width="53"><img src="images/logo-dd.jpg" border="0"></td>
                    <td width="340" align="left" valign="middle">
                        <table border="0" width="321" cellpadding="0" cellspacing="0">
<tr>
                                <td class="Texte" align="right" valign="bottom" width="38">0</td>
                  <td width="226">&nbsp;</td>
                  <td class="Texte" valign="bottom" align="left" width="57">%(hdsize)d</td>
                          </tr>
                                <tr>
                                <td height="15" width="38"></td>
                              <td width="226" height="15">
<table border="1" cellspacing="0" width="225" height="15"  cellpadding="0" bordercolor="red" bordercolordark="red" bordercolorlight="red">
                                            <tr>
						<td bordercolor="red" height="12">
             <div style="width:%(_h)d%%; height:12px; background-image:url(images/barre-chargement.jpg); font-size:1"></div>
						</td>
                                            </tr>
                                        </table>
                                    </td>
                                <td height="15" width="57"></td>
                          </tr>
                            <tr>
                                <td width="38">&nbsp;</td>
                              <td width="226">&nbsp;</td>
                              <td width="57">&nbsp;</td>
                          </tr>
                        </table>
                  </td>
                </tr>
            </table>
        </td>
        <td width="17" height="83">&nbsp;</td>
        <td width="226" height="83">            
			<table cellspacing="0" style="border-collapse:collapse;" cellpadding="0" height="83">
                <tr>
                    <td width="207" background="images/cadre-general-1.jpg" height="22" style="border-width:0; border-color:black; border-style:solid;"></td>
                </tr>
                <tr>
                    <td width="207" background="images/cadre-bas.jpg" height="60" valign="top">
                        <table border="0" width="204">
                            <tr>
                                <td width="75" class="Texte" align="right">Ver :</td>
                                <td class="Texte">%(ver)s</td>
                            </tr>
                            <tr>
                                <td width="75" class="Texte" align="right">Usage :</td>
                                <td class="Texte">%(usage)s</td>
                            </tr>
                            <tr>
                                <td width="75" class="Texte" align="right" height="14">Firmware :</td>
                                <td class="Texte" height="14">%(firmware)s</td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
		</td>
    </tr>
    <tr>
        <td width="385" align="left">
            <table border="0" width="395">
                <tr>
                    <td width="72"><img src="images/logos-objets.jpg" border="0"></td>
                    <td width="313" align="left" valign="middle">
                                <table border="0" width="282" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td width="19"><div align="right"><span class="Texte">0</span></div></td>
                                      <td width="225">&nbsp;</td>
                                        <td width="38"><div align="left"><span class="Texte">%(objlim)s</span></div></td>
                                  </tr>
                                    <tr>
                                        <td height="12" width="19"></td>
                                        <td width="225"  height="12">
						<table border="1" cellspacing="0" width="225" height="15" cellpadding="0" bordercolor="red" bordercolordark="red" bordercolorlight="red">
                                            <tr>
						<td bordercolor="red" height="12">
             <div style="width:%(_o)d%%; height:12px; background-image:url(images/cellule.jpg); font-size:1"></div>
						</td>
                                            </tr>
                                        	</table>
					</td>
                                        <td height="12" width="38"></td>
                                    </tr>
                                    <tr>
                                        <td width="19">&nbsp;</td>
                                        <td width="225">&nbsp;</td>
                                        <td width="38">&nbsp;</td>
                                    </tr>
                                </table>
                    </td>
                </tr>
            </table>
        </td>
        <td width="17">&nbsp;</td>
        <td width="226">            
			<table cellspacing="0" style="border-collapse:collapse;" cellpadding="0">
                <tr>
                    <td width="207" background="images/cadre-datetime.jpg" height="22" style="border-width:0; border-color:black; border-style:solid;"></td>
                </tr>
                <tr>
                    <td width="207" background="images/cadre-time.jpg" height="57" valign="top">
                        <table border="0" width="204">
                            <tr>
                                <td width="75" class="Texte" align="right" height="19">Date :</td>
                                <td class="Texte" height="19">%(date)s</td>
                            </tr>
                            <tr>
                                <td width="75" class="Texte" align="right" height="21">Time :</td>
                                <td class="Texte" height="21">%(time)s</td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
		</td>
    </tr>
</table>
</center>
</body>
</html>
""" % param)
