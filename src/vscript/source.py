
from copy import copy, deepcopy

import errors, lexemes, library, exceptions



__all__=[u"vname", u"vmybase", u"vmy", u"vmyclass", u"vnames",
	u"vexpression", u"vexpressions",
	u"vsubscripts", u"varguments", u"vstatements", u"vdeclarations", u"vredim",
	u"verase", u"vlet", u"vset", u"vuse", u"vpython", u"vconstant", u"vcall",
	u"velseif", u"velseifs", u"vifthen", u"vifthenelse",
	u"vselectcase", u"vselectcases", u"vselect", u"vselectelse",
	u"vdoloop", u"vdowhileloop", u"vdountilloop", u"vdoloopwhile", u"vdoloopuntil",
	u"vforeach", u"vfor", u"vforstep",
	u"vtrycatch", u"vtrycatches", u"vtry", u"vtryfinally",
	u"vwith", u"vexitfunction", u"vexitsub", u"vexitproperty", u"vexitdo", u"vexitfor",
	u"vrandomize", u"vprint", u"vtouch", u"vglobals",
	u"vfunction", u"vsub", u"vpropertyget", u"vpropertylet", u"vpropertyset",
	u"vinherits", u"vclass", u"vsource"]



NOT_AN_ARGUMENT="NOT AN ARGUMENT"



no_explicit=1 # try to emulate OPTION EXPLICIT OFF behaviour

absent="ABSENT"

vscript_constructor=u"%sclass_initialize"%lexemes.prefix
vscript_destructor=u"%sclass_terminate"%lexemes.prefix

python_default=u"__call__"
python_constructor=u"__init__"
python_destructor=u"__del__"
python_result="result"



class vnamemanager(object):

	def get_names(self):
		return {}

	names=property(get_names)

class vgenericnamemanager(vnamemanager):

	def __init__(self, names):
		self._names=names

	def get_names(self):
		return self._names

	names=property(get_names)

class vinitialnamemanager(vnamemanager):

	def __init__(self, names):
		self._names=names

	def import_names(self, module_name, alias=NOT_AN_ARGUMENT):
		if alias==NOT_AN_ARGUMENT:
			alias=module_name
		module=__import__("src.vscript.%s"%module_name).__dict__["vscript"].__dict__[module_name]
		for name in dir(module):
			if name.startswith(lexemes.prefix):
				self._names[name]=alias

	def get_names(self):
		global namemanager
		self.import_names("exceptions", alias=None)
		self.import_names("library", alias=None)
		self.import_names("extensions")
		self.import_names("wrappers")
		namemanager=vgenericnamemanager(self._names)
		return self._names
		
	names=property(get_names)

namemanager=vinitialnamemanager({u"v_this": None, u"v_server": None,
	u"v_request": None, u"v_response": None, u"v_session": None})



class vself(object):

	def __init__(self, line=None):
		pass

	def scope_names(self, mysource, myclass, myprocedure):
		pass

	def __unicode__(self):
		return u"self"

class vname(object):

	def __init__(self, base, line=None):
		self.line=line
		self.base=base
		self.string=u"%s"
		self.values=()
		self.check=1

	def join(self, value):
		if isinstance(value, (vexpression, vexpressions)):
			self.string+=u"(%s)"
			self.values+=(value, )
			self.check=0
		else:
			if self.check:
				self.string=u"check(%s)"%self.string
			self.string=u"%s.%s"%(self.string, value)
			self.check=1
		return self

	def let(self, value):
		if not self.values:
			self.join(vexpressions())
		self.values[-1].let(value)
		return self

	def set(self, value):
		if not self.values:
			self.join(vexpressions())
		self.values[-1].set(value)
		return self

	def scope_names(self, mysource, myclass, myprocedure):
		if self.base is None:
			if not mysource.withs:
				raise errors.syntax_error("Invalid or unqualified reference", line=self.line)
			self.member=0
			self.base=mysource.withs[-1]
		elif self.base in mysource.trys:
			self.member=0
		elif myprocedure and self.base in myprocedure.names:
			self.member=0
			if self.base==myprocedure.name:
				if self.values:
					if myclass and myclass.check_name_deeply(self.base):
						self.member=1
				else:
					self.base=python_result
		elif myclass and myclass.check_name_deeply(self.base): # self.base in myclass.names
			self.member=1
		elif self.base in mysource.names:
			self.member=0
			if myprocedure:
				myprocedure.globals.append(self.base)
		elif self.base in mysource.using:
			self.member=0
			if self.base not in mysource.using[self.base].import_names:
				mysource.using[self.base].import_names.append(self.base)
		elif myprocedure and no_explicit:
			self.member=0
			myprocedure.names[self.base]="variant()"
		elif no_explicit:
			self.member=0
			mysource.names[self.base]="variant()"
		else:
			raise errors.variable_is_undefined(self.base, line=self.line)

		for expressions in self.values:
			expressions.scope_names(mysource, myclass, myprocedure)

	def __unicode__(self):
		result=self.string%((u"self.%s"%self.base if self.member else self.base, )+self.values)
		return u"check(%s)"%result if self.check else result

