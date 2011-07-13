"""
Source manager: source cache
"""

import sys

import managers, file_access
import utils.id 
from utils.exception import VDOM_exception 

class VDOM_source_cache(object):
	"""source cache class"""

	def __init__(self):
		self.__cache_file_index = {}
		self.__cache_list = []
		self.__memused = 0

	def get_source(self, application, container, action_name, context):
		"""geting source code of compiled VDOM object"""
		source = self.__cache_file_index.get((application.id, container.id, action_name, context),None)
		if source is not None:
			return source
		source = managers.source_swap.pop(application.id, container.id, action_name, context)
		if source is None:
			source = managers.compiler.compile(application, container, action_name, context)
		if source is not None:
			requered = source.size()
			self.check_space(requered)
			self.__memused = self.__memused + requered
			self.__cache_file_index[(application.id, container.id, action_name, context)] = source
			self.__cache_list.insert(0,(application.id, container.id, action_name, context))
			return source
		print "SOURCE6"
		
	def check_space(self, requested):
		""""""
		memquote = int(VDOM_CONFIG["SERVER-SOURCE-MANAGER-MEMORY-QUOTE"])
		while False and self.__memused + requested > memquote and self.__memused > 0:
			(id_application, id_container, action_name, context) = self.__cache_list.pop()
			source = self.__cache_file_index[(id_application, id_container, action_name, context) ]
			managers.source_swap.push(id_application, id_container, action_name, context, source)
			self.__memused = self.__memused - source.size()
		if self.__memused < 0:
			self.__memused = 0
			raise VDOM_exception(_("Memory leak while source swaping"))

#	def invalidate(self,id_application, id_container, action_name, context):
#		"""seting source code as invalid and removing it from cache or swap"""
#		obj = self.__cache_file_index.pop((id_application, id_container, action_name, context), None)
#		if not obj: return
#		size = obj.size()
#		self.__cache_list.remove((id_application, id_container, action_name, context))
#		self.__memused = self.__memused - size
#		managers.source_swap.pop(id_application, id_container, action_name, context)

	def invalidate(self, id_application, id_container):
		"""seting source code as invalid and removing it from cache or swap"""
		delete_list=[(id1, id2, a1, a2) for id1, id2, a1, a2 in \
			self.__cache_file_index if id1==id_application and id2==id_container]
		for id_application, id_container, action_name, context in delete_list:
			obj = self.__cache_file_index.pop((id_application, id_container, action_name, context), None)
			if obj:
				size = obj.size()
				self.__cache_list.remove((id_application, id_container, action_name, context))
				self.__memused = self.__memused - size
				managers.source_swap.pop(id_application, id_container, action_name, context)
	
	def clear_cache(self):
		self.__cache_file_index = {}
		self.__cache_list = []
		self.__memused = 0
		source.swap.clear()
		
	def clear_container_swap(self,application_id):
		managers.file_manager.clear(file_access.cache, application_id, None)

	def store_type(self,identificator,content):
		"""storing source file for Native types"""
		managers.file_manager.write(file_access.type_source, identificator, None, utils.id.guid2mod(identificator) + ".py", "# coding=utf-8\n\n" + content, encode=True)

	def clear_type_sources(self,type_id):
		managers.file_manager.clear(file_access.type_source, type_id, None)
