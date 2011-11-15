import managers, utils.uuid
import task
from subprocess import *
import shlex

class VDOM_scheduler_manager(object):

        def __init__(self):
                self.__task_list = {}
                self.__crontab_builder = VDOM_crontab_builder()
		self.__cron = []

        def restore(self):
                self.__task_list = managers.storage.read_object(VDOM_CONFIG["SCHEDULER-MANAGER-INDEX-STORAGE-RECORD"])
                if not self.__task_list:
                        self.__task_list = {}
		else:
			self.clean_crontab()
			for tid in self.__task_list:
				if hasattr(self.__task_list[tid][0], 'in_cron') and self.__task_list[tid][0].in_cron:
					self.__cron.append((tid, self.__task_list[tid][1]))
			if self.__cron:
				self.build_crontab(self.__cron)
				
        def fetch(self, task_class):
                concrete_task_list = {}
                for key in self.__task_list:
                        if isinstance(self.__task_list[key][0], task_class):
                                concrete_task_list[key] = self.__task_list[key]

                return concrete_task_list

        def add_task(self, task_object, interval):
                task_id = str(utils.uuid.uuid4())
                self.__task_list[task_id] = (task_object, interval)
                managers.storage.write_object_async(VDOM_CONFIG["SCHEDULER-MANAGER-INDEX-STORAGE-RECORD"],self.__task_list)
                return task_id

        def update (self, task_id, task, interval):
                if task_id in self.__task_list:
                        self.__task_list[task_id] = (task, interval)
                        managers.storage.write_object_async(VDOM_CONFIG["SCHEDULER-MANAGER-INDEX-STORAGE-RECORD"],self.__task_list)
			return True
                else:
                        return False

        def dell_task(self, task_id):
                remove_list = []
                for key in self.__task_list:
                        if task_id == key:
                                remove_list.append(key)

                                is_dirty_index = False
                for key in remove_list:
                        self.__task_list.pop(key)
                        is_dirty_index = True

                        if is_dirty_index:
                                managers.storage.write_object_async(VDOM_CONFIG["SCHEDULER-MANAGER-INDEX-STORAGE-RECORD"],self.__task_list)

        def on_signal(self, task_id):
                if task_id in self.__task_list:
                        task = self.__task_list[task_id][0]
                        task.run()
                else:
                        pass

        def build_crontab(self, tasks):
		self.__cron = tasks
                self.__crontab_builder.set_crontab(tasks)
        
        def get_crontab(self):
                return self.__cron
	
	def clean_crontab(self):
		self.__cron = []
		self.__crontab_builder.clean_crontab()
        
class VDOM_crontab_builder(object):
        
        def set_crontab(self, tasks):
		"""parameters is a list of tuples (task_id, interval)
		interval is a tuple of the form ('minute','hour','day','week','month')"""
		# tasks = [(tid, ("34","1","*/1","*","*")), ... ]

		crontab = "/var/spool/cron/crontabs/root"
		cron_handler = open(crontab, "wb")
		for task in tasks:
			t_id, intervals = task
			m, h, d, w, M = intervals
			debug("""%s %s %s %s %s %s \n"""%(m, h, d, w, M, t_id))
			cron_handler.write("""%s %s %s %s %s  /opt/boot/./do_scheduler_task.sh --tid %s \n"""%(m, h, d, w, M, t_id))
		cron_handler.close()
		cmd = """/usr/bin/crontab %s """%(crontab)
		out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
		out.wait()
		rc = out.returncode

		# if exitcode == 0
		if rc == 0:
		    debug("Crontab build OK")
		else:
		    debug("Crontab build failed")

	def clean_crontab(self):
		crontab = "/var/spool/cron/crontabs/root"
		cron_handler = open(crontab, "wb")
		cron_handler.write("")
		cron_handler.close()