class vnames(list):
	
	def __init__(self, line=None):
		self.line=line

	def join(self, name):
		self.append(name)
		return self

	def __unicode__(self):
		return u", ".join([name for name in self])

class vmy(vname):

	def __init__(self, line=None):
		vname.__init__(self, None, line=line)
		self.expression=None
		self.check=0

	def join(self, value):
		if isinstance(value, vexpressions) and self.expression is None:
			self.expressions=value.classify()
		return vname.join(self, value)

	def scope_names(self, mysource, myclass, myprocedure):
		if myclass is None:
			raise error.object_required(name="my", line=self.line)
		self.member=0
		self.base="self"

		for expressions in self.values:
			expressions.scope_names(mysource, myclass, myprocedure)

class vmybase(vname):

	def __init__(self, line=None):
		vname.__init__(self, None, line=line)
		self.expression=None
		self.check=0

	def join(self, value):
		if isinstance(value, vexpressions) and self.expression is None:
			self.expressions=value.classify()
		return vname.join(self, value)

	def scope_names(self, mysource, myclass, myprocedure):
		if myclass is None:
			raise error.object_required(name="mybase", line=self.line)
		self.member=0
		self.base=myclass.inherits

		for expressions in self.values:
			expressions.scope_names(mysource, myclass, myprocedure)

class vmyclass(vname):

	def __init__(self, line=None):
		vname.__init__(self, None, line=line)
		self.expression=None
		self.check=0

	def join(self, value):
		if isinstance(value, vexpressions) and self.expression is None:
			self.expressions=value.classify()
		return vname.join(self, value)

	def scope_names(self, mysource, myclass, myprocedure):
		if myclass is None:
			raise error.object_required(name="myclass", line=self.line)
		self.member=0
		self.base=myclass.name

		for expressions in self.values:
			expressions.scope_names(mysource, myclass, myprocedure)

class vexpression(object):

	def __init__(self, string, values=None, line=None):
		self.line=line
		self.string=string
		self.values=values or ()

	def join(self, string, value):
		if isinstance(value, vexpression):
			self.string=string%(self.string, value.string)
			self.values+=value.values
		else:
			self.string=string%(self.string, " ,".join(["%s"]*len(value)))
			self.values+=tuple(value)
		return self

	def apply(self, string):
		self.string=string%self.string
		return self
		
	def scope_names(self, mysource, myclass, myprocedure):
		for value in self.values:
			value.scope_names(mysource, myclass, myprocedure)

	def __unicode__(self):
		return self.string%self.values

class vexpressions(list):

	def __init__(self, line=None):
		self.line=line

	def join(self, expression):
		self.append(expression)
		return self

	def let(self, value):
		self.append(value.apply(u"let=%s"))
		return self

	def set(self, value):
		self.append(value.apply(u"set=%s"))
		return self

	def classify(self):
		self.insert(0, vself())
		return self

	def scope_names(self, mysource, myclass, myprocedure):
		for expression in self:
			expression.scope_names(mysource, myclass, myprocedure)

	def __unicode__(self):
		return u", ".join(map(unicode, self))

class vsubscripts(list):

	def __init__(self):
		pass

	def join(self, dimension):
		self.append(dimension)
		return self

	def scope_names(self, mysource, myclass, myprocedure):
		pass

	def __unicode__(self):
		return u"[%s]"%u", ".join(map(unicode, self))

class varguments(list):

	def __init__(self):
		pass

	def join(self, argument):
		self.append(argument)
		return self

	initialization=property(lambda self: u"=".join(filter(None,
		[u", ".join([name for name, type in self if type]),
		u", ".join([u"%s(%s)"%(type, name) for name, type in self if type])])))

	def __unicode__(self):
		return u", ".join([argument[0] for argument in self])

class vstatements(list):

	def __init__(self):
		pass

	def join(self, statement):
		if statement:
			self.append(statement)
		return self

	def collect_names(self, names):
		for statement in self:
			statement.collect_names(names)

	def scope_names(self, mysource, myclass, myprocedure):
		for statement in self:
			statement.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident, precede=None, follow=None):
		contents=[]
		if precede:
			contents.extend(precede)
		for statement in self:
			contents.extend(statement.compose(ident))
		if follow:
			contents.extend(follow)
		contents=[line for line in contents if line[2]]
		return contents if contents else [(None, ident, u"pass")]

class vstatement(object):

	def __init__(self, line=None):
		self.line=line

	def collect_names(self, names):
		pass

	def scope_names(self, mysource, myclass, myprocedure):
		pass

	def compose(self, ident):
		return tuple()

