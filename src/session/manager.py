"""Session Manager module"""

import thread, time, copy

from session import VDOM_session
from src.util.semaphore import VDOM_semaphore
from src.util.exception import VDOM_exception
import src.managers

class VDOM_session_manager(dict):
	"""Session Manager class"""

	def __init__(self):
		"""constructor"""
		self.__timeout = VDOM_CONFIG["SESSION-LIFETIME"]
		self.__sem = VDOM_semaphore()
		#start clean thread
		thread.start_new_thread(self.clean_thread, ())
		dict.__init__(self)

	def check_sessions(self):
		"""clean timed-out sessions"""
		keys_copy = copy.deepcopy(self.keys())
		for sid in keys_copy:
			self[sid]

	def clean_thread(self):
		"""clean thread function"""
		interval = self.__timeout
		if interval < 3600:
			interval = 3600
		while True:
			time.sleep(interval)
			self.check_sessions()
		return 0

	def create_session(self):
		"""create session & return it`s id"""
		s = VDOM_session()
		self.__sem.lock()
		dict.__setitem__(self, s.id(), s)
		self.__sem.unlock()
		return s.id()

	def remove_session(self, session_id):
		self.__delitem__(session_id)

	def session_exists(self, session_id):
		return self.__contains__(session_id)

	def get_session(self, session_id):
		return self.__getitem__(session_id)

	def __setitem__(self, key, value):
		# not allowed
		raise AttributeError()

	def __getitem__(self, key):
		self.__sem.lock()
		try:
			if dict.__contains__(self, key):
				s = dict.__getitem__(self, key)
				if s.is_expired(self.__timeout):
					s.context = {}
					dict.__delitem__(self, key)
				else:
					return s
			return None
		finally:
			self.__sem.unlock()

	def __delitem__(self, key):
		self.__sem.lock()
		try:
			if dict.__contains__(self, key):
				s = dict.__getitem__(self, key)
				s.context = {}
				dict.__delitem__(self, key)
		finally:
			self.__sem.unlock()

	def __contains__(self, key):
		return dict.__contains__(self, key)

	def __get_current(self):
		self.__sem.lock()
		try:
			return src.managers.request_manager.current.session()
		finally:
			self.__sem.unlock()

	def __set_current(self, sess):
		self.__sem.lock()
		try:
			src.managers.request_manager.current.set_session_id(sess.id)
		finally:
			self.__sem.unlock()

	current = property(__get_current, __set_current)


internal_session_manager = VDOM_session_manager()
del VDOM_session_manager
