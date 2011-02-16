
import sys, traceback, os.path, re

from util.mutex import VDOM_named_mutex_auto as auto_mutex

import managers, log

import ply.lex as lex
import ply.yacc as yacc

import options, errors, types, lexemes, syntax

from array import array
from empty import empty, v_empty
from null import null, v_null
from integer import integer
from double import double, nan, infinity
from date import date
from string import string
from boolean import boolean, v_true_value, v_false_value
from generic import generic
from nothing import nothing, v_nothing
from variant import variant
from constant import constant
from shadow import shadow

from . import byref, byval, exitloop
from auxiliary import as_value, as_is, as_array, as_integer, as_double, as_string, as_boolean, as_generic, as_date

from prepare import tablepath, tablename, lexer, parser
from wrapper import vdomtypewrapper, vdomobjectwrapper
from integration import server, request, response, session



vscript_source_string=u"<vscript>"

vscript_default_code=compile(u"", vscript_source_string, u"exec")
vscript_default_source=[]



def show_exception_details(source, error, error_type=errors.generic.runtime):
	exclass, exexception, extraceback=sys.exc_info()
	history=traceback.extract_tb(extraceback)
	path_python=sys.prefix
	path_binary=os.path.split(os.path.dirname(sys.argv[0]))[0]
	vbline=error.line
	print "- - - - - - - - - - - - - - - - - - - -"
	for path, line, function, st in history:
		if path.startswith(".."):
			path=os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), path))
		if path.startswith(path_binary):
			path="<server>%s"%path[len(path_binary):]
		elif path.startswith(path_python):
			path="<python>%s"%path[len(path_python):]
		elif path==vscript_source_string:
			st=source[line-1][2]
			vbline=source[line-1][0] or None
		print (u"%s, line %s%s - %s"%(path, line, ": %s"%st if st else "", function)).encode("utf-8")
	print "- - - - - - - - - - - - - - - - - - - -"
	error.line=vbline
	error.type=error_type
	debug(error, console=True)
	del exclass, exexception, extraceback, history
	managers.log_manager.error_bug(error, "vscript")

def vsetup(skip_wrappers=None):
	if skip_wrappers is not None:
		options.skip_wrappers=skip_wrappers

def vcompile(script, bytecode=1, package=None, lines=None):
	debug("[VScript] Wait for mutex...")
	mutex=auto_mutex("vscript_engine_compile_mutex")
	debug("[VScript] Done")
	source=None
	try:
		print "- - - - - - - - - - - - - - - - - - - -"
		for line, statement in enumerate(script.split("\n")):
			print (u"  %s      %s"%(unicode(line+1).ljust(4), statement.expandtabs(4))).encode("utf-8")
		lexer.lineno, parser.package=1, package
		source=parser.parse(script, lexer=lexer, debug=0, tracking=0).compose(0)
		if lines: source[0:0]=((None, 0, line) for line in lines)
		print "- - - - - - - - - - - - - - - - - - - -"
		for line, data in enumerate(source):
			print (u"  %s %s %s%s"%(unicode(line+1).ljust(4),
				unicode("" if data[0] is None else data[0]).ljust(4),
				"    "*data[1], data[2].expandtabs(4))).encode("utf-8")
		print "- - - - - - - - - - - - - - - - - - - -"
		code=u"\n".join([u"%s%s"%(u"\t"*ident, string) for line, ident, string in source])
		if bytecode:
			code=compile(code, vscript_source_string, u"exec")
		return code, source
	except errors.generic, error:
		show_exception_details(None, error, error_type=errors.generic.compilation)
		return vscript_default_code, vscript_default_source
	except errors.python, error:
		show_exception_details(source, errors.system_error(message=unicode(error)),
			error_type=errors.generic.compilation)
		raise
	finally:
		del mutex

def vexecute(code, source, object=None, namespace=None):
	try:
		try:
			if namespace is None:
				namespace={}
			namespace[u"v_this"]=variant(vdomobjectwrapper(object) if object else v_nothing)
			namespace[u"v_server"]=server
			namespace[u"v_request"]=request
			namespace[u"v_response"]=response
			namespace[u"v_session"]=session
			exec code in namespace
		except exitloop:
			exclass, exexception, extraceback=sys.exc_info()
			del exclass, exexception
			raise errors.invalid_exit_statement, None, extraceback
		except AttributeError, error:
			exclass, exexception, extraceback=sys.exc_info()
			path, line, function, text=traceback.extract_tb(extraceback)[-1]
			if path==vscript_source_string:
				print "- - - - - - - - - - - - - - - - - - - -"
				print (u"Python (AttributeError): %s"%error.message).encode("utf-8")
				result=re.search(".+ has no attribute \'(.+)\'", unicode(error))
				if result:
					del exclass, exexception
					raise errors.object_has_no_property(name=result.group(1)), None, extraceback
				else:
					del exclass, exexception, extraceback
					raise
			else:
				del exclass, exexception, extraceback
				raise
		except ValueError, error:
			exclass, exexception, extraceback=sys.exc_info()
			path, line, function, text=traceback.extract_tb(extraceback)[-1]
			if path==vscript_source_string:
				print "- - - - - - - - - - - - - - - - - - - -"
				print (u"Python (ValueError): %s"%error).encode("utf-8")
				del exclass, exexception
				raise errors.type_mismatch, None, extraceback
			else:
				del exclass, exexception, extraceback
				raise
		except TypeError, error:
			exclass, exexception, extraceback=sys.exc_info()
			path, line, function, text=traceback.extract_tb(extraceback)[-1]
			if path==vscript_source_string:
				print "- - - - - - - - - - - - - - - - - - - -"
				print (u"Python (TypeError): %s"%error).encode("utf-8")
				result=re.search("(.+)\(\) (?:takes no arguments)|(?:takes exactly \d+ arguments) \(\d+ given\)", unicode(error))
				if result:
					del exclass, exexception
					raise errors.wrong_number_of_arguments(name=result.group(1)), None, extraceback
				else:
					del exclass, exexception
					raise errors.type_mismatch, None, extraceback
			else:
				del exclass, exexception, extraceback
				raise
	except errors.generic, error:
		show_exception_details(source, error)
		raise
	except errors.python, error:
		show_exception_details(source, errors.system_error(message=unicode(error)))
		raise
