
python=Exception



class generic(python):

	compilation=u"compilation"
	runtime=u"runtime"
	
	def __init__(self, message=u"Unknown error", line=None):
		self.type=generic.compilation
		self.message=message
		self.line=line

	def __str__(self):
		return u"VScript %s error%s: %s"%(self.type,
			u"" if self.line is None else u" (line %s)"%self.line, self.message)

class internal_error(generic):

	def __init__(self, message, line=None):
		generic.__init__(self,
			message=u"Internal error: %s"%message,
			line=line)

class system_error(generic):

	def __init__(self, message, line=None):
		generic.__init__(self,
			message=u"System error: %s"%message,
			line=line)

class invalid_character(generic):

	def __init__(self, character, line=None):
		generic.__init__(self,
			message=u"Invalid character: '%s'"%character,
			line=line)

class syntax_error(generic):

	def __init__(self, token, line=None):
		generic.__init__(self,
			message=u"Syntax error: '%s'"%token,
			line=line)

class expected_statement(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Expected statement",
			line=line)

class class_have_multiple_default(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Cannot have multiple default property/method in a Class",
			line=line)

class property_have_no_arguments(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Property set or let must have at least one argument",
			line=line)

class use_parentheses_when_calling_sub(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Cannot use parentheses when calling a Sub",
			line=line)
		
class constructor_or_destructor_have_arguments(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Class initialize or terminate do not have arguments",
			line=line)

class default_not_a_property_get(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"'Default' specification can only be on Property Get",
			line=line)

class default_not_a_public(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"'Default' specification must also specify 'Public'",
			line=line)

class expected_something(generic):

	def __init__(self, name, line=None):
		generic.__init__(self,
			message=u"Expected '%s'"%name,
			line=line)

class inconsistent_arguments_number(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Number of arguments must be consistent across properties specification",
			line=line)

class invalid_exit_statement(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message="Invalid 'Exit' statement",
			line=line)

class not_implemented(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message="Not implemented",
			line=line)

class variable_is_undefined(generic):

	def __init__(self, name=None, line=None):
		details=(u": '%s'"%(name[2:] if name.startswith(u"v_") else name) if name else u"")
		generic.__init__(self,
			message=u"Variable is undefined%s"%details,
			line=line)

class name_redefined(generic):

	def __init__(self, name=None, line=None):
		details=(u": '%s'"%(name[2:] if name.startswith(u"v_") else name) if name else u"")
		generic.__init__(self,
			message=u"Name redefined%s"%details,
			line=line)

class division_by_zero(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Division by zero",
			line=line)

class overflow(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Overflow",
			line=line)

class object_has_no_property(generic):
	
	def __init__(self, name=None, line=None):
		details=(u": '%s'"%(name[2:] if name.startswith(u"v_") else name) if name else u"")
		generic.__init__(self,
			message=u"Object doesn't support this property or method%s"%details,
			line=line)

class subscript_out_of_range(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Subscript out of range",
			line=line)

class type_mismatch(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Type mismatch",
			line=line)

class object_required(generic):

	def __init__(self, name=None, line=None):
		details=(u": '%s'"%(name[2:] if name.startswith(u"v_") else name) if name and name!="__call__" else u"")
		generic.__init__(self,
			message=u"Object required%s"%details,
			line=line)

class static_array(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"This array is fixed or temporarily locked",
			line=line)

class illegal_assigment(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Illegal assignment",
			line=line)

class illegal_attribute_name(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"Illegal attribute name",
			line=line)

class wrong_number_of_arguments(generic):

	def __init__(self, name=None, line=None):
		details=(u": '%s'"%(name[2:] if name.startswith(u"v_") else name) if name and name!="__call__" else u"")
		generic.__init__(self,
			message=u"Wrong number of arguments or invalid property assignment%s"%details,
			line=line)

class invalid_procedure_call(generic):

	def __init__(self, name=None, line=None):
		details=(u": '%s'"%(name[2:] if name.startswith(u"v_") else name) if name else u"")
		generic.__init__(self,
			message=u"Invalid procedure call or argument%s"%details,
			line=line)

class multiple_inherits(generic):

	def __init__(self, line=None):
		generic.__init__(self,
			message=u"'Inherits' can appear only once within a 'Class' statement and can only specify one class",
			line=line)
