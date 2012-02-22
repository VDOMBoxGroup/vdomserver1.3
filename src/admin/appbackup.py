
import os, traceback
import managers
from utils.system import get_external_drives
from utils.exception import VDOM_exception
from backup.storage_driver import VDOM_sd_external_drive, VDOM_cloud_storage_driver #, VDOM_smb_storage_driver

def run(request):
        sess = request.session()
        if not sess.value("appmngmtok"):
                request.write("Authentication failed")
                raise VDOM_exception("Authentication failed")

        args = request.arguments().arguments()
	request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="";</script>')
        applst = managers.xml_manager.get_applications()
        sm = managers.server_manager
        drivers = managers.backup_manager.get_storages()
	from utils.card_connect import send_to_card_and_wait
	login = send_to_card_and_wait("getlicense %s %s" % ("0", "106"),"%s/%s" % ("0", "106"))
	add_cloud = True if login else False
	if "forget" in args and "devid" in args:
		driver = drivers[args["devid"][0]]
		managers.backup_manager.del_storage(driver)
        if "device" in args and "abs" in args:
		request.redirect("/sdconfig.py?type=%s" % args["device"][0])
		return
        if "devid" in args:
                drv = managers.backup_manager.get_storage(args["devid"][0])
                if drv.type == "external_drive":
                        request.redirect("/sdconfig.py?devid=%s&type=%s" % (drv.id, "external"))
			return
		elif drv.type == "cloud_drive":
			request.redirect("/sdconfig.py?devid=%s&type=%s" % (drv.id, "cloud"))
			return
	if "save" in args:
		if "drv[]" in args:
			crontab = []
			for drv in drivers:
				task_id, schedule = managers.backup_manager.get_schedule(drv)
				if drv in args["drv[]"]:
					schedule[0].in_cron = True
					managers.scheduler_manager.update(task_id, schedule[0], schedule[1])
					crontab.append((task_id, schedule[1]))
				else: 
					schedule[0].in_cron = False
					managers.scheduler_manager.update(task_id, schedule[0], schedule[1])
			managers.scheduler_manager.build_crontab(crontab)
		elif "drv[]" not in args:
			schedule_list = managers.backup_manager.get_schedule_list()
			for tid in schedule_list:
				schedule_list[tid][0].in_cron = False
				managers.scheduler_manager.update(tid, schedule_list[tid][0], schedule_list[tid][1])
			managers.scheduler_manager.clean_crontab()
		request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Crontab built successfully";</script>')
        request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Uninstall</title>
<style>
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
function LoadImgWait(message){
        var msg = message || "";
	document.getElementById('Imgload').style.display='';
	parent.server.document.getElementById("MsgSvrInfo").innerHTML=msg;
}
</script>
</head>

<body>


<div id="Imgload" style="position:absolute; z-index:100; top:0px; left:0px; width:100%; height:100%; background-color:#FFFFFF; display:none" align="center"><br><br><img src="/images/loading.gif" border="0"></div>

<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; Backup</p>
<form method=post action="/appbackup.py" enctype="multipart/form-data">
<div class="wrapper"> 
  <div class="block">
   <h2>Enabled backup storage</h2>
   <table class="devices">""")
	tasks_in_cron = managers.scheduler_manager.get_crontab()
        for driver in drivers:
		if drivers[driver].type == "cloud_drive":
			add_cloud = False
		try:
			task_id, schedule = managers.backup_manager.get_schedule(driver)
		except:
			task_id, schedule = None, None
		driver_icon = "ext-drive" if drivers[driver].type == "external_drive" else "cloud-drive"
		checked = 'checked = "checked"' if task_id in dict(tasks_in_cron) else ''
                request.write("""
     <tr><td class="check"><input type="checkbox" name="drv[]" value="%(drv)s" %(checked)s></td><td class="name %(icon)s">%(name)s</td><td class="options"><a href="/appbackup.py?devid=%(drv)s">Config</a><a href="/getbackup.py?devid=%(drv)s&devname=%(name)s">Browse backups</a><a href="/appbackup.py?forget&devid=%(drv)s" onclick="LoadImgWait();">Forget</a></td></tr>""" % {"icon": driver_icon, "drv": driver, "checked": checked, "name": drivers[driver].name})
	request.write("""
   </table>
   <div class="submit-gray"><input type="submit" name="save" value="Save changes" onclick="LoadImgWait('Saving backup configuration...');"/></div>
  </div>
  <div class="block" style="padding-bottom:15px;">
   <h2>Add new backup storage</h2>
   <select name="device">
    <option value="external">External device</option>""")
	if add_cloud:
		request.write("""
    <option value="cloud">Cloud storage</option>""")
	request.write("""
    <option value="smb">SMB storage</option>
   </select>
   <input type="submit" name="abs" value="Add storage"/>
  </div>
</div>
</form>
</body>
</html>""")