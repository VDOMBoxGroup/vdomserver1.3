"""
Source manager: file swap
"""

from utils.exception import VDOM_exception
import utils.uuid
import file_access
import cPickle
import managers


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
		if(managers.file_manager.exists(file_access.cache, application_id, None, name)):
			return None
		#not safe =(
		content = managers.file_manager.read(file_access.cache, application_id, None, name)
		managers.file_manager.delete(file_access.cache, application_id, None, name)

		return cPickle.loads(content)

	def push(self, application_id, container_id, action_name, context, content):
		"""Store file in disk swap"""
		name = str(utils.uuid.uuid4())
		self.__swap_file_index[(application_id,container_id, action_name, context)] = name
		return managers.file_manager.write(file_access.cache, application_id, None, name, cPickle.dumps(content))
