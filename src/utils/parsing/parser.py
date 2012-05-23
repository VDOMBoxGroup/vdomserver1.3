
import re
from xml.parsers.expat import errors as expat_errors, ParserCreate, ExpatError
from errors import *


__all__=["VDOM_parser"]


spaces=re.compile(r"[\r\n\s\t]+", re.IGNORECASE|re.MULTILINE)
erratic={
	1: VDOM_out_of_memory_error,					# XML_ERROR_NO_MEMORY
	# XML_ERROR_SYNTAX: Syntax error
	# XML_ERROR_NO_ELEMENTS: No element found
	# XML_ERROR_INVALID_TOKEN: Not well-formed (invalid token)
	# XML_ERROR_UNCLOSED_TOKEN: Unclosed token
	# XML_ERROR_PARTIAL_CHAR: Partial character
	# XML_ERROR_TAG_MISMATCH: Mismatched tag
	# XML_ERROR_DUPLICATE_ATTRIBUTE: Duplicate attribute
	9: VDOM_junk_after_document_error}				# XML_ERROR_JUNK_AFTER_DOC_ELEMENT
	# XML_ERROR_PARAM_ENTITY_REF: Illegal parameter entity reference
	# XML_ERROR_UNDEFINED_ENTITY: Undefined entity
	# XML_ERROR_RECURSIVE_ENTITY_REF: Recursive entity reference
	# XML_ERROR_ASYNC_ENTITY: Asynchronous entity
	# XML_ERROR_BAD_CHAR_REF: Reference to invalid character number
	# XML_ERROR_BINARY_ENTITY_REF: Reference to binary entity
	# XML_ERROR_ATTRIBUTE_EXTERNAL_ENTITY_REF: Reference to external entity in attribute
	# XML_ERROR_MISPLACED_XML_PI: XML or text declaration not at start of entity
	# XML_ERROR_UNKNOWN_ENCODING: Unknown encoding
	# XML_ERROR_INCORRECT_ENCODING: Encoding specified in XML declaration is incorrect
	# XML_ERROR_UNCLOSED_CDATA_SECTION: Unclosed CDATA section
	# XML_ERROR_EXTERNAL_ENTITY_HANDLING: Error in processing external entity reference
	# XML_ERROR_NOT_STANDALONE: Document is not standalone
	# XML_ERROR_UNEXPECTED_STATE: Unexpected parser state - please send a bug report
	# XML_ERROR_ENTITY_DECLARED_IN_PE: Entity declared in parameter entity
	# XML_ERROR_FEATURE_REQUIRES_XML_DTD: Requested feature requires XML_DTD support in Expat
	# XML_ERROR_CANT_CHANGE_FEATURE_ONCE_PARSING: Cannot change setting once parsing has begun
	# XML_ERROR_UNBOUND_PREFIX: Unbound prefix
	# XML_ERROR_UNDECLARING_PREFIX: Must not undeclare prefix
	# XML_ERROR_INCOMPLETE_PE: Incomplete markup in parameter entity
	# XML_ERROR_XML_DECL: XML declaration not well-formed
	# XML_ERROR_TEXT_DECL: Text declaration not well-formed
	# XML_ERROR_PUBLICID: Illegal character(s) in public id
	# XML_ERROR_SUSPENDED: Parser suspended
	# XML_ERROR_NOT_SUSPENDED: Parser not suspended
	# XML_ERROR_ABORTED: Parsing aborted
	# XML_ERROR_FINISHED: Parsing finished
	# XML_ERROR_SUSPEND_PE: Cannot suspend in external parameter entity


def encode_data(value):
	return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")

def encode_cdata(value):
	return value.replace("]]>", "]]]]><![CDATA[>")


def empty_builder(parser):
	def document_handler(name, attributes): parser.handle_unknown_element(name, attributes)
	return document_handler


