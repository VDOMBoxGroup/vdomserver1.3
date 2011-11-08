from extracter import VDOM_extracter
from subprocess import *
import shlex

class VDOM_backup(object):
    

    def backup(self, app_id, path):
        
        el = VDOM_extracter.get_extracters(app_id)
        all_path = {key: value.extract() for key, value in el.items()}
        src_path = {key: value for key, value in all_path.items() if value}
        return self.__do_backup(app_id, path, src_path)
		
			
    def __do_backup(self, app_id, path, src_path):
	debug("DO_BACKUP Called PATH: %s"%(path))
	cmd = """sh /opt/boot/repo_browse.sh -p %s -g %s -l""" % (path, app_id)
	out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
	out.wait()
	rc = out.returncode

	# if exitcode == 0
	if rc == 0:
	    debug("DO_BACKUP rc=0")
	    # grab output
	    revs = str(out.stdout.read())
	    # make python list from shit
	    if not revs:
		debug("DO_BACKUP No Revisions")
		current_rev = "1"
		prev_rev = ""
	    else:
		debug("DO_BACKUP Prev Revisions exist")
		prev_rev = int(revs.strip('\n').split('\n')[-1])
		current_rev = str(prev_rev + 1)
		debug("DO_BACKUP Prev %s Current %s"%(prev_rev, current_rev))
		
		#prev_path = "%s/%s/%s"%(path,app_id,str(last_rev))
		#current_path = "%s/%s/%s"%(path,app_id,current_rev)
		# last %s compiled above.
	    prev = "--prev %s " % prev_rev if prev_rev else ""
	    ok = True
	    for dirname in src_path:
		cmd = """sh /opt/boot/do_backup.sh --guid %s --mountpoint %s %s --current %s -n %s  -p %s """%(app_id, path, prev, current_rev, dirname, src_path[dirname])
		out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
		out.wait()
		rc = out.returncode

		if rc == 0:
			continue
		else:
			debug(str(out.stderr.read()))
			debug("%s has not backuped" % dirname)
			ok = False
	    if not ok:
		exit_error = "Some parts of application (id = %s) has not backuped" % app_id
		return exit_error
	    else:
		return True
	else:
	    exit_error = "Unexpected Error"
	    debug(exit_error)
	    return exit_error

backup = VDOM_backup()