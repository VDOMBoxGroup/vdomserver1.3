import __builtin__


class File_argument(object):
	def __init__(self,fileobj, name):
		self.fileobj = fileobj
		self.name = self.__try_decode(name)
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