
import time, threading
import auxiliary


class VDOM_thread(threading.Thread):

	def __init__(self, name=None, sleep=auxiliary.quantum):
		threading.Thread.__init__(self, name=name)
		self.__server=auxiliary.server
		self.__quantum=auxiliary.quantum
		self.__running=True
		self.__sleep=sleep

	server=property(lambda self: self.__server)
	quantum=property(lambda self: self.__quantum)
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
					value=min(self.__quantum, remainder)
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
