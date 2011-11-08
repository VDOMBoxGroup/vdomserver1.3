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
        applst = managers.xml_manager.get_applications()
        dev_list = VDOM_sd_external_drive.get_device_list()
        if "devid" in args and args["devid"][0] != "":
                sd = managers.backup_manager.get_storage(args["devid"][0])
                schedule = managers.backup_manager.get_schedule(args["devid"][0])[1]
                inter = schedule[1] if schedule else ("00", "00", "30", "*", "*")
            	applist = schedule[0].applications if schedule else applst
	if "devselect" in args or "driver" in args:
		if "devselect" in args and args["devselect"][0] != "":
			if "addsd" in args: 
				driver = VDOM_sd_external_drive(args["devselect"][0])
		if "driver" in args:
			if "update" in args:
				driver = managers.backup_manager.get_storage(args["driver"][0])
			elif "delete" in args:
				driver = managers.backup_manager.get_storage(args["driver"][0])
				managers.backup_manager.del_storage(driver)
				request.redirect("/appbackup.py")
				return
                path = driver.mount()
                if not path:
                        request.write("Mount failed")
                        raise VDOM_exception("Mount failed")
                else:
			if "hour" in args and "minutes" in args and "days" in args and "appl[]" in args:
                    		managers.backup_manager.add_storage(driver)
                    		interval = ('%s' % args["minutes"][0],
				            '%s' % args["hour"][0],
				            '*/%s' % args["days"][0], '*', '*')
                                if "addsd" in args:
                                        managers.backup_manager.add_schedule(driver.id, args["appl[]"], interval, rotation="0")
                                elif "update" in args:
                                        managers.backup_manager.update_schedule(driver.id, args["appl[]"], interval, rotation="0")
                                driver.umount()
                        request.redirect("/appbackup.py")
			return
        request.write("""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Uninstall</title>
<style type="text/css">

.Texte {
	font-family: Tahoma, Verdana, Arial, Helvetica, sans-serif;
	font-size: 12px;
	color: #000000;
}
select.dev{
        width: 123px;
}
</style>

<script language="javascript">
function LoadImgWait(){
	document.getElementById('Imgload').style.display='';
	parent.server.document.getElementById("MsgSvrInfo").innerHTML="Saving backup configuration...";
}
</script>
</head>

<body>


<div id="Imgload" style="position:absolute; z-index:100; top:0px; left:0px; width:100%; height:100%; background-color:#FFFFFF; display:none" align="center"><br><br><img src="/images/loading.gif" border="0"></div>

<p class="Texte"><a href="menuappli.py">Application Management</a> &gt; Backup</p>
<table width="100%" height="85%" border="0">
   <tr>
     <td>
""")
        request.write("""
	<form name="configBackup" method=post onsubmit="LoadImgWait();" action="/sdconfig.py" enctype="multipart/form-data">""")
	if "devid" in args:
		request.write("""
	<input type="hidden" name="driver" value="%s">""" % sd.id)
	request.write("""
	<table>
	  <tr>
	    <td>
	     <p><span>Select device: </span>
	      <select class="dev" name="devselect">""")
        for devs in dev_list:
                request.write("""
		  <option value="%(dev)s">%(dev)s</option>""" % {"dev": devs})
        request.write("""
	      </select>
	     </p> 
	    </td>
	  </tr>
	  <tr>
	    <td>
	      <p><span>Backup at: </span>
	        <input type="text" size="2" name="hour" onchange="hour_test(this);"><span> : </span>
	        <input type="text" size="2" name="minutes" onchange="minute_test(this);">
	      </p>
	    </td>
	  </tr>
	  <tr>
	    <td>
	      <p><span>Backup every: </span>
	        <label><input type="text" size="2" name="days"> day(s)</label>
	      </p>
	    </td>
	  </tr>
	  <tr>
	    <td>
	      <p><span>Rotate: </span>
	        <input type="text" size="3" name="rotate" onchange="rot_test(this);">
	      </p>
	    </td>
	  </tr>  
	  <tr>
	    <td>""")
        for appid in applst:
                app = managers.xml_manager.get_application(appid)
                appname = app.name
                request.write("""
	     <p><input type="checkbox" name="appl[]" value="%s"><span> Name: "%s" GUID: (%s)</span></p>""" % (appid, appname, appid))
        request.write("""
	    </td>
	  </tr>
          <tr>
            <td>
              <input type="submit" name="addsd" value="Add">
              <input type="submit" name="update" value="Update">
              <input type="submit" name="delete" value="Delete">
            </td>
          </tr>  
	</table>
	</form>
     </td>
   </tr>
 </table>""")
        if "devid" in args and args["devid"][0] != "":
                request.write("""
<script language="javascript">
   function in_array(needle, haystack, strict) {
     var found = false, key, strict = !!strict;
     for (key in haystack) {
       if ((strict && haystack[key] === needle) || (!strict && haystack[key] == needle)) {
         found = true;
         break;
       }
     }
     return found;
   }
   
   var form = document.configBackup;
   form["addsd"].disabled=true;
   var el = form["devselect"];
   el.disabled=true;
   var applst = %s;
   for (var i=0; i<el.options.length; i++){
      if (el.options[i].value == '%s'){
        el.options[i].selected=true;
      }else{
        el.options[i].selected=false;
      }
   }
   form["hour"].value = '%s';
   form["minutes"].value = '%s';
   form["days"].value = '%s';
   var check = document.getElementsByName("appl[]")
   for (var i=0; i<check.length; i++){
      if (in_array(check[i].value, applst)) check[i].checked = true; else check[i].checked = false;
   }

</script>""" % (json.dumps(applist), sd.dev, inter[1], inter[0], inter[2].strip('*/') if inter[2] else "30"))
        if not "devid" in args:
                request.write("""
<script language="javascript">var form = document.configBackup; form["update"].disabled=true; form["delete"].disabled=true;</script>""")
        request.write("""
<script language="javascript">
function hour_test(input) {
    var re = /^(([0,1][0-9])|(2[0-3]))$/;
    if (!(re.test(input.value))) input.value = '';
}
function minute_test(input) {
    var re = /^[0-5][0-9]$/;
    if (!(re.test(input.value))) input.value = '';
}
function rot_test(input){
    var re = /\d*/;
    if (!(re.test(input.value))) input.value = '';
}
</script>
</body>
</html>""")