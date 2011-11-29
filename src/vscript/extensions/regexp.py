
import re
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *



class v_match(generic):

	def __init__(self, sre_match):
		generic.__init__(self)
		self.__firstindex=sre_match.start()
		self.__length=sre_match.end()-self.__firstindex
		self.__value=sre_match.group()

	def v_firstindex(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property(u"firstindex")
		else:
			return integer(self.__firstindex)

	def v_length(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property(u"length")
		else:
			return integer(self.__length)

	def v_value(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property(u"value")
		else:
			return string(unicode(self.__value))

class v_matches_iterator(object):

	def __init__(self, iterator):
		self.__iterator=iterator

	def next(self):
		return v_match(self.__iterator.next())
			
class v_matches(generic):

	def __init__(self, regexp, value, everything):
		generic.__init__(self)
		self.__regexp=regexp
		self.__value=value
		self.__collection=None
		self.__everything=everything

	def __call__(self, index, *arguments, **keywords):
		index=as_integer(index)
		if not self.__collection:
			self.__collection=[match for match in self.__regexp.finditer(self.__value)]
		return v_match(self.__collection[index])

	def __iter__(self):
		return v_matches_iterator(self.__regexp.finditer(self.__value))

class v_regexp(generic):

	def __init__(self):
		generic.__init__(self)
		self.__global=False # TODO!!! COMPLETE SUPPORT
		self.__ignorecase=False
		self.__pattern=""
		self.__regexp=None

	def v_global(self, let=None, set=None):
		if let is not None:
			self.__global=as_boolean(let)
		elif set is not None:
			raise errors.object_has_no_property("global")
		else:
			return boolean(self.__global)

	def v_ignorecase(self, let=None, set=None):
		if let is not None:
			self.__ignorecase=as_boolean(let)
		elif set is not None:
			raise errors.object_has_no_property("ignorecase")
		else:
			return boolean(self.__ignorecase)

	def v_pattern(self, let=None, set=None):
		if let is not None:
			self.__pattern=as_string(let)
		elif set is not None:
			raise errors.object_has_no_property("pattern")
		else:
			return string(self.__pattern)

	def v_execute(self, value):
		value=as_string(value)
		if not self.__regexp:
			self.__regexp=re.compile(self.__pattern, re.IGNORECASE if self.__ignorecase else 0)
		return v_matches(self.__regexp, value, self.__global)

	def v_replace(self, value, replace_string):
		value=as_string(value)
		replace_string=as_string(replace_string)
		if not self.__regexp:
			self.__regexp=re.compile(self.__pattern, re.IGNORECASE if self.__ignorecase else 0)
		return string(unicode(replace_string.join(self.__regexp.split(value))))

	def v_test(self, value):
		value=as_string(value)
		if not self.__regexp:
			self.__regexp=re.compile(self.__pattern, re.IGNORECASE if self.__ignorecase else 0)
		return boolean(v_false_value if self.__regexp.search(value) is None else v_true_value)
