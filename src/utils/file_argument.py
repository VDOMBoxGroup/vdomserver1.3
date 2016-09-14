import __builtin__
import os
import time
from types import FileType
class File_argument(object):
	def __init__(self,fileobj, name):
		"""File argument wrapper for uploaded files"""
		self.fileobj = fileobj
		self.name = self.__try_decode(name)
		self.autoremove = True
	def __getitem__(self, key):
		if not isinstance(key, int):
			raise TypeError
		if key == 0:
			self.fileobj.seek(0)
			value = self.fileobj.read()
			self.fileobj.seek(0)
			return value
		elif key == 1:
			return self.name
		else:
			raise AttributeError
		
	def __try_decode(self, item):
		if isinstance(item, str):
			return unicode(item.decode("utf-8", "ignore"))
		else:
			return item
		
	def remove(self):
		"""Remove uploaded file from HDD"""
		if self.fileobj:
			filepath = getattr(self.fileobj,"name",None)
			if not self.fileobj.closed:
				self.fileobj.close()
			if filepath:
				try:
					os.remove(filepath)
				except Exception as e:
					print (str(e))
			self.fileobj = None#TODO: maybe not none bug StringIO()?
		
	def close(self):
		"""Close file object and give name"""
		self.fileobj.close()
		return getattr(self.fileobj,"name")

	
class Attachment(object):
	def __init__(self, file_argument):
		self.__filearg = file_argument
		
	def __get_filename(self):
		return self.__filearg.name
	def __get_handler(self):
		return self.__filearg.fileobj
	def _get_realpath(self):
		return getattr(self.__filearg.fileobj,"name",None)
	def _del_fileobj(self):
		self.__filearg.fileobj = None
	def remove(self):
		self.__filearg.remove()

	name = property(__get_filename)
	handler = property(__get_handler)

__builtin__.Attachment = Attachment