
import sys, time, threading, signal
from utils.singleton import VDOM_singleton
import managers
from thread import VDOM_thread
from daemon import VDOM_daemon


class VDOM_server(VDOM_singleton):

	def __init__(self, name=None, quantum=0.5):
		VDOM_singleton.__init__(self)
		self.__running=True
		self.__quantum=quantum
		signal.signal(signal.SIGTERM, self.terminate)
		current=threading.current_thread()
		current.name="Main"
		self.__ident=current.ident

	running=property(lambda self: self.__running)
	quantum=property(lambda self: self.__quantum)

	def prepare(self):
		pass

	def cleanup(self):
		pass

	def main(self):
		try:
			while self.__running: time.sleep(self.__quantum)
		except KeyboardInterrupt:
			pass
			#debug("Force shutdown by keyboard")

	def start(self):
		try:
			self.prepare()
			self.main()
		except:
			raise
			#debug("Force shutdown due exception")
			#pass
		finally:
			self.stop()
			#debug("STOP THREADS")
			self.notify(lambda thread: not isinstance(thread, VDOM_daemon))
			#debug("STOP DAEMONS")
			self.notify(lambda thread: isinstance(thread, VDOM_daemon) and not thread.dependencies)
			#debug("CLEANUP")
			self.cleanup()

	def stop(self):
		self.__running=False

	def terminate(self):
		#debug("Force shutdown by signal")
		self.stop()

	def notify(self, condition):
		while True:
			threads=tuple(thread for thread in threading.enumerate() if isinstance(thread, VDOM_thread) and condition(thread))
			if not threads: return
			for thread in threads:
				if thread.running:
					#debug("STOP %s"%thread.name)
					thread.stop()
			#debug("WAIT FOR %s"%thread.name)
			threads[0].join(self.__quantum)
