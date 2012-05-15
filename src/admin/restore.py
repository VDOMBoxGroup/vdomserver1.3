import os, traceback
import managers
from utils.exception import VDOM_exception
from datetime import datetime

def run(request):
        sess = request.session()
        if not sess.value("appmngmtok"):
                request.write("Authentication failed")
                raise VDOM_exception("Authentication failed")

        args = request.arguments().arguments()
        request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Please, choose a revision";</script>')
        if "devid" in args and "appid" in args:
                appid = args["appid"][0].split("|")[0]
                revs = managers.backup_manager.get_revision_list(args["devid"][0], appid)
                app_name = args["appid"][0].split("|")[1]
                driver_name = managers.backup_manager.get_storage(args["devid"][0]).name
        else:
                request.redirect("/getbackup.py?devid=%s&devname=%s" % (args["devid"][0], managers.backup_manager.get_storage(args["devid"][0]).name))
                return
        if "devid" in args and "appid" in args and "rev" in args:
                rev_info = managers.backup_manager.get_revision_info(args["devid"][0], appid, args["rev"][0])
                ret = managers.backup_manager.restore(args["devid"][0], appid, args["rev"][0])
                vh = request.server().virtual_hosting()
                if rev_info["virtual_hosts"]:
                        sites = rev_info["virtual_hosts"].split(', ')
                        if sites:
                                for site in sites:
                                        vh.set_site(site, appid)
                if ret[1] != "":
                        request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Application has been restored with warnings\n%s";</script>' % ret[1])
                else:
                        request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Application has been restored";</script>')
                
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

<script language="javascript">
function LoadImgWait(){
        document.restore.style.display='none';
	document.getElementById('Imgload').style.display='';
	parent.server.document.getElementById("MsgSvrInfo").innerHTML="Restoring...";
}
</script>
</head>

<body>


<div id="Imgload" style="position:absolute; z-index:100; top:0px; left:0px; width:100%; height:100%; background-color:#FFFFFF; display:none" align="center"><br><br><img src="/images/loading.gif" border="0"></div>""")
        request.write('<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; <a href="appbackup.py">Backup</a> &gt; <a href="getbackup.py?devid=%s&devname=%s">Browse backup</a> &gt; %s</p>' % (args["devid"][0], driver_name, app_name))
        request.write("""
<form name="restore" method=post action="/restore.py" enctype="multipart/form-data">
<input type="hidden" name="devid" value="%(devid)s">
<input type="hidden" name="appid" value="%(appid)s">""" % {"devid": args["devid"][0], "appid": args["appid"][0]})
        request.write("""
<div class="wrapper"> 

 <div class="block">
  <h2>Restore %(appname)s from <img src="images/exthdd.png" align="absmiddle"/>%(drv_name)s</h2>
  <div class="radiob">""" % {"appname": app_name, "drv_name": driver_name})
        for rev in revs:
                dt = datetime.strptime(rev["time"], "%Y-%m-%dT%H:%M:%S.%f")
                time = dt.strftime("%d-%m-%Y at %H:%M")
                request.write("""
   <p><label><input type="radio" name="rev" value="%(rev)s">Revision %(rev)s <span>%(time)s</span></label></p>""" % {"rev": rev["revision"], "time": time})
        request.write("""
  </div>
  <div class="submit-gray"><input type="button" value="Back" onclick="history.back();"/> &nbsp &nbsp <input type="submit" onclick="LoadImgWait();" value="Restore application"/></div>

 </div>

</div>
</form>
</body>
</html>""")