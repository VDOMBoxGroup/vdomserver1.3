import os, traceback, json
import managers
from utils.system import get_external_drives
from utils.exception import VDOM_exception
from backup.storage_driver import VDOM_sd_external_drive

def run(request):
        sess = request.session()
        if not sess.value("appmngmtok"):
                request.write("Authentication failed")
                raise VDOM_exception("Authentication failed")
        
        args = request.arguments().arguments()
        sdrvs = managers.backup_manager.get_storages()
        revs = None
        request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Please, choose an application";</script>')
        if "devid" in args:
                appls = managers.backup_manager.get_app_list(args["devid"][0])
        request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Uninstall</title>
<style type="text/css">
body {
margin:0;
padding:0;
font-family:Arial;
background-color:#f8f8f8;
}

.Texte {
 font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
 font-size: 12px;
 color: #000000;
}

.wrapper {

width:100%;
height:100%;
margin:0px;
padding:0;
}

.block {
width:605px;
background-color:#fff;
border:1px solid #ccc;
margin:15px;
 box-shadow: 0 0 10px #c6c6c6;
    -moz-box-shadow: 0 0 10px #c6c6c6;
    -webkit-box-shadow: 0 0 10px #c6c6c6;
}

.block h2 {
color:#5e5e5e;
font-size:18px;
font-weight:normal;
margin-left:18px;
}

table.devices {
width:100%;
font-size:14px;
border-collapse:collapse;
}
table.devices td {
border-bottom:1px solid #d6d6d6;
line-height:28px;

}

table.devices td.name {
padding-left:24px;
}

table.devices td.ext-drive {
background: url(images/exthdd.png);
background-position:left 50%;
background-repeat:no-repeat;
}
table.devices td.cloud-drive {
background: url(images/cloud.png);
background-position:left 50%;
background-repeat:no-repeat;
}

table.devices td.check {
width:24px;
padding-left:15px;
}

table.devices td.options a {
font-size:10px;
color:#7f7f7f;
padding-right:10px;
text-decoration:none;
} 
table.devices td.options a:hover {
color:#000;
}
table.devices td.options {
text-align:right;
} 

.submit-gray {
background:#e9e9e9;
width:100%;
height:50px;
text-align:center;
}
.submit-gray input {
margin-top:15px;
}

.block select{
width:240px;
margin-left:15px;
}
.radiob {
margin-left:15px;
margin-top:15px;
}

.radiob p{
font-size:14px;

}

.radiob p span{
color:#4a4a4a;
font-size:10px;
}
</style>
</head>
<body>

<div id="Imgload" style="position:absolute; z-index:100; top:0px; left:0px; width:100%; height:100%; background-color:#FFFFFF; display:none" align="center"><br><br><img src="/images/loading.gif" border="0"></div>

<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; <a href="appbackup.py">Backup</a> &gt; Browse backup</p>
<form name="getBackup" method=post action="/restore.py" enctype="multipart/form-data">
<div class="wrapper"> 

  <div class="block">""")
        request.write("""
   <h2>Restore from <img src="images/exthdd.png" align="absmiddle"/>%(name)s</h2>
   <input type="hidden" name="devid" value="%(value)s">""" % {"name": str(args["devname"][0]), "value": str(args["devid"][0])})
        if appls:
                request.write("""
   <div class="radiob">""")        
                for app_id, app_name in appls.items():
                        request.write("""
    <p><label><input type="radio" name="appid" value="%(appid)s|%(name)s">%(name)s <span>GUID %(appid)s</span></label></p>""" % {"name": app_name, "appid": app_id, "drv": args["devid"][0]})
                request.write("""
   </div>
   <div class="submit-gray"><input type="submit" value="Select application"/></div>
  </div>
</div>
</form>
</body>
</html>""")
                