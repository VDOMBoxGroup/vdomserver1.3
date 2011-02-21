
import time, threading
from managers import search_manager



class VDOM_thread(threading.Thread):

	def __init__(self, name=None, sleep=1):
		threading.Thread.__init__(self, name=name)
		self.__server=search_manager("server")
		self.__running=True
		self.__sleep=sleep

	running=property(lambda self: self.__running)

	def prepare(self):
		pass

	def cleanup(self):
		pass

	def work(self):
		pass

	def main(self):
		#while self.__server.running and self.__running:
		while self.__running:
			if not self.work():
				remainder=self.__sleep
				#while remainder>0 and self.__server.running and self.running:
				while remainder>0 and self.__running:
					sleep=min(self.__server.quantum, remainder)
					time.sleep(remainder)
					remainder-=sleep

	def run(self):
		try:
			self.prepare()
			self.main()
		except:
			raise
			#debug("Force shutdown due exception")
			#self.__server.stop()
		finally:
			self.cleanup()

	def stop(self):
		self.__running=False

class VDOM_daemon(VDOM_thread):

	def __init__(self, name=None, sleep=1, dependencies=None):
		VDOM_thread.__init__(self, name=name, sleep=sleep)
		self.__dependencies=[]
		if dependencies:
			if not isinstance(dependencies, (list, tuple)): dependencies=(dependencies,)
			mapping={thread.name: thread for thread in threading.enumerate() if thread.name in dependencies}
			if len(mapping)<len(dependencies):
				raise Exception("Require %s thread(s) to run"%", ".join(set(dependencies)-set(mapping)))
			for name, thread in mapping.items():
				assert isinstance(thread, VDOM_daemon)
				thread.__dependencies.append(self)

	dependencies=property(lambda self: tuple(thread for thread in self.__dependencies if thread.is_alive()))
