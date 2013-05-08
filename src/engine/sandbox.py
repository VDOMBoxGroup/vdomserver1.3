"""
Sandbox
"""

import sys
import thread
import time
from utils.exception import VDOM_timeout_exception

class VDOM_sandbox:
	""" Sandbox class"""

	def __init__(self, routine):
		""" Constructor """
		self.__routine=routine

	def execute(self, timeout, arguments=None):
		""" Execute code """
		self.deadline=time.time()+timeout
		sys.settrace(self.globaltrace)
		try:
			if arguments:
				return self.__routine(arguments)
			else:
				return self.__routine()
		finally:
			sys.settrace(None)

	def globaltrace(self, frame, event, arg):
		""" Global trace routine """
		# debug("[Trace] Global %s/%s/%s"%(str(frame), str(event), str(arg)))
		if event=='call':
			return self.localtrace
		else:
			return None

	def localtrace(self, frame, event, arg):
		# debug("[Trace] Local %s/%s/%s"%(str(frame), str(event), str(arg)))
		""" Local trace routine """
		if event=='line' and time.time()>self.deadline:
			c_byte = ord( frame.f_code.co_code[frame.f_lasti] )
			#If next command is try - then let python register it before terminating. Used to avoid deadlocks
			if c_byte == 122: # SETUP_FINALLY byte
				return self.localtrace			
			sys.settrace(None)
			raise VDOM_timeout_exception("Routine not responding in given timeout")
		return self.localtrace