class vdeclarations(dict, vstatement):
	
	def __init__(self, line=None):
		vstatement.__init__(self, line)

	def join(self, name, value):
		if name in self:
			raise errors.name_redefined(name, line=self.line)
		self[name]=value
		return self

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		conflicts=set(self).intersection(names)
		if conflicts:
			raise errors.name_redefined(name=conflicts.pop(), line=self.line)
		names.update(self)

class vredim(list, vstatement):
	
	def __init__(self, preserve=False, line=None):
		vstatement.__init__(self, line)
		self.preserve=preserve

	def join(self, name, value):
		self.append((name, value))
		return self

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		for name, value in self:
			name.scope_names(mysource, myclass, myprocedure)
			value.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		preserve=", preserve=True" if self.preserve else ""
		return [(self.line, ident, u"redim(%s, [%s]%s)"%\
			(name, value, preserve)) for name, value in self]

class verase(vstatement):
	
	def __init__(self, name, line=None):
		vstatement.__init__(self, line)
		self.name=name

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.name.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		return ((self.line, ident, u"erase(%s)"%self.name),)

class vlet(vstatement):

	def __init__(self, name, value, line=None):
		vstatement.__init__(self, line)
		self.name=name
		self.name.check=0
		self.value=value

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.name.scope_names(mysource, myclass, myprocedure)
		self.value.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		return ((self.line, ident, u"%s(let=%s)"%(self.name, self.value)),)

class vset(vstatement):

	def __init__(self, name, value, line=None):
		vstatement.__init__(self, line)
		self.name=name
		self.name.check=0
		self.value=value

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.name.scope_names(mysource, myclass, myprocedure)
		self.value.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		return ((self.line, ident, u"%s(set=%s)"%(self.name, self.value)),)

class vuse(vstatement):

	def __init__(self, name, line, package=None):
		vstatement.__init__(self, line)
		self.name=name[2:]
		self.package=package
		self.module=__import__("%s.%s"%(self.package, self.name)).__dict__[self.name] \
			if package else __import__(self.name)
		self.names=[]
		default_names=namemanager.names
		for name in dir(self.module):
			if name.startswith(lexemes.prefix) and name not in default_names:
				self.names.append(name)

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		mysource.uses.append(self)
		for name in self.names:
			mysource.using[name]=self
		self.import_names=[]

	def compose(self, ident):
		return ((self.line, ident, u"from %s import %s"%(self.name, ", ".join(self.import_names))),) \
			if self.import_names else ()

class vpython(vstatement):

	def __init__(self, source, line=None):
		vstatement.__init__(self, line)
		self.source=source

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)

	def compose(self, ident):
		string=self.source
		return ((self.line, ident, string),)

class vconstant(vstatement):

	def __init__(self, name, value, line=None):
		vstatement.__init__(self, line)
		self.name=name
		self.name.check=0
		self.value=value

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		if self.name.base in names:
			raise errors.name_redefined(self.name.base, line=self.line)
		names[self.name.base]=None

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.name.scope_names(mysource, myclass, myprocedure)
		self.value.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		return ((self.line, ident, u"%s=constant(value=%s)"%(self.name, self.value)),)

class vcall(vstatement):

	def __init__(self, expression, line=None):
		vstatement.__init__(self, line)
		self.expression=expression

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.expression.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		return ((self.line, ident, u"%s"%self.expression),)

class velseif(vstatement):

	def __init__(self, condition, statements, line=None):
		vstatement.__init__(self, line)
		self.condition=condition
		self.statements=statements

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		self.statements.collect_names(names)

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.condition.scope_names(mysource, myclass, myprocedure)
		self.statements.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		contents=[(self.line, ident, u"elif bool(%s):"%self.condition)]
		contents.extend(self.statements.compose(ident+1))
		return contents

class velseifs(list):

	def __init__(self):
		pass

	def join(self, elseif):
		self.append(elseif)
		return self

	def collect_names(self, names):
		for elseif in self:
			elseif.collect_names(names)

	def scope_names(self, mysource, myclass, myprocedure):
		for elseif in self:
			elseif.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		contents=[]
		for elseif in self:
			contents.extend(elseif.compose(ident))
		return contents

class vifthen(vstatement):

	def __init__(self, condition, statements, elseifs=None, line=None):
		vstatement.__init__(self, line)
		self.condition=condition
		self.statements=statements
		self.elseifs=elseifs

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		self.statements.collect_names(names)

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.condition.scope_names(mysource, myclass, myprocedure)
		self.statements.scope_names(mysource, myclass, myprocedure)
		if self.elseifs:
			self.elseifs.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		contents=[(self.line, ident, u"if bool(%s):"%self.condition)]
		contents.extend(self.statements.compose(ident+1))
		if self.elseifs:
			contents.extend(self.elseifs.compose(ident))
		return contents

class vifthenelse(vifthen):

	def __init__(self, condition, statements, else_statements, elseifs=None, line=None):
		vifthen.__init__(self, condition, statements, elseifs=elseifs, line=line)
		self.else_statements=else_statements

	def collect_names(self, names):
		vifthen.collect_names(self, names)
		self.else_statements.collect_names(names)

	def scope_names(self, mysource, myclass, myprocedure):
		vifthen.scope_names(self, mysource, myclass, myprocedure)
		self.else_statements.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		contents=vifthen.compose(self, ident)
		contents.append((self.line, ident, u"else:"))
		contents.extend(self.else_statements.compose(ident+1))
		return contents

class vselectcase(vstatement):

	def __init__(self, expressions, statements, line=None):
		vstatement.__init__(self, line)
		self.expressions=expressions
		self.statements=statements

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		self.statements.collect_names(names)

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.expressions.scope_names(mysource, myclass, myprocedure)
		self.statements.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident, compare, index):
		contents=[]
		conditions=u" or ".join([u"bool(%s==%s)"%(compare, expression) for expression in self.expressions])
		contents.append((self.line, ident, u"%s %s:"%(u"elif" if index else u"if", conditions)))
		contents.extend(self.statements.compose(ident+1))
		return contents

class vselectcases(list):

	def __init__(self):
		pass

	def join(self, case):
		self.append(case)
		return self

	def collect_names(self, names):
		for case in self:
			case.collect_names(names)

	def scope_names(self, mysource, myclass, myprocedure):
		for case in self:
			case.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident, compare):
		contents=[]
		for index, case in enumerate(self):
			contents.extend(case.compose(ident, compare, index))
		return contents

class vselect(vstatement):
	
	def __init__(self, expression, cases, line=None):
		vstatement.__init__(self, line)
		self.expression=expression
		self.cases=cases

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		self.cases.collect_names(names)

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.expression.scope_names(mysource, myclass, myprocedure)
		self.cases.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		contents=[]
		contents.extend(self.cases.compose(ident, self.expression))
		return contents

class vselectelse(vselect):

	def __init__(self, expression, cases, else_statements, line=None):
		vselect.__init__(self, expression, cases, line)
		self.else_statements=else_statements

	def collect_names(self, names):
		vselect.collect_names(self, names)
		self.else_statements.collect_names(names)

	def scope_names(self, mysource, myclass, myprocedure):
		vselect.scope_names(self, mysource, myclass, myprocedure)
		self.else_statements.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		contents=vselect.compose(self, ident)
		contents.append((self.line, ident, u"else:"))
		contents.extend(self.else_statements.compose(ident+1))
		return contents

class vdoloop(vstatement):

	def __init__(self, statements, line=None):
		vstatement.__init__(self, line)
		self.statements=statements

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		self.statements.collect_names(names)

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.statements.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident, condition=None, follow=None):
		contents=[(self.line, ident, u"while %s:"%(condition or u"1")), (self.line, ident+1, u"try:")]
		contents.extend(self.statements.compose(ident+2, follow=follow))
		contents.append((self.line, ident+1, u"except exitdo:"))
		contents.append((self.line, ident+2, u"break"))
		return contents

class vdoconditionalloop(vdoloop):

	def __init__(self, condition, statements, line=None):
		vdoloop.__init__(self, statements, line)
		self.condition=condition

	def scope_names(self, mysource, myclass, myprocedure):
		vdoloop.scope_names(self, mysource, myclass, myprocedure)
		self.condition.scope_names(mysource, myclass, myprocedure)

class vdowhileloop(vdoconditionalloop):
	
	def compose(self, ident):
		return vdoconditionalloop.compose(self, ident,
			condition=u"bool(%s)"%self.condition)

class vdountilloop(vdoconditionalloop):
	
	def compose(self, ident):
		return vdoconditionalloop.compose(self, ident,
			condition=u"not bool(%s)"%self.condition)

class vdoloopwhile(vdoconditionalloop):
	
	def compose(self, ident):
		return vdoconditionalloop.compose(self, ident,
			follow=[(self.condition.line, ident+2, u"if not bool(%s):"%self.condition),
			(self.condition.line, ident+3, u"break")])

class vdoloopuntil(vdoconditionalloop):

	def compose(self, ident):
		return vdoconditionalloop.compose(self, ident,
			follow=[(self.condition.line, ident+2, u"if bool(%s):"%self.condition),
			(self.condition.line, ident+3, u"break")])

class vforeach(vstatement):
	
	def __init__(self, variable, collection, statements, line=None):
		vstatement.__init__(self, line)
		self.variable=variable
		self.variable.check=0
		self.collection=collection
		self.statements=statements

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.variable.scope_names(mysource, myclass, myprocedure)
		self.collection.scope_names(mysource, myclass, myprocedure)
		self.statements.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		contents=[(self.line, ident, u"for %s in %s:"%(self.variable, self.collection)),
			(self.line, ident+1, u"try:")]
		contents.extend(self.statements.compose(ident+2))
		contents.append((self.line, ident+1, u"except exitfor:"))
		contents.append((self.line, ident+2, u"break"))
		contents.append((self.line, ident+1, u"finally:"))
		contents.append((self.line, ident+2, u"%s=variant()"%self.variable))
		return contents

