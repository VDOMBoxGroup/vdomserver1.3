
import time, threading
import managers


class VDOM_thread(threading.Thread):

	def __init__(self, name=None, sleep=1):
		threading.Thread.__init__(self, name=name)
		self.__server=managers.server
		self.__running=True
		self.__sleep=sleep

	server=property(lambda self: self.__server)
	running=property(lambda self: self.__running)

	def prepare(self):
		pass

	def cleanup(self):
		pass

	def work(self):
		pass

	def main(self):
		while self.__running:
			if not self.work():
				remainder=self.__sleep
				while remainder>0 and self.__running:
					value=min(self.__server.quantum, remainder)
					time.sleep(value)
					remainder-=value

	def run(self):
		try:
			self.prepare()
			self.main()
		finally:
			self.cleanup()

	def stop(self):
		self.__running=False
