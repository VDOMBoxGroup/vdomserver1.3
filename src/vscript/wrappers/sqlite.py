
import re
from database.dbobject import VDOM_sql_query as sql_query
import managers
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *



class v_vdomdbrow(generic):

	def __init__(self, value):
		self.__value=value

	def __call__(self, index): # , *arguments, **keywords
		index=as_value(index)
		if isinstance(index, (integer, string)):
			return pack(self.__value[index.value])
		else:
			raise errors.invalid_procedure_call

	def v_length(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("length")
		else:
			return integer(len(self.__value))

class v_vdomdbrecordset_iterator(generic):

	def __init__(self, iterator):
		self.__iterator=iterator

	def next(self):
		return v_vdomdbrow(self.__iterator.next())

class v_vdomdbrecordset(generic):

	def __init__(self, value):
		generic.__init__(self)
		self.__value=value

	def __call__(self, index): # , *arguments, **keywords
		index=as_integer(index)
		return v_vdomdbrow(self.__value[index])

	def __iter__(self):
		return v_vdomdbrecordset_iterator(iter(self.__value))

	def __len__(self):
		return len(self.__value)

	def __nonzero__(self):
		return len(self.__value)

	def __invert__(self):
		return len(self.__value)==0

	def v_length(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("length")
		else:
			return integer(len(self.__value))

class v_vdomdbconnection(generic):

	def __init__(self):
		generic.__init__(self)
		self.__application_id=managers.request_manager.current.application_id
		self.__database_id=None
		self.__database_name=None

	def v_open(self, connection_string):
		if self.__database_id is not None:
			raise errors.invalid_procedure_call(name="open")
		connection_string=as_string(connection_string).lower()
		if re.search("[0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12}", connection_string):
			self.__database_id=connection_string.lower()
			self.__database_name=None
		else:
			self.__database_id=managers.database_manager.list_names(self.__application_id)[connection_string]
			self.__database_name=connection_string

	def v_close(self):
		if self.__database_id is None:
			raise errors.invalid_procedure_call(name="close")
		self.__database_id=None
		self.__database_name=None

	def v_execute(self, query, parameters=None):
		if self.__database_id is None:
			raise errors.invalid_procedure_call(name="execute")
		query=as_string(query)
		if parameters is not None:
			raise errors.invalid_procedure_call(name="execute")
			parameters=as_array(parameters)
		query=sql_query(self.__application_id, self.__database_id, query, parameters, executescript=True)
		query.commit()

	def v_query(self, query, parameters=None):
		if self.__database_id is None:
			raise errors.invalid_procedure_call(name="query")
		query=as_string(query)
		if parameters is not None:
			raise errors.invalid_procedure_call(name="query")
			parameters=as_array(parameters).as_list()
		query=sql_query(self.__application_id, self.__database_id, query, parameters, executemany=True)
		# , simple_rows=True
		return v_vdomdbrecordset(query.fetchall())