class VDOM_parser(object):

	def __init__(self, builder=empty_builder, result=None):
		self._handler=builder(self)
		self._unexpected_attribute_handler=None
		self._unexpected_element_handler=None
		self._parser=ParserCreate()
		self._parser.StartElementHandler=self._handler
		self._result=result


	def _set_cache(self, value):
		self._parser.buffer_text=value

	def _set_cache_size(self, value):
		self._parser.buffer_size=value

	def _set_unexpected_attribute_handler(self, value):
		self._unexpected_attribute_handler=vakue

	def _set_unexpected_element_handler(self, value):
		self._unexpected_element_handler=value

	cache=property(lambda self: self._parser.buffer_text, _set_cache)
	cache_size=property(lambda self: self._parser.buffer_size, _set_cache_size)
	unexpected_attribute_handler=property(lambda self: self._unexpected_attribute_handler, _set_unexpected_attribute_handler)
	unexpected_element_handler=property(lambda self: self._unexpected_element_handler, _set_unexpected_element_handler)
	result=property(lambda self: self._result)


	def reset(self, result=None):
		cache=self._parser.buffer_text
		self._parser=ParserCreate()
		self._parser.buffer_text=cache
		self._parser.StartElementHandler=self._handler
		self._result=result
	
	def parse(self, document=None, chunk=None, filename=None):
		try:
			if document is not None:
				if isinstance(document, basestring): self._parser.Parse(document, True)
				else: self._parser.ParseFile(document)
			elif chunk is not None:
				self._parser.Parse(chunk)
			elif filename is not None:
				with open(filename) as file: self._parser.ParseFile(file)
			else:
				raise VDOM_missing_arguments_error
		except ExpatError as error:
			try: error=erratic[error.code]()
			except KeyError: error=VDOM_parsing_exception(error.message.split(":")[0].capitalize())
			error.lineno=self._parser.ErrorColumnNumber
			error.offset=self._parser.ErrorByteIndex
			raise error
		except VDOM_parsing_exception as error:
			error.lineno=self._parser.ErrorColumnNumber
			error.offset=self._parser.ErrorByteIndex
			raise
		return self._result

	def accept(self, result):
		self._result=result
		
	def handle_value_element(self, name, attributes, setter):
		for attribute in attributes:
			if self._unexpected_attribute_handler: self._unexpected_attribute_handler(attribute)
			else: raise VDOM_unexpected_attribute_error(attribute)
		chunks, chunks2clean=[], []
		context=self._parser.StartElementHandler, self._parser.EndElementHandler

		def data_handler(chunk):
			chunks2clean.append(chunk)

		def cdata_handler(chunk):
			chunks.append(u" ".join(filter(None, spaces.split(u"".join(chunks2clean)))))
			del chunks2clean[:]
			chunks.append(chunk)

		def cdata_section_handler():
			self._parser.CharacterDataHandler=cdata_handler

		def close_cdata_section_handler():
			self._parser.CharacterDataHandler=data_handler

		def element_handler(name, attributes):
			if self._unexpected_element_handler: self._unexpected_element_handler(name)
			else: raise VDOM_unexpected_element_error(attribute)
			context=self._parser.CharacterDataHandler, self._parser.StartCdataSectionHandler, \
				self._parser.EndCdataSectionHandler, self._parser.EndElementHandler

			def element_handler(name, attributes):
				context=self._parser.EndElementHandler

				def close_element_handler(name):
					self._parser.EndElementHandler=context

				self._parser.EndElementHandler=close_element_handler

			def close_element_handler(name):
				self._parser.CharacterDataHandler, self._parser.StartCdataSectionHandler, \
					self._parser.EndCdataSectionHandler, self._parser.EndElementHandler=context

			self._parser.CharacterDataHandler=None
			self._parser.StartCdataSectionHandler=None
			self._parser.EndCdataSectionHandler=None
			self._parser.StartElementHandler=element_handler
			self._parser.EndElementHandler=close_element_handler

		def close_element_handler(name):
			self._parser.CharacterDataHandler=None
			self._parser.StartCdataSectionHandler=None
			self._parser.EndCdataSectionHandler=None
			self._parser.StartElementHandler, self._parser.EndElementHandler=context
			chunks.append(u" ".join(filter(None, spaces.split(u"".join(chunks2clean)))))
			setter(u"".join(chunks))

		self._parser.CharacterDataHandler=data_handler
		self._parser.StartCdataSectionHandler=cdata_section_handler
		self._parser.EndCdataSectionHandler=close_cdata_section_handler
		self._parser.StartElementHandler=element_handler
		self._parser.EndElementHandler=close_element_handler

	def handle_complex_element(self, name, attributes, setter):
		for attribute in attributes:
			if self._unexpected_attribute_handler: self._unexpected_attribute_handler(attribute)
			else: raise VDOM_unexpected_attribute_error(attribute)
		context=self._parser.StartElementHandler, self._parser.EndElementHandler
		chunks=[]

		def data_handler(chunk):
			chunks.append(encode_data(chunk))

		def cdata_handler(chunk):
			chunks.append(chunk)

		def cdata_section_handler():
			chunks.append("<![CDATA[")
			self._parser.CharacterDataHandler=cdata_handler

		def close_cdata_section_handler():
			chunks.append("]]>")
			self._parser.CharacterDataHandler=data_handler

		def default_handler(data):
			chunks.append(data)

		def element_handler(name, attributes):
			chunks.append("<%s"%name)
			for name, value in attributes.iteritems(): chunks.append(" %s=\"%s\""%(name, encode_data(value)))
			chunks.append(">")
			context=self._parser.EndElementHandler

			def close_element_handler(name):
				chunks.append("</%s>"%name)
				self._parser.EndElementHandler=context

			self._parser.EndElementHandler=close_element_handler

		def close_element_handler(name):
			self._parser.CharacterDataHandler=None
			self._parser.StartCdataSectionHandler=None
			self._parser.EndCdataSectionHandler=None
			self._parser.DefaultHandler=None
			self._parser.StartElementHandler, self._parser.EndElementHandler=context
			setter(u"".join(chunks))

		self._parser.CharacterDataHandler=data_handler
		self._parser.StartCdataSectionHandler=cdata_section_handler
		self._parser.EndCdataSectionHandler=close_cdata_section_handler
		self._parser.DefaultHandler=default_handler
		self._parser.StartElementHandler=element_handler
		self._parser.EndElementHandler=close_element_handler

	def handle_element(self, name, attributes, handler=None, close_handler=None):
		for attribute in attributes:
			if self._unexpected_attribute_handler: self._unexpected_attribute_handler(attribute)
			else: raise VDOM_unexpected_attribute_error(attribute)
		context=self._parser.StartElementHandler, self._parser.EndElementHandler

		def element_handler(name, attributes):
			if self._unexpected_element_handler: self._unexpected_element_handler(name)
			else: raise VDOM_unexpected_element_error(attribute)
			context=self._parser.StartElementHandler, self._parser.EndElementHandler

			def element_handler(name, attributes):
				context=self._parser.EndElementHandler

				def close_element_handler(name):
					self._parser.EndElementHandler=context

				self._parser.EndElementHandler=close_element_handler

			def close_element_handler(name):
				self._parser.StartElementHandler, self._parser.EndElementHandler=context

			self._parser.StartElementHandler=element_handler
			self._parser.EndElementHandler=close_element_handler

		def close_element_handler(name):
			self._parser.StartElementHandler, self._parser.EndElementHandler=context
			if close_handler: close_handler(name)

		self._parser.StartElementHandler=handler or element_handler
		self._parser.EndElementHandler=close_element_handler

	def handle_unknown_element(self, name, attributes, close_handler=None):
		if self._unexpected_element_handler: self._unexpected_element_handler(name)
		else: raise VDOM_unexpected_element_error(name)
		context=self._parser.StartElementHandler, self._parser.EndElementHandler

		def element_handler(name, attributes):
			context=self._parser.EndElementHandler

			def close_element_handler(name):
				self._parser.EndElementHandler=context

			self._parser.EndElementHandler=close_element_handler

		def close_element_handler(name):
			if close_handler: close_handler(name)
			self._parser.StartElementHandler, self._parser.EndElementHandler=context

		self._parser.StartElementHandler=element_handler
		self._parser.EndElementHandler=close_element_handler
