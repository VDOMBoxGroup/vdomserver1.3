import os, traceback, json, re
import managers
from datetime import time
from random import randint
from utils.system import get_external_drives
from utils.exception import VDOM_exception
from backup.storage_driver import VDOM_sd_external_drive, VDOM_cloud_storage_driver, VDOM_smb_storage_driver, VDOM_sshfs_drive

def run(request):
	sess = request.session()
	if not sess.value("appmngmtok"):
		request.write("Authentication failed")
		raise VDOM_exception("Authentication failed")

	args = request.arguments().arguments()
	if "cancel" in args:
		request.redirect("/appbackup.py")
		return
	applst = managers.xml_manager.get_applications()
	dev_list = VDOM_sd_external_drive.get_device_list()
	dev_option_tag = apps_tag = ""
	drv_icon = "images/exthdd.png"
	driver = None
	default_drv_name = ""
	hidden_tag = ""
	apps_tag = ""
	for app in applst:
		appname = managers.xml_manager.get_application(app).name
		apps_tag += """
          <p><input type="checkbox" name="backup_app[]" value="%(appid)s" checked>%(appname)s <span>GUID %(appid)s</span></input></p>""" % \
		                                                                                                                         {"appid": app, "appname": appname}

	hourly_selected = ""
	week_display = ''
	rotation_value = "10"
	daily_selected = " selected"
	week_days = "*"
	daily_display = ''
	hourly_display = ' style="display:none;"'
	t = time(randint(0, 5), randint(0, 59))
	d_backup_time = t.strftime("%H:%M")
	h_backup_time = '1'
	crypt_box = ""
	server = user = passwd = location = port = remote_path = ""
	if "erase" in args and args["erase"][0] != "":
		driver = managers.backup_manager.get_storage(args["erase"][0])
		driver.erase_storage()
		#managers.backup_manager.del_storage(driver)
		#driver = None
	if "devid" in args:
		driver = managers.backup_manager.get_storage(args["devid"][0])

		hidden_tag = """
<input type="hidden" name="devid" value="%s">""" % driver.id
	if "type" in args:
		hidden_tag += """
<input type="hidden" name="type" value="%s">""" % args["type"][0]
		if args["type"][0] == "external_drive":
			default_drv_name = "External Drive"
			drv_icon = "images/exthdd.png"
		elif args["type"][0] == "cloud_drive":
			default_drv_name = "Cloud Storage"
			drv_icon = "images/cloud.png"
		elif args["type"][0] == "smb_drive":
			default_drv_name = "Windows Share"
		elif args["type"][0] == "sshfs_drive":
			default_drv_name = "SSHFS Drive"
	if "save" in args:
		ok = True
		if not driver:
			crypt = False
			if "type" in args:
				try:
					if args["type"][0] == "external_drive":
						driver = VDOM_sd_external_drive(args["devselect"][0], crypt)
					elif args["type"][0] == "cloud_drive":
						driver = VDOM_cloud_storage_driver(crypt)
					elif args["type"][0] == "smb_drive":
						driver = VDOM_smb_storage_driver()
					elif args["type"][0] == "sshfs_drive":
						driver = VDOM_sshfs_drive(crypt)
					

				except Exception as e:
					request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="%s";</script>' % unicode(e))
					ok = False
				if ok:
					hidden_tag += """
<input type="hidden" name="devid" value="%s">""" % driver.id
		if hasattr(driver, "authentificate"):
			try:
				server = args["server_adr"][0]
				user = args["username"][0]
				passwd = args["passwd"][0]
				if driver.type == "smb_drive":
					location = args["location"][0]
					if not driver.authentificate(user, passwd, server, location):
						raise Exception("Incorrect login or password for host %s" % server)
				elif driver.type == "sshfs_drive":
					if "port" in args and "remote_path" in args:
						port = args["port"][0]
						remote_path = args["remote_path"][0]
						if not driver.authentificate(user, passwd, server, port, remote_path):
							raise Exception("Incorrect login or password for host %s" % server)
			except Exception as e:
				request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="%s";</script>' % unicode(e))
				ok = False
		if "backup_app[]" in args:
			backup_apps = args["backup_app[]"]
		else:
			backup_apps = []
		if "rotation" in args:
			rotation_value = args["rotation"][0]
		else:
			rotation_value = "10"
		if "week-day[]" in args and "daily_int" in args and args["int1"][0] == "daily" and re.match("^([01]?[0-9]|2[0-3]):[0-5][0-9]$", args["daily_int"][0]):
			days_of_week = "*" if len(args["week-day[]"]) == 7 else ",".join(args["week-day[]"])
			minutes = args["daily_int"][0].split(':')[1]
			hours = args["daily_int"][0].split(':')[0]
			interval = (minutes, hours, "*", "*", days_of_week)
		elif args["int1"][0] == "hourly" and "hourly_int" in args and re.match("^([1-9]|1[0-9]|2[0-4])$", args["hourly_int"][0]):
			hours = "*/" + args["hourly_int"][0]
			interval = ("0", hours, "*", "*", "*")
		elif args["int1"][0] == "daily" and "week-day[]" not in args:
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Error: you must choose one or more days!";</script>')
			ok = False
		else:
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Error: Incorrect time format!";</script>')
			ok = False
		if ok:
			if hasattr(driver, "change_device") and driver.change_device(args["devselect"][0]):
				managers.backup_manager.add_storage(driver)
			if not managers.backup_manager.update_schedule(driver.id, backup_apps, interval, rotation_value):
				managers.backup_manager.add_storage(driver)
				managers.backup_manager.add_schedule(driver.id, backup_apps, interval, rotation_value)
			drivers = managers.backup_manager.get_storages()
			crontab = []
			for drv in drivers:
				task_id, schedule = managers.backup_manager.get_schedule(drv)
				if schedule[0].in_cron:
					crontab.append((task_id, schedule[1]))

			managers.scheduler_manager.build_crontab(crontab)
			request.redirect("/appbackup.py")
			return

	for dev in dev_list:
		dev_option_tag += "<option value='%(dev)s'%(selected)s>%(devname)s</option>" % {"dev": dev[0], "devname": dev[1], "selected": " selected" if driver and hasattr(driver, 'dev') and dev[0] == driver.dev else ""}		
	if "devid" in args or "save" in args:
		schedule = managers.backup_manager.get_schedule(driver.id)
		if schedule:			
			backup_apps = schedule[1][0].applications
			rotation_value = schedule[1][0].rotation
			apps_tag = ""
			for app in applst:
				appname = managers.xml_manager.get_application(app).name
				apps_tag += """
          <p><input type="checkbox" name="backup_app[]" value="%(appid)s"%(checked)s>%(appname)s <span>GUID %(appid)s</span></input></p>""" % \
				                                                                                                            {"appid": app, "appname": appname, "checked": " checked" if app in backup_apps else ""}
			schedule1 = schedule[1][1]
			if "*" in schedule1[1]:
				hourly_selected = " selected"
				week_display = ' style="display:none;"'
				daily_selected = ""
				week_days = "*"
				daily_display = ' style="display:none;"'
				hourly_display = ''
				h_backup_time = "1" if schedule1[1] == "*" else schedule1[1].split('/')[1]
				d_backup_time = '00:00'
			else:
				daily_selected = " selected"
				week_display = ""
				hourly_selected = ""
				week_days = schedule1[4]
				daily_display = ''
				hourly_display = ' style="display:none;"'
				d_backup_time = schedule1[1] + ":" + schedule1[0]
				h_backup_time = '1'

	if driver:
		if driver.type == "smb_drive":
			server = driver.host or ""
			user = driver.login or ""
			passwd = driver.password or ""
			location = driver.location or ""
		elif driver.type == "sshfs_drive":
			server = driver.host or ""
			user = driver.login or ""
			passwd = driver.password or ""
			port = driver.port or ""
			remote_path = driver.remote_path or ""

		#crypt_box = " disabled checked" if hasattr(driver, 'crypt') and driver.crypt else " disabled"
		try:
			path = driver.mount()
			if path:
				(size, used, free, percent) = driver.get_sd_size(path)
				driver.umount()
			else:
				raise Exception("Storage driver hasn't been mounted")
		except Exception as e:
			(size, used, free, percent) = ("0", "0", "0", "0%")
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="%s";</script>' % unicode(e))
	else:
		(size, used, free, percent) = ("0", "0", "0", "0%")
	if "backupNow" in args:
		if "devid" in args:
			try:
				if hasattr(driver, "authentificate"):
					if driver.type == "smb_drive":
						try:
							if not driver.authentificate(args["username"][0], args["passwd"][0], args["server_adr"][0], args["location"][0]):
								raise Exception("Incorrect login or password")
						except:
							raise Exception("Incorrect login or password")
					elif driver.type == "sshfs_drive":
						if "port" in args and "remote_path" in args:
							try:
								if not driver.authentificate(args["username"][0], args["passwd"][0], args["server_adr"][0], args["port"][0], args["remote_path"][0]):
									raise Exception("Incorrect login or password")
							except:
								raise Exception("Incorrect login or password")
				if "backup_app[]" in args:
					for appid in args["backup_app[]"]:
						managers.backup_manager.backup(appid, args["devid"][0], args["rotation"][0])
				else:
					request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="There are no applications to backup";</script>')
			except Exception as e:
				request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="%s";</script>' % unicode(e))

		else:
			request.write('<script language="javascript">parent.server.document.getElementById("MsgSvrInfo").innerHTML="Storage driver not found";</script>')
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
.radiob, .checkbox {
margin-left:15px;
margin-top:15px;
}