class vfor(vstatement):
	
	def __init__(self, variable, range, statements, line=None):
		vstatement.__init__(self, line)
		self.variable=variable
		self.variable.check=0
		self.range=range
		self.statements=statements

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.variable.scope_names(mysource, myclass, myprocedure)
		self.range[0].scope_names(mysource, myclass, myprocedure)
		self.range[1].scope_names(mysource, myclass, myprocedure)
		self.statements.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident, step=None):
		contents=[(self.line, ident, u"%s(let=%s)"%(self.variable, self.range[0])),
			(self.line, ident, u"while bool(%s<=%s):"%(self.variable, self.range[1])),
			(self.line, ident+1, u"try:")]
		contents.extend(self.statements.compose(ident+2,
			follow=[(self.line, ident+2, u"%s(let=%s+integer(%s))"%(self.variable, self.variable, step or u"1"))]))
		contents.append((self.line, ident+1, u"except exitfor:"))
		contents.append((self.line, ident+2, u"break"))
		return contents

class vforstep(vfor):
	
	def __init__(self, variable, range, step, statements, line=None):
		vfor.__init__(self, variable, range, statements, line)
		self.step=step

	def scope_names(self, mysource, myclass, myprocedure):
		vfor.scope_names(self, mysource, myclass, myprocedure)
		self.step.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		return vfor.compose(ident, step=self.step)

class vtrycatch(vstatement):

	def __init__(self, statements, exceptions=None, name=None, line=None):
		vstatement.__init__(self, line)
		self.exceptions=exceptions
		self.name=name
		self.statements=statements

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		self.statements.collect_names(names)
	
	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		mysource.trys.enter(self.name)
		self.statements.scope_names(mysource, myclass, myprocedure)
		mysource.trys.leave()

	def compose(self, ident):
		contents=[(self.line, ident, u"except%s%s:"%\
			(" (%s)"%unicode(self.exceptions) if self.exceptions else "",
			", %s"%self.name if self.name else ""))]
		contents.extend(self.statements.compose(ident+1,
			precede=[(self.line, ident+1, u"%s=error(%s)"%(self.name, self.name))] if self.name else None))
		return contents

class vtrycatches(list):
	
	def __init__(self):
		pass

	def join(self, value):
		self.append(value)
		return self

	def collect_names(self, names):
		for value in self:
			value.collect_names(names)
	
	def scope_names(self, mysource, myclass, myprocedure):
		for value in self:
			value.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		contents=[]
		for value in self:
			contents.extend(value.compose(ident))
		return contents

class vtry(vstatement):
	
	def __init__(self, statements, excepts, line=None):
		vstatement.__init__(self, line)
		self.statements=statements
		self.excepts=excepts

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		self.excepts.collect_names(names)
	
	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.statements.scope_names(mysource, myclass, myprocedure)
		self.excepts.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident, complete=1):
		contents=[(self.line, ident, u"try:")]
		contents.extend(self.statements.compose(ident+1))
		if self.excepts:
			contents.extend(self.excepts.compose(ident))
		elif complete:
			contents.append((self.line, ident, u"finally:"))
			contents.append((self.line, ident+1, u"pass"))
		return contents

class vtryfinally(vtry):
	
	def __init__(self, statements, excepts, finally_statements, line=None, finally_line=None):
		vtry.__init__(self, statements, excepts, line)
		self.finally_statements=finally_statements
		self.finally_line=finally_line

	def collect_names(self, names):
		vtry.collect_names(self, names)
		self.finally_statements.collect_names(names)
	
	def scope_names(self, mysource, myclass, myprocedure):
		vtry.scope_names(self, mysource, myclass, myprocedure)
		self.finally_statements.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		contents=[]
		contents.extend(vtry.compose(self, ident, complete=0))
		contents.append((self.finally_line, ident, u"finally:"))
		contents.extend(self.finally_statements.compose(ident+1))
		return contents

class vwith(vstatement):
	
	def __init__(self, name, statements, line=None):
		vstatement.__init__(self, line)
		self.name=name
		self.statements=statements

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		mysource.withs.enter(self.name)
		self.statements.scope_names(mysource, myclass, myprocedure)
		mysource.withs.leave()

	def compose(self, ident):
		contents=[]
		contents.extend(self.statements.compose(ident))
		return contents

