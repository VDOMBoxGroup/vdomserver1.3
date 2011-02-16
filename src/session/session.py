"""session module"""

import sys, string, time, os, shutil, copy
from utils.id import VDOM_id
from utils.exception import *
import managers


class VDOM_session(dict):
	"""session class"""

	def __init__(self):
		"""session constructor"""
		dict.__init__(self)
		id_obj = VDOM_id()
		self.__id = id_obj.new()
		self.context = {}
		self.on_start_executed = False
		self.__user = ""
		self.update()

	def id(self):
		"""access id property"""
		return self.__id

	def update(self):
		"""update last access time"""
		self.__last_access = time.time()

	def is_expired(self, tout):
		"""check if session is expired"""
		if self.__last_access < time.time() - tout:
			return True
		return False

	def value(self, key, value=None):
		"""access session values"""
		if value is not None:
			self[key] = value
			return value
		elif key in self:
			return self[key]
		else:
			return None

	def remove(self, key):
		"""remove data"""
		self.__delitem__(key)

	def get_key_list(self):
		"""get list of keys"""
		return self.keys()

	def __setitem__(self, key, value):
		self.update()
		if not isinstance(key, basestring):
			raise TypeError()
		dict.__setitem__(self, key, value)

	def __getitem__(self, key):
		self.update()
		if not isinstance(key, basestring):
			raise TypeError()
		if dict.__contains__(self, key):
			return dict.__getitem__(self, key)
		return None

	def __delitem__(self, key):
		self.update()
		if dict.__contains__(self, key):
			dict.__delitem__(self, key)

	def __contains__(self, key):
		self.update()
		if not isinstance(key, basestring):
			raise TypeError()
		return dict.__contains__(self, key)

	def set_user(self, login, password, md5 = False):
		if md5:
			if managers.user_manager.match_user_md5(login, password):
				self.__user = login
				return
		else:
			if managers.user_manager.match_user(login, password):
				self.__user = login
				return
		raise VDOM_exception_sec("Authentication failed")

	def __get_user(self):
		return self.__user

	user = property(__get_user)
