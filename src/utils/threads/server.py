
import sys, time, threading, signal
from utils.singleton import VDOM_singleton
from thread import VDOM_thread
from daemon import VDOM_daemon
import auxiliary
from utils.tracing import show_threads_trace


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
		finally:
			show_threads_trace(details=None)

	def start(self):
		try:
			self.prepare()
			self.main()
		finally: # TODO: Rewrite
			self.stop()
			sys.stderr.write("Stop threads...\n")
			self.notify(lambda thread: not isinstance(thread, VDOM_daemon))
			sys.stderr.write("Stop daemons...\n")
			self.notify(lambda thread: isinstance(thread, VDOM_daemon) and not thread.dependencies)
			self.cleanup()

	def stop(self):
		self.__running=False

	def terminate(self,signum=None, frame=None):
		print "Catch SIGTERM. Server termination in process"
		self.stop()

	def notify(self, condition):
		ignore=set();
		while True:
			threads=tuple(thread for thread in threading.enumerate() if isinstance(thread, VDOM_thread) and condition(thread))
			if not threads: return
			for thread in threads:
				if thread in ignore: continue
				if thread.running:
					thread.stop()
					ignore.add(thread)
			threads[0].join(self.__quantum)