.radiob p{
font-size:14px;

}
.checkbox p{
font-size:12px;
font-weight:bold;
line-height:16px;
}
.radiob p span,.checkbox p span{
color:#4a4a4a;
font-size:10px;
font-weight:normal;
}
.fields {
width:240px;

}

.fields div{
clear:both;
margin-left:20px;
margin-top:15px;
}

.fields select, .fields input{
float:right;
display:block;
position:relative;
margin-bottom:10px;
width:150px;
}

.fields label {
float:left;
line-height:24px;
font-size:12px;
display:block;
position:relative;
}
#x_hourly input{
float: left;
width: 30px;
margin: 0 10;
}
.clear {
clear:both;
width:100%;
display:block;
}
.week {
clear:none !important;
position:absolute;
top:104px;
left:270px;
}
.week .week-day {
float:left;
padding:3px;
font-size:10px;
text-align:center;
}
.week label,.week input[type=checkbox] {
display:block;
margin:0;
padding:0;
}
.hdd-state {
width:150px;
border:1px solid #dcdcdc;
background: url(images/gr-bg.png);
background-position:bottom left;
background-repeat:repeat-x;
padding:8px;
margin:10px;
}
.hdd-state h2 {
color:#000;
margin:0;
padding:0;
font-size:14px;
}