class vexitfunction(vstatement):

	def __init__(self, line=None):
		vstatement.__init__(self, line)

	def scope_names(self, mysource, myclass, myprocedure):
		if not isinstance(myprocedure, vfunction):
			raise errors.expected_something(u"Function", line=self.line)
		self.myprocedure=myprocedure

	def compose(self, ident):
		return ((self.line, ident, u"return %s.value"%python_result),)

class vexitsub(vstatement):

	def __init__(self, line=None):
		vstatement.__init__(self, line)

	def scope_names(self, mysource, myclass, myprocedure):
		if not isinstance(myprocedure, vsub):
			raise errors.expected_something(u"Sub")

	def compose(self, ident):
		return ((self.line, ident, u"return"),)

class vexitproperty(vstatement):

	def __init__(self, line=None):
		vstatement.__init__(self, line)

	#def scope_names(self, mysource, myclass, myprocedure):
		# TODO: check for call in property
		#self.string=u"return %s.value"%myprocedure.name if isinstance(myprocedure, vpropertyget) else u"return"

	def compose(self, ident):
		#return ((self.line, ident, self.string),)
		return ((self.line, ident, u"return %s.value"%python_result),)

class vexitdo(vstatement):

	def __init__(self, line=None):
		vstatement.__init__(self, line)

	def compose(self, ident):
		return ((self.line, ident, u"raise exitdo"),)

class vexitfor(vstatement):

	def __init__(self, line=None):
		vstatement.__init__(self, line)

	def compose(self, ident):
		return ((self.line, ident, u"raise exitfor"),)

class vrandomize(vstatement):

	def __init__(self, seed=None, line=None):
		vstatement.__init__(self, line)
		self.seed=seed

	def compose(self, ident):
		return ((self.line, ident, u"randomize(%s)"%(self.seed or u"")),)

class vprint(vstatement):

	def __init__(self, expressions, line=None):
		vstatement.__init__(self, line)
		self.expressions=expressions

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.expressions.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		string=u"echo(%s)"%u", ".join(map(unicode, self.expressions))
		return ((self.line, ident, string),)

class vtouch(vstatement):

	def __init__(self, expressions, line=None):
		vstatement.__init__(self, line)
		self.expressions=expressions

	def scope_names(self, mysource, myclass, myprocedure):
		vstatement.scope_names(self, mysource, myclass, myprocedure)
		self.expressions.scope_names(mysource, myclass, myprocedure)

	def compose(self, ident):
		string=u"print repr(%s)"%u", ".join(map(unicode, self.expressions))
		return ((self.line, ident, string),)

class vglobals(list):
	
	def __init__(self):
		pass

	initialization=property(lambda self:(u"global %s"%u", ".join(self)) if self else u"")

class vdefinename(vstatement):
	
	def __init__(self, name, line=None):
		vstatement.__init__(self, line)
		self.name=name

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		if self.name in names:
			raise errors.name_redefined(name=name, line=self.line)
		names[self.name]=None

class vprocedure(vstatement):

	def __init__(self, name, arguments, statements, default=False, line=None):
		vstatement.__init__(self, line)
		self.name=name
		self.vname=name
		self.arguments=arguments
		self.statements=statements
		self.default=default
		self.cachenames={}
		self.statements.insert(0, vdefinename(self.name))

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		if self.default:
			if python_default in names:
				raise errors.class_have_multiple_default(line=self.line)
			names[python_default]=self
		for name, xtype in self.arguments:
			#if name in names:
			#	raise errors.name_redefined(name, line=self.line)
			self.cachenames[name]=None
		self.statements.collect_names(self.cachenames)

	def scope_names(self, mysource, myclass, myprocedure):
		self.globals=vglobals()
		self.names=deepcopy(self.cachenames)
		self.statements.scope_names(mysource, myclass, self)

	def compose(self, ident, precede=None):
		contents=[(self.line, ident, u"def %s(%s):"%(self.vname, self.arguments))]
		initialization=[(self.line, ident+1, self.arguments.initialization),
			(self.line, ident+1, self.globals.initialization)]
		if precede:
			initialization.extend(precede)
		dims=[(name, value) for name, value in self.names.iteritems() if isinstance(value, basestring)]
		initialization.extend(
			[(self.line, ident+1, u"=".join(filter(None, [u", ".join([name for name, value in dims]),
				u", ".join([value for name, value in dims])])))])
		contents.extend(self.statements.compose(ident+1, precede=initialization))
		return contents

class vfunction(vprocedure):

	def __init__(self, name, arguments, statements, default=False, line=None):
		vprocedure.__init__(self, name, arguments, statements, default, line)
		self.statements.append(vexitfunction(line=self.line))

	def collect_names(self, names):
		vprocedure.collect_names(self, names)
		if self.name in names:
			raise errors.name_redefined(self.name, line=self.line)
		names[self.name]=self

	def compose(self, ident):
		return vprocedure.compose(self, ident,
			precede=[(self.line, ident+1, u"%s=variant()"%python_result)])

