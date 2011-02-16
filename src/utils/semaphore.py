
from threading import BoundedSemaphore as sem

class VDOM_semaphore:

	def __init__(self, counter=1):
		self.__semaphore = sem(counter)

	def lock(self):
		self.__semaphore.acquire()

	def unlock(self):
		self.__semaphore.release()	
