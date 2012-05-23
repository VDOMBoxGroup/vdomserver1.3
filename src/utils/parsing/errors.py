
class VDOM_parsing_exception(Exception):

	def __init__(self, message):
		super(VDOM_parsing_exception, self).__init__(message)
		self.lineno=None
		self.offset=None

class VDOM_out_of_memory_error(VDOM_parsing_exception):

	def __init__(self):
		super(VDOM_out_of_memory_error, self).__init__(u"Out of memory")

class VDOM_junk_after_document_error(VDOM_parsing_exception):

	def __init__(self):
		super(VDOM_junk_after_document_error, self).__init__(u"Junk after document")

class VDOM_missing_arguments_error(VDOM_parsing_exception):

	def __init__(self):
		super(VDOM_missing_arguments_error, self).__init__(u"Missing arguments")

class VDOM_section_must_precede_error(VDOM_parsing_exception):

	def __init__(self, name):
		super(VDOM_section_must_precede_error, self).__init__(u"%s section must precede"%name)

class VDOM_missing_section_error(VDOM_parsing_exception):

	def __init__(self, name):
		super(VDOM_missing_section_error, self).__init__(u"Missing %s section"%name)

class VDOM_unexpected_element_error(VDOM_parsing_exception):

	ignore="Ignore %s element"

	def __init__(self, name):
		super(VDOM_unexpected_element_error, self).__init__(u"Unexpected %s element"%name)

class VDOM_unexpected_attribute_error(VDOM_parsing_exception):

	ignore="Ignore %s attribute"

	def __init__(self, name):
		super(VDOM_unexpected_attribute_error, self).__init__(u"Unexpected %s atribute"%name)

class VDOM_unexpected_element_value_error(VDOM_parsing_exception):

	ignore="Ignore %s element value"

	def __init__(self, name):
		super(VDOM_unexpected_element_value_error, self).__init__(u"Unexpected %s element value or contents"%name)

class VDOM_unexpected_attribute_value_error(VDOM_parsing_exception):

	ignore="Ignore %s attribute value"

	def __init__(self, name):
		super(VDOM_unexpected_attribute_value_error, self).__init__(u"Unexpected %s attribute value"%name)

class VDOM_incorrect_element_value_error(VDOM_parsing_exception):

	def __init__(self, name):
		super(VDOM_incorrect_element_value_error, self).__init__(u"Incorrect %s element value or contents"%name)

class VDOM_incorrect_attribute_value_error(VDOM_parsing_exception):

	def __init__(self, name):
		super(VDOM_incorrect_attribute_value_error, self).__init__(u"Incorrect %s attribute value"%name)

class VDOM_missing_element_error(VDOM_parsing_exception):

	def __init__(self, name):
		super(VDOM_missing_element_error, self).__init__(u"Missing %s element"%name)

class VDOM_missing_attribute_error(VDOM_parsing_exception):

	def __init__(self, name):
		super(VDOM_missing_attribute_error, self).__init__(u"Missing %s atribute"%name)