.progress {
width:120px;
height:14px;
display:none;
border:1px solid #989898;
 border-radius: 10px;
    -moz-border-radius: 10px;
    -webkit-border-radius: 10px;
	padding:1px;
	margin-top:15px;
}
.progress .bar {
width:120px;
height:14px;
background:#000;
 border-radius: 10px;
    -moz-border-radius: 10px;
    -webkit-border-radius: 10px;
}""")
	request.write("""
.progress .bar-holder {
overflow:hidden;
width:%s;

}""" % percent)
	request.write("""
.free-mem {
font-size:12px;
margin-top:15px;
display:none;
}

.hdd-state .erase {
margin-top:15px;
}

.hdd-state .erase a{
font-size:14px;
color:#fe0000;
}

.hdd-state .crypt {
margin-top:15px;
font-size:12px;
display:none;
}

.fl-left {
float:left;
}

.fl-right {
float:right;
}
</style>

<script language="javascript">
function LoadImgWait(message){
        var msg = message || "";
        document.configBackup.style.display='none';
	document.getElementById('Imgload').style.display='';
	parent.server.document.getElementById("MsgSvrInfo").innerHTML=msg;
}
function ChangeBackup(obj){
	if (obj.value == "hourly"){
	  document.getElementsByClassName('week')[0].style.display='none';
	  document.getElementById('x_daily').style.display='none';
	  document.getElementById('x_hourly').style.display='';
	}else if (obj.value == "daily"){
	  document.getElementsByClassName('week')[0].style.display='';
	  document.getElementById('x_daily').style.display='';
	  document.getElementById('x_hourly').style.display='none';
	}
}

