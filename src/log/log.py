"""
log module
"""

import time, thread, sys, os
import logging
import logging.handlers

from util.semaphore import VDOM_semaphore

class VDOM_log_manager:
	"""log class"""

	def __init__(self):
		"""constructor"""
		self.message_info 		= 0
		self.message_error 		= 1

		self.log_server			= 0
		self.log_user			= 1
		self.log_bug			= 2

		self.message_types = {
			self.message_info:		"INFO",
			self.message_error:		"ERROR"
		}

		self.__sem = VDOM_semaphore()
		formatter = logging.Formatter('%(asctime)s %(name)-12s %(message)s', '%d %b %Y %H:%M:%S')
		log_dir = VDOM_CONFIG["LOG-DIRECTORY"]
		h1 = logging.handlers.RotatingFileHandler(log_dir + "/server", "a", VDOM_CONFIG["LOG-FILE-SIZE"], VDOM_CONFIG["LOG-FILE-COUNT"])
		h2 = logging.handlers.RotatingFileHandler(log_dir + "/user", "a", VDOM_CONFIG["LOG-FILE-SIZE"], VDOM_CONFIG["LOG-FILE-COUNT"])
		h3 = logging.handlers.RotatingFileHandler(log_dir + "/bug", "a", VDOM_CONFIG["LOG-FILE-SIZE"], VDOM_CONFIG["LOG-FILE-COUNT"])
		h1.setLevel(logging.NOTSET)
		h2.setLevel(logging.NOTSET)
		h3.setLevel(logging.NOTSET)

		self.logger_server = logging.getLogger('vdom.server')
		self.logger_user = logging.getLogger('vdom.user')
		self.logger_bug = logging.getLogger('vdom.bug')
		self.logger_server.addHandler(h1)
		self.logger_user.addHandler(h2)
		self.logger_bug.addHandler(h3)

		h1.setFormatter(formatter)
		h2.setFormatter(formatter)
		h3.setFormatter(formatter)

		self.__queue = []
		thread.start_new_thread(self.__write_thread, ())
		self.__write_start()

	def __del__(self):
		self.__write_close()

	def __write_thread(self):
		"""thread that implements async writing"""
		while True:
			if len(self.__queue) > 0:
				self.__sem.lock()
				while len(self.__queue) > 0:
					(msg, l) = self.__queue.pop(0)
					if l == self.log_server:
						self.logger_server.error(msg)
					elif l == self.log_user:
						self.logger_user.error(msg)
					elif l == self.log_bug:
						self.logger_bug.error(msg)
				self.__sem.unlock()
			time.sleep(0.1)

	def __write_start(self):
		"""write startup message"""
		self.__write_message(self.message_info, "Server log", "Logger started", self.log_server)
		self.__write_message(self.message_info, "User log", "Logger started", self.log_user)
		self.__write_message(self.message_info, "Bug log", "Logger started", self.log_bug)

	def __write_close(self):
		"""write shutdown message"""
		self.__write_message(self.message_info, "Server log", "Logger terminated", self.log_server)
		self.__write_message(self.message_info, "User log", "Logger terminated", self.log_user)
		self.__write_message(self.message_info, "Bug log", "Logger terminated", self.log_bug)

	def __write_message(self, message_type, caller, message_text, log_type):
		"""general logging method"""
		_msg = message_text
		if message_type in self.message_types:
			_msg = self.message_types[message_type] + ": " + str(_msg)
		if "" != caller:
			_msg += " (%s)" % caller
		self.__sem.lock()
		self.__queue.append((_msg, log_type))
		self.__sem.unlock()

	def info(self, log_type, message_text, caller=""):
		"""write info message"""
		self.__write_message(self.message_info, caller, message_text, log_type)

	def error(self, log_type, message_text, caller=""):
		"""write error message"""
		self.__write_message(self.message_error, caller, message_text, log_type)

	# =========================================================================================

	def info_server(self, message_text, caller=""):
		"""write info message"""
		self.__write_message(self.message_info, caller, message_text, self.log_server)

	def error_server(self, message_text, caller=""):
		"""write error message"""
		self.__write_message(self.message_error, caller, message_text, self.log_server)

	def info_user(self, message_text, caller=""):
		"""write info message"""
		self.__write_message(self.message_info, caller, message_text, self.log_user)

	def error_user(self, message_text, caller=""):
		"""write error message"""
		self.__write_message(self.message_error, caller, message_text, self.log_user)

	def info_bug(self, message_text, caller=""):
		"""write info message"""
		self.__write_message(self.message_info, caller, message_text, self.log_bug)

	def error_bug(self, message_text, caller=""):
		"""write error message"""
		self.__write_message(self.message_error, caller, message_text, self.log_bug)


log_manager_internal = VDOM_log_manager()
del VDOM_log_manager
