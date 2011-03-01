
import time, threading
import auxiliary
from thread import VDOM_thread

class VDOM_daemon(VDOM_thread):

	def __init__(self, name=None, sleep=auxiliary.quantum, dependencies=None):
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
