"""
Source manager: file swap
"""

from src.util.exception import VDOM_exception
import src.util.uuid
import src.file_access
import cPickle

class VDOM_source_swap:

	def __init__(self):
		self.__swap_file_index = {}
		
	def pop(self, application_id, container_id, action_name, context):
		"""Retreives file from swap (None if not exists) and delete file"""
		try:
			filename = self.__swap_file_index[(application_id,container_id, action_name, context)]
			if filename == None:
				
				return None
			else:
				content =  self.__pop(application_id,filename)
		except:
			return None
		self.__swap_file_index.pop((application_id,container_id, action_name, context))
		return content
	
	def __pop(self, application_id, name):
		"""Private. Retreives file from swap (None if not exists) and delete file"""
		if(src.file_access.file_manager.exists(src.file_access.cache, application_id, None, name)):
			return None
		#not safe =(
		content = src.file_access.file_manager.read(src.file_access.cache, application_id, None, name)
		src.file_access.file_manager.delete(src.file_access.cache, application_id, None, name)

		return cPickle.loads(content)

	def push(self, application_id, container_id, action_name, context, content):
		"""Store file in disk swap"""
		name = str(src.util.uuid.uuid4())
		self.__swap_file_index[(application_id,container_id, action_name, context)] = name
		return src.file_access.file_manager.write(src.file_access.cache, application_id, None, name, cPickle.dumps(content))

internal_swap=VDOM_source_swap()
del VDOM_source_swap
