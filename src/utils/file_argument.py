class File_argument(object):
	def __init__(self,fileobj, name):
		self.__fileobj = fileobj
		self.__name = name
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