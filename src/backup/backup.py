from extracter import VDOM_extracter
from subprocess import *
import shlex, shutil

class VDOM_backup(object):


	def backup(self, app_id, path, rotation, no_encryption=0):
		if not path:
			debug("Storage driver is not mounted")
			return
		el = VDOM_extracter.get_extracters(app_id)
		all_path = {key: value.extract() for key, value in el.items()}
		src_path = {key: value for key, value in all_path.items() if value}
		return self.__do_backup(app_id, path, src_path, rotation, no_encryption)


	def __do_backup(self, app_id, path, src_path, rotation, no_encryption=0):
		debug("DO_BACKUP Called PATH: %s"%(path))
		ok = True
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
			#ok = True
			for dirname in src_path:
				# get password from PC/SC
				from utils.card_connect import send_to_card_and_wait
				result = send_to_card_and_wait("getlicense %s %s" % ("0", "114"),"%s/%s" % ("0", "114"))
				crypto_arg=""
				if not result:
					# default password
					crypto_arg="--passphrase vdom"
				else:
					# password from PC/SC
					crypto_arg="--passphrase %s" % result
				debug("Crypto argument :: %s" % crypto_arg)
				no_encryption_arg = "-N" if no_encryption == 1 else ""
				cmd = """sh /opt/boot/do_backup.sh --guid %s --mountpoint %s --rotate %s %s --current  %s -n %s  -p %s %s %s"""%(app_id, path, rotation, prev, current_rev, dirname, src_path[dirname], crypto_arg, no_encryption_arg)
				out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
				out.wait()
				rc = out.returncode

				if rc == 0:
					continue
				else:
					debug(str(out.stderr.read()))
					debug("%s has not backuped" % dirname)
					ok = False
					errorcode = (rc, unicode(out.stdout))
					break

			for dirname in src_path:
				if not src_path[dirname].startswith(VDOM_CONFIG["FILE-STORAGE-DIRECTORY"]) and not src_path[dirname].startswith(VDOM_CONFIG["SHARE-DIRECTORY"]):
					shutil.rmtree(src_path[dirname], ignore_errors = True)
			if not ok:
				exit_error = "Some parts of application (id = %s) has not backuped\nReturn code: %s\nMessage: %s" % (app_id, errorcode[0], errorcode[1])
				return (rc, exit_error)
			else:
				return (rc, current_rev)
		else:
			errorcode = (rc, unicode(out.stdout))
			exit_error = "Return code: %s\nMessage: %s" % errorcode
			debug(exit_error)
			return (rc, exit_error)

backup = VDOM_backup()
# fake revision