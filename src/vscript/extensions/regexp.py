
import re
from .. import errors
from ..subtypes import boolean, generic, string, true, false, v_empty
from ..variables import variant


# TODO: Support RegEx Global property


class v_match(generic):

	def __init__(self, match):
		generic.__init__(self)
		self._match=match


	def v_firstindex(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property(u"firstindex")
		else:
			return integer(self._match.start())

	def v_length(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property(u"length")
		else:
			return integer(self._match.end()-self._match.start())

	def v_value(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property(u"value")
		else:
			return string(unicode(self._match.group()))

	def v_group(self, group, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property(u"value")
		else:
			group=group.as_simple
			if isinstance(group, integer): group=group.as_integer
			elif isinstance(group, string): group=group.as_string
			else: raise errors.type_mismatch
			try: value=self._match.group(group)
			except IndexError: return v_empty
			return string(unicode(value))
			

class v_matches(generic):

	def __init__(self, regexp, value, everything):
		generic.__init__(self)
		self._regexp=regexp
		self._value=value
		self._collection=None
		self._everything=everything

	def __call__(self, index, *arguments, **keywords):
		index=index.as_integer
		if not self._collection:
			self._collection=[match for match in self._regexp.finditer(self._value)]
		return v_match(self._collection[index])

	def __iter__(self):
		for match in self._regexp.finditer(self._value):
			yield variant(v_match(match))


class v_regexp(generic):

	def __init__(self):
		generic.__init__(self)
		self._global=False
		self._ignorecase=False
		self._pattern=""
		self._regexp_cache=None


	def _get_regex(self):
		if not self._regexp_cache: self._regexp_cache=re.compile(self._pattern, \
			re.IGNORECASE if self._ignorecase else 0)
		return self._regexp_cache

	_regexp=property(_get_regex)


	def v_global(self, let=None, set=None):
		if let is not None:
			self._global=let.as_boolean
		elif set is not None:
			raise errors.object_has_no_property("global")
		else:
			return boolean(self._global)

	def v_ignorecase(self, let=None, set=None):
		if let is not None:
			self._ignorecase=let.as_boolean
			self._regexp_cache=None
		elif set is not None:
			raise errors.object_has_no_property("ignorecase")
		else:
			return boolean(self._ignorecase)

	def v_pattern(self, let=None, set=None):
		if let is not None:
			self._pattern=let.as_string
			self._regexp_cache=None
		elif set is not None:
			raise errors.object_has_no_property("pattern")
		else:
			return string(self._pattern)


	def v_execute(self, value):
		return v_matches(self._regexp, value.as_string, self._global)

	def v_replace(self, value, replace_string):
		return string(unicode(replace_string.as_string.join(self._regexp.split(value.as_string))))

	def v_test(self, value):
		return boolean(false if self._regexp.search(value.as_string) is None else true)
