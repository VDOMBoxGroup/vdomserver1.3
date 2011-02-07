"""
Source manager: source cache
"""

import sys

import src.file_access
import src.util.id 
from src.util.exception import VDOM_exception 

class VDOM_source_cache(object):
	"""source cache class"""

	def __init__(self):
		self.__cache_file_index = {}
		self.__cache_list = []
		self.__memused = 0

	def get_source(self, application, container, action_name, context):
		"""geting source code of compiled VDOM object"""
		source = None
		try: 
			source = self.__cache_file_index[(application.id, container.id, action_name, context)]
		except:
			pass # WHAT IS THIS!?!
		if source is not None:
			return source
		source = src.source.swap.pop(application.id, container.id, action_name, context)
		if source is None:
			source = src.source.compiler.compile(application, container, action_name, context)
		if source is not None:
			requered = source.size()
			self.check_space(requered)
			self.__memused = self.__memused + requered
			self.__cache_file_index[(application.id, container.id, action_name, context)] = source
			self.__cache_list.insert(0,(application.id, container.id, action_name, context))
			return source
		
	def check_space(self, requested):
		""""""
		memquote = int(VDOM_CONFIG["SERVER-SOURCE-MANAGER-MEMORY-QUOTE"])
		while False and self.__memused + requested > memquote and self.__memused > 0:
			(id_application, id_container, action_name, context) = self.__cache_list.pop()
			source = self.__cache_file_index[(id_application, id_container, action_name, context) ]
			src.source.swap.push(id_application, id_container, action_name, context, source)
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
#		src.source.swap.pop(id_application, id_container, action_name, context)

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
				src.source.swap.pop(id_application, id_container, action_name, context)

	def clear_container_swap(self,application_id):
		src.file_access.file_manager.clear(src.file_access.cache, application_id, None)

	def store_type(self,identificator,content):
		"""storing source file for Native types"""
		src.file_access.file_manager.write(src.file_access.type_source, identificator, None, src.util.id.guid2mod(identificator) + ".py", "# coding=utf-8\n\n" + content, encode=True)

	def clear_type_sources(self,type_id):
		src.file_access.file_manager.clear(src.file_access.type_source, type_id, None)

internal_cache=VDOM_source_cache()
del VDOM_source_cache