</script>
</head>

<body>


<div id="Imgload" style="position:absolute; z-index:100; top:0px; left:0px; width:100%; height:100%; background-color:#FFFFFF; display:none" align="center"><br><br><img src="/images/loading.gif" border="0"></div>

<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; <a href="appbackup.py">Backup</a> &gt; Config</p>""")
	request.write("""
<form name="configBackup" method=post onsubmit="LoadImgWait();" enctype="multipart/form-data">%s
<div class="wrapper"> 
 <div class="block">
  <h2><img src="%s" align="absmiddle"/> Config %s</h2>
  <div class="fields fl-left">""" % (hidden_tag, drv_icon, driver.name if driver else default_drv_name))
	if "type" in args and args["type"][0] == "external_drive":
		request.write("""
   <div><label for="devselect">Device :</label><select name="devselect">%s</select></div>""" % dev_option_tag)
	request.write("""
   <div><label for="int1">Backup :</label><select name="int1" onchange="ChangeBackup(this);"><option value="daily"%s>Daily</option><option value="hourly"%s>Hourly</option></select></div>""" % (daily_selected, hourly_selected))
	request.write("""
   <div id="x_daily"%(display)s><label for="daily_int">Backup at : </label><input type="text" name="daily_int" value="%(value)s"></div>""" % {"display": daily_display, "value": d_backup_time})
	request.write("""
   <div id="x_hourly"%(display)s><label for="hourly_int">Backup every </label><input type="text" name="hourly_int" value="%(value)s"><label for="hourly_int"> hour(s)</label></div>""" % {"display": hourly_display, "value": h_backup_time})
	request.write("""
   <div id="rotation"><label for="rotation">Rotation </label><input type="text" name="rotation" value="%(value)s"></div>""" % {"value": rotation_value})
	if "type" in args and args["type"][0] == "smb_drive":

		request.write("""
   <div id="server_adr"><label for="server_adr">Server: </label><input type="text" name="server_adr" value="%(serv_adr)s"></div>
   <div id="location"><label for="location">Location: </label><input type="text" name="location" value="%(location)s"></div>
   <div id="username"><label for="username">Username: </label><input type="text" name="username" value="%(usrname)s"></div>
   <div id="passwd"><label for="passwd">Password: </label><input type="password" name="passwd" value="%(passwd)s"></div>""" % {"serv_adr": server, "location": location, "usrname": user, "passwd": passwd})
	if "type" in args and args["type"][0] == "sshfs_drive":
		request.write("""
   <div id="server_adr"><label for="server_adr">Server: </label><input type="text" name="server_adr" value="%(serv_adr)s"></div>
   <div id="port"><label for="port">Port: </label><input type="text" name="port" value="%(port)s"></div>
   <div id="remote_path"><label for="remote_path">Remote: </label><input type="text" name="remote_path" value="%(remote_path)s"></div>
   <div id="username"><label for="username">Username: </label><input type="text" name="username" value="%(usrname)s"></div>
   <div id="passwd"><label for="passwd">Password: </label><input type="password" name="passwd" value="%(passwd)s"></div>""" % {"serv_adr": server, "port": port, "remote_path": remote_path, "usrname": user, "passwd": passwd})
	request.write("""
   <div class="clear"> </div>
  </div>""")
	
	request.write("""
  <div class="week"%(display)s>
	<div class="week-day"><label for="mon">M</label><input id="mon" name="week-day[]" value="1" type="checkbox"%(mon)s/></div>
	<div class="week-day"><label for="tue">T</label><input id="tue" name="week-day[]" value="2" type="checkbox"%(tue)s/></div>
	<div class="week-day"><label for="wed">W</label><input id="wed" name="week-day[]" value="3" type="checkbox"%(wed)s/></div>
	<div class="week-day"><label for="thu">T</label><input id="thu" name="week-day[]" value="4" type="checkbox"%(thu)s/></div>

	<div class="week-day"><label for="fri">F</label><input id="fri" name="week-day[]" value="5" type="checkbox"%(fri)s/></div>
	<div class="week-day"><label for="sat">S</label><input id="sat" name="week-day[]" value="6" type="checkbox"%(sat)s/></div>
	<div class="week-day"><label for="sun">S</label><input id="sun" name="week-day[]" value="7" type="checkbox"%(sun)s/></div>
	<div class="clear"> </div>
  </div>""" % {"display": week_display,
	       "mon": " checked" if "1" in week_days or week_days == '*' else "",
	       "tue": " checked" if "2" in week_days or week_days == '*' else "",
	       "wed": " checked" if "3" in week_days or week_days == '*' else "",
	       "thu": " checked" if "4" in week_days or week_days == '*' else "",
	       "fri": " checked" if "5" in week_days or week_days == '*' else "",
	       "sat": " checked" if "6" in week_days or week_days == '*' else "",
	       "sun": " checked" if "7" in week_days or week_days == '*' else ""})
	request.write("""
  <div class="hdd-state fl-right" align="center">
	<div class="head"><h2><img src="%(icon)s" align="absmiddle"/> %(driver)s</h2></div>

	<div class="progress" align="left">
		<div class="bar-holder">
		  <div class="bar"></div>
		</div>
	</div>

	<div class="free-mem">%(free)s of %(size)s is free</div>

	<div class="crypt"><label><input type="checkbox" name="crypt-dev"%(crypt)s>Crypt disk</label></div>

	<div class="erase"><a href="sdconfig.py?erase=%(dev)s" onclick="if (confirm('Do you really want erase all data from storage?')){LoadImgWait(); return true;}else{return false;};">Erase this storage</a></div>

  </div>
  <div class="clear"> </div>
 </div>""" % {"icon": drv_icon, "driver": driver.name if driver else default_drv_name, "free": humanize_bytes(int("100")), "size": humanize_bytes(int(size)), "dev": driver.id if driver else "", "crypt": crypt_box})
	request.write("""
 <div class="block">
	<h2>Backup following applications :</h2>
	<div class="checkbox">%s
        </div>
 </div>""" % apps_tag)
	request.write("""
<center><input type="submit" name="cancel" value="Back"/> &nbsp &nbsp <input type="submit" name="save" value="Save changes" onclick="LoadImgWait('Saving...');"/> &nbsp &nbsp <input type="submit" name="backupNow" value="Backup Now" onclick="LoadImgWait('Backing up...');"/></center>
</div>
</form>
</body>
</html>""")

def humanize_bytes(bytes, precision=1):
	abbrevs = (
	        (1<<40L, 'PB'),
	        (1<<30L, 'TB'),
	        (1<<20L, 'GB'),
	        (1<<10L, 'MB'),
	        (1, 'kB')
	)
	if bytes == 1:
		return '1 kB'
	for factor, suffix in abbrevs:
		if bytes >= factor:
			break
	return '%.*f %s' % (precision, bytes / factor, suffix)