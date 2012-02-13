
import re
import managers
from database.dbobject import VDOM_sql_query as sql_query
from .. import errors
from ..subtypes import integer, generic, string, v_empty, v_nothing, v_mismatch
from ..variables import variant
from ..conversions import pack, unpack


class v_vdomdbrow(generic):

	def __init__(self, items):
		generic.__init__(self)
		self._items=items

	def __call__(self, index, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property
		else:
			index=index.as_simple
			if isinstance(index, (integer, string)):
				try: return pack(self._items[index.value])
				except KeyError: return v_empty
			else:
				raise errors.invalid_procedure_call


	def v_length(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("length")
		else:
			return integer(len(self._items))


	def __iter__(self):
		for item in self._items:
			yield variant(pack(item))

	def __len__(self):
		return integer(len(self._items))


class v_vdomdbrecordset(generic):

	def __init__(self, value):
		generic.__init__(self)
		self._items=value

	def __call__(self, index): # , *arguments, **keywords
		if let is not None or set is not None:
			raise errors.object_has_no_property
		else:
			try: return v_vdomdbrow(self._items[index.as_integer])
			except KeyError: return v_nothing


	def v_length(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("length")
		else:
			return integer(len(self._items))


	def __iter__(self):
		for item in self._items:
			yield variant(v_vdomdbrow(item))

	def __len__(self):
		return integer(len(self._items))


class v_vdomdbconnection(generic):

	check_regex=re.compile("[0-9A-Z]{8}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{12}", re.IGNORECASE)


	def __init__(self):
		generic.__init__(self)
		self._application_id=managers.request_manager.current.application_id
		self._database_id=None
		self._database_name=None


	def v_open(self, connection_string):
		if self._database_id is not None:
			raise errors.invalid_procedure_call(name="open")
		connection_string=connection_string.as_string.lower()
		if self.check_regex.search(connection_string):
			self._database_id=connection_string.lower()
			self._database_name=None
		else:
			self._database_id=managers.database_manager.list_names(self._application_id)[connection_string]
			self._database_name=connection_string
		return v_mismatch

	def v_close(self):
		if self._database_id is None:
			raise errors.invalid_procedure_call(name="close")
		self._database_id=None
		self._database_name=None
		return v_mismatch

	def v_execute(self, query, parameters=None):
		if self._database_id is None:
			raise errors.invalid_procedure_call(name="execute")
		query=query.as_string
		if parameters is not None:
			parameters=[unpack(parameter.as_simple) for parameter in parameters.as_array]
		query=sql_query(self._application_id, self._database_id, query, parameters)
		query.commit()
		return v_mismatch

	def v_query(self, query, parameters=None):
		if self._database_id is None:
			raise errors.invalid_procedure_call(name="query")
		query=query.as_string
		if parameters is not None:
			parameters=[unpack(parameter.as_simple) for parameter in parameters.as_array]
		query=sql_query(self._application_id, self._database_id, query, parameters, executemany=True)
		query.commit()
		return v_vdomdbrecordset(query.fetchall())
