
import sys, time, threading, signal
from utils.singleton import VDOM_singleton
from thread import VDOM_thread
from daemon import VDOM_daemon
import auxiliary


class VDOM_server(VDOM_singleton):

	def __init__(self, name="Main"):
		VDOM_singleton.__init__(self)
		self.__quantum=auxiliary.quantum
		self.__running=True
		threading.current_thread().name=name
		auxiliary.server=self
		signal.signal(signal.SIGTERM, self.terminate)

	quantum=property(lambda self: self.__quantum)
	running=property(lambda self: self.__running)

	def prepare(self):
		pass

	def cleanup(self):
		pass

	def main(self):
		try:
			while self.__running: time.sleep(self.__quantum)
		except KeyboardInterrupt:
			pass

	def start(self):
		try:
			self.prepare()
			self.main()
		finally:
			self.stop()
			self.notify(lambda thread: not isinstance(thread, VDOM_daemon))
			self.notify(lambda thread: isinstance(thread, VDOM_daemon) and not thread.dependencies)
			self.cleanup()

	def stop(self):
		self.__running=False

	def terminate(self):
		self.stop()

	def notify(self, condition):
		while True:
			threads=tuple(thread for thread in threading.enumerate() if isinstance(thread, VDOM_thread) and condition(thread))
			if not threads: return
			for thread in threads:
				if thread.running: thread.stop()
			threads[0].join(self.__quantum)