class vsub(vprocedure):

	def __init__(self, name, arguments, statements, default=False, line=None):
		vprocedure.__init__(self, name, arguments, statements, default, line)

	def collect_names(self, names):
		vprocedure.collect_names(self, names)
		if self.name in names:
			raise errors.name_redefined(self.name, line=self.line)
		names[self.name]=self

	def compose(self, ident):
		return vprocedure.compose(self, ident,
			precede=[(self.line, ident+1, u"%s=constant()"%python_result)]\
				if self.name not in (python_constructor, python_destructor) else None)

class vproperty(vstatement):

	def __init__(self, name, get=None, let=None, set=None, line=None):
		vstatement.__init__(self, line)
		self.name=name
		self.get=get
		self.let=let
		self.set=set

	def compose(self, ident):
		arguments=[len(self.get.arguments)+1] if self.get else []
		if self.let: arguments.append(len(self.let.arguments))
		if self.set: arguments.append(len(self.set.arguments))
		if len(arguments)>1 and sum(arguments)/3!=arguments[0]:
			raise errors.inconsistent_arguments_number(line=self.line)
		return [(self.line, ident, u"def %s(self, *arguments, **keywords):"%self.name),
			(self.line, ident+1, u"if \"let\" in keywords:"),
			(self.line, ident+2, u"return self.%s_let(let=keywords[\"let\"], *arguments)"%self.name),
			(self.line, ident+1, u"elif \"set\" in keywords:"),
			(self.line, ident+2, u"return self.%s_set(set=keywords[\"set\"], *arguments)"%self.name),
			(self.line, ident+1, u"else:"),
			(self.line, ident+2, u"return self.%s_get(*arguments)"%self.name)]

class vpropertyget(vprocedure):

	def __init__(self, name, arguments, statements, default=False, line=None):
		vprocedure.__init__(self, name, arguments, statements, default, line)
		self.vname=u"%s_get"%self.name
		self.statements.append(vexitproperty(line=self.line))

	def collect_names(self, names):
		vprocedure.collect_names(self, names)
		name=names.get(self.name, absent)
		if name is absent:
			names[self.name]=vproperty(self.name, get=self)
		else:
			if not isinstance(name, vproperty) or name.get:
				raise errors.name_redefined(self.name, line=self.line)
			name.get=self

	def compose(self, ident):
		return vprocedure.compose(self, ident,
			precede=[(self.line, ident+1, u"%s=variant()"%python_result)])

class vpropertyletset(vprocedure):

	def __init__(self, name, arguments, statements, default=False, line=None):
		vprocedure.__init__(self, name, arguments, statements, default, line)
		if len(self.arguments)<1:
			raise errors.property_have_no_arguments(line=self.line)
		self.value=self.arguments.pop()
		self.statements.insert(0, vdefinename(self.value[0]))

class vpropertylet(vpropertyletset):

	def __init__(self, name, arguments, statements, default=False, line=None):
		vpropertyletset.__init__(self, name, arguments, statements, default, line)
		self.vname=u"%s_let"%self.name
		self.arguments.join((u"let", None))

	def collect_names(self, names):
		vprocedure.collect_names(self, names)
		name=names.get(self.name, absent)
		if name is absent:
			names[self.name]=vproperty(self.name, let=self)
		else:
			if not isinstance(name, vproperty) or name.let:
				raise errors.name_redefined(self.name, line=self.line)
			name.let=self

	def compose(self, ident):
		return vprocedure.compose(self, ident,
			precede=[(self.line, ident+1, u"%s=variant()"%python_result),
				(self.line, ident+1, u"%s=%s(let)"%(self.value[0], self.value[1]))])

class vpropertyset(vpropertyletset):

	def __init__(self, name, arguments, statements, default=False, line=None):
		vpropertyletset.__init__(self, name, arguments, statements, default, line)
		self.vname=u"%s_set"%self.name
		self.arguments.join((u"set", None))

	def collect_names(self, names):
		vprocedure.collect_names(self, names)
		name=names.get(self.name, absent)
		if name is absent:
			names[self.name]=vproperty(self.name, set=self)
		else:
			if not isinstance(name, vproperty) or name.set:
				raise errors.name_redefined(self.name, line=self.line)
			name.set=self

	def compose(self, ident):
		return vprocedure.compose(self, ident,
			precede=[(self.line, ident+1, u"%s=variant()"%python_result),
				(self.line, ident+1, u"%s=%s(set)"%(self.value[0], self.value[1]))])

class vinitializations(vstatement):

	def __init__(self, owner, line=None):
		vstatement.__init__(self, line=line)
		self.owner=owner

	def compose(self, ident):
		return [(self.line, ident, u"self.%s=%s"%(name, value)) for name, value in self.owner.initializations]

