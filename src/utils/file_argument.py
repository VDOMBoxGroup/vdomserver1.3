import __builtin__


class File_argument(object):
	def __init__(self,fileobj, name):
		self.fileobj = fileobj
		self.name = name
	def __getitem__(self, key):
		if not isinstance(key, int):
			raise TypeError
		if key == 0:
			self.__fileobj.seek(0)
			value = self.__fileobj.read()
			self.__fileobj.seek(0)
			return value
		elif key == 1:
			return self.__name
		else:
			raise AttributeError
		
class Attachment(object):
	def __init__(self, file_argument):
		self.__filearg = file_argument
	def __get_filename(self):
		return self.__filearg.name
	def __get_handler(self):
		return self.__filearg.fileobj
	
	name = property(__get_filename)
	handler = property(__get_handler)

__builtin__.Attachment = Attachment