
import sys, traceback, os.path, re
from copy import copy, deepcopy
import managers
from utils.mutex import VDOM_named_mutex_auto as auto_mutex
from . import errors, lexemes, syntax
from .variables import variant
from .essentials import exitloop
from .prepare import lexer, parser
from .wrappers import v_vdomobject,	v_server, v_request, v_response, v_session


vscript_source_string=u"<vscript>"
vscript_wrappers_name="wrappers"

vscript_default_code=compile(u"", vscript_source_string, u"exec")
vscript_default_source=[]
vscript_default_environment={u"v_this": None,
	u"v_server": None, u"v_request": None, u"v_response": None, u"v_session": None,
	"v_vdomdbconnection": vscript_wrappers_name, "v_vdomdbrecordset": vscript_wrappers_name,
	"v_vdomimaging": vscript_wrappers_name, "v_vdombox": vscript_wrappers_name,
	"v_wholeconnection": vscript_wrappers_name, "v_wholeapplication": vscript_wrappers_name,
	"v_wholeerror": vscript_wrappers_name, "v_wholeconnectionerror": vscript_wrappers_name,
	"v_wholenoconnectionerror": vscript_wrappers_name,
	"v_wholeremotecallerror": vscript_wrappers_name, "v_wholeincorrectresponse": vscript_wrappers_name,
	"v_wholenoapierror": vscript_wrappers_name, "v_wholenoapplication": vscript_wrappers_name}


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
	error.source=error_type
	debug(error, console=True)
	del exclass, exexception, extraceback, history
	#managers.log_manager.error_bug(error, "vscript")

def vcompile(script, filename=None, bytecode=1, package=None, lines=None, environment=None): # CHECK: def vcompile(script, bytecode=1, package=None, lines=None):
	debug("[VScript] Wait for mutex...")
	mutex=auto_mutex("vscript_engine_compile_mutex")
	debug("[VScript] Done")
	source=None
	try:
		print "- - - - - - - - - - - - - - - - - - - -"
		for line, statement in enumerate(script.split("\n")):
			print (u"  %s      %s"%(unicode(line+1).ljust(4), statement.expandtabs(4))).encode("utf-8")
		lexer.lineno=1
		try:
			parser.package=package
			parser.environment=vscript_default_environment if environment is None else environment
			source=parser.parse(script, lexer=lexer, debug=0, tracking=0).compose(0)
		finally:
			parser.package=None
			parser.environment=None
		if lines: source[0:0]=((None, 0, line) for line in lines)
		print "- - - - - - - - - - - - - - - - - - - -"
		for line, data in enumerate(source):
			print (u"  %s %s %s%s"%(unicode(line+1).ljust(4),
				unicode("" if data[0] is None else data[0]).ljust(4),
				"    "*data[1], data[2].expandtabs(4))).encode("utf-8")
		print "- - - - - - - - - - - - - - - - - - - -"
		code=u"\n".join([u"%s%s"%(u"\t"*ident, string) for line, ident, string in source])
		if bytecode:
			code=compile(code, filename or vscript_source_string, u"exec") # CHECK: code=compile(code, vscript_source_string, u"exec")
		return code, source
	except errors.generic, error:
		show_exception_details(None, error, error_type=errors.generic.compilation)
		return vscript_default_code, vscript_default_source
	except errors.python, error:
		show_exception_details(source, errors.system_error(unicode(error)),
			error_type=errors.generic.compilation)
		raise
	finally:
		del mutex

def vexecute(code, source, object=None, namespace=None, environment=None):
	try:
		try:
			if namespace is None: namespace={}
			if environment is None:
				namespace[u"v_this"]=v_vdomobject(object) if object else v_nothing
				namespace[u"v_server"]=v_server
				namespace[u"v_request"]=v_request
				namespace[u"v_response"]=v_response
				namespace[u"v_session"]=v_session
			else:
				namespace.update(environment)
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
		show_exception_details(source, errors.system_error(unicode(error)))
		raise