class vinherits(vstatement):

	def __init__(self, name, line=None):
		vstatement.__init__(self, line=line)
		self.name=name
		self.parent=None

	def scope_names(self, mysource, myclass, myprocedure):
		if myclass is None:
			raise error.object_required(name="inherits", line=self.line)
		if myclass.inherits is not None:
			raise error.multiple_inherits(line=self.line)
		myclass.inherits=self.name
		myclass.parent=mysource.names[self.name]

class vclass(vstatement):

	def __init__(self, name, statements, line=None):
		vstatement.__init__(self, line)
		self.name=name
		self.statements=statements
		self.inherits=None
		self.parent=None

	def collect_names(self, names):
		vstatement.collect_names(self, names)
		if self.name in names:
			raise errors.name_redefined(self.name, line=self.line)
		names[self.name]=self
		self.names={}
		self.statements.collect_names(self.names)
		self.default=self.names.get(python_default, None)
		self.constructor=self.names.get(vscript_constructor, None)
		self.destructor=self.names.get(vscript_destructor, None)
		for value in self.names.itervalues():
			if isinstance(value, vproperty):
				self.statements.append(value)
		if self.default:
			self.statements.insert(0, vsub(python_default, deepcopy(self.default.arguments),
				vstatements().join(vcall(vexpression(u"return self.%s(%s)"%(self.default.name,
				self.default.arguments), line=self.line), line=self.line)), line=self.line))
		if self.destructor:
			if not isinstance(self.destructor, vsub):
				raise errors.expected_something(u"sub")
			if self.destructor.arguments:
				raise errors.constructor_or_destructor_have_arguments
			self.statements.insert(0, vsub(python_destructor, deepcopy(self.destructor.arguments),
				vstatements().join(vcall(vexpression(u"self.%s()"%vscript_destructor, line=self.line),
				line=self.line)), line=self.line))
		self.initializations=[(name, value) for name, value in self.names.iteritems() if isinstance(value, basestring)]
		if self.constructor or self.initializations:
			statements=vstatements()
			if self.initializations:
				statements.join(vinitializations(self, line=self.line))
			if self.constructor:
				if not isinstance(self.constructor, vsub):
					raise errors.expected_something(u"Sub")
				if self.constructor.arguments:
					raise errors.constructor_or_destructor_have_arguments
				arguments=deepcopy(self.constructor.arguments)
				statements.join(vcall(vexpression(u"self.%s()"%vscript_constructor, line=self.line), line=self.line))
			else:
				arguments=varguments()
			self.statements.insert(0, vsub(python_constructor, arguments, statements, line=self.line))
		for procedure in [statement for statement in self.statements if isinstance(statement, vprocedure)]:
			procedure.arguments.insert(0, (u"self", None))

	def check_name_deeply(self, name):
		if name in self.names: return True
		if self.inherits: return self.parent.check_name_deeply(name)
		return False

	def scope_names(self, mysource, myclass, myprocedure):
		self.statements.scope_names(mysource, self, myprocedure)

	def compose(self, ident):
		contents=[(self.line, ident, u"class %s(%s):"%(self.name, self.inherits or "generic"))]
		contents.extend(self.statements.compose(ident+1))
		return contents

class vnamestack(list):

	def enter(self, name):
		self.append(name)

	def leave(self):
		self.pop()

class vsourcenames(object):

	def __init__(self):
		self.internal_names=namemanager.names
		self.names={}
		self.imports={}

	def update(self, names):
		self.names.update(names)

	def __iter__(self):
		return iter(self.names)

	def __setitem__(self, name, value):
		self.names[name]=value

	def __contains__(self, name):
		if name in self.internal_names:
			alias=self.internal_names[name]
			names=self.imports.setdefault(alias, set())
			names.add(name)
			return True
		if name in self.names:
			return True

	def compose(self, ident):
		contents=[(None, ident, u"from src.vscript.%s import %s"%(name, u", ".join(names))) \
			for name, names in self.imports.iteritems() if name is not None]
		contents.extend((None, ident, u"globals().setdefault(%s, %s)"%(repr(name), value)) \
			for name, value in self.names.iteritems() if isinstance(value, basestring))
		return contents

class vsource(object):

	def __init__(self, statements, package=None):
		self.line=0
		self.names=vsourcenames()
		self.statements=statements
		self.package=package
		self.collect_names()

	def collect_names(self):
		self.statements.collect_names(self.names)

	def scope_names(self):
		self.uses=[]
		self.using={}
		try:
			self.trys=vnamestack()
			self.withs=vnamestack()
			self.statements.scope_names(self, None, None)
		finally:
			self.trys=None
			self.withs=None

	def compose(self, ident):
		self.scope_names()
		contents=[(None, ident, u"from src.vscript import *")]
		if self.package:
			contents.insert(0, (None, 0, "__package__=\"%s\""%self.package))
		contents.extend(self.statements.compose(ident=0, precede=self.names.compose(ident)))
		return contents
