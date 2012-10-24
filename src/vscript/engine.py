
import sys, traceback, os.path, re
from copy import copy, deepcopy
from weakref import WeakKeyDictionary
import managers
from utils.mutex import VDOM_named_mutex_auto as auto_mutex
from . import errors, lexemes, syntax
from .variables import variant
from .essentials import exitloop
from .prepare import lexer, parser
from .subtypes import v_nothing
from .wrappers import v_vdomobject,	v_server, v_request, v_response, v_session, v_application


vscript_source_string=u"<vscript>"
vscript_wrappers_name="wrappers"

vscript_default_code=compile(u"", vscript_source_string, u"exec")
vscript_default_source=[]

vscript_default_action_namespace={
	u"v_server": v_server(),
	u"v_request": v_request(),
	u"v_response": v_response(),
	u"v_session": v_session(),
	u"v_application": v_application()}
vscript_default_environment={
	u"v_this": None,
	u"v_server": None,
	u"v_request": None,
	u"v_response": None,
	u"v_session": None,
	u"v_application": None,
	u"v_vdomdbconnection": vscript_wrappers_name,
	u"v_vdomdbrecordset": vscript_wrappers_name,
	u"v_vdomimaging": vscript_wrappers_name,
	u"v_vdombox": vscript_wrappers_name,
	u"v_wholeconnection": vscript_wrappers_name,
	u"v_wholeapplication": vscript_wrappers_name,
	u"v_wholeerror": vscript_wrappers_name,
	u"v_wholeconnectionerror": vscript_wrappers_name,
	u"v_wholenoconnectionerror": vscript_wrappers_name,
	u"v_wholeremotecallerror": vscript_wrappers_name,
	u"v_wholeincorrectresponse": vscript_wrappers_name,
	u"v_wholenoapierror": vscript_wrappers_name,
	u"v_wholenoapplication": vscript_wrappers_name}

weakuses=WeakKeyDictionary()
	
	
def check_exception(source, error, error_type=errors.generic.runtime, quiet=None):
	exclass, exexception, extraceback=sys.exc_info()
	history=traceback.extract_tb(extraceback)
	path_python=sys.prefix
	path_binary=os.path.split(os.path.dirname(sys.argv[0]))[0]
	vbline=error.line if isinstance(error, errors.generic) else None
	if not quiet:
		debug( "- - - - - - - - - - - - - - - - - - - -")
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
		if not quiet:
			debug( (u"%s, line %s%s - %s"%(path, line, ": %s"%st if st else "", function)).encode("utf-8"))
	if not quiet:
		debug( "- - - - - - - - - - - - - - - - - - - -")
	if isinstance(error, errors.generic):
		error.line=vbline
		error.source=error_type
	if not quiet:
		debug(error, console=True)
	del exclass, exexception, extraceback, history
	#managers.log_manager.error_bug(error, "vscript")


def vcompile(script=None, let=None, set=None, filename=None, bytecode=1, package=None, lines=None, environment=None, use=None, anyway=1, quiet=None, safe=None):
	if script is None:
		if let is not None:
			script="result=%s"%let
		elif set is not None:
			script="set result=%s"%set
		else:
			return vscript_default_code, vscript_default_source
	if not safe:
		mutex=auto_mutex("vscript_engine_compile_mutex")
	try:
		source=None
		if not quiet:
			debug("- - - - - - - - - - - - - - - - - - - -")
			for line, statement in enumerate(script.split("\n")):
				debug( (u"  %s      %s"%(unicode(line+1).ljust(4), statement.expandtabs(4))).encode("utf-8"))
		lexer.lineno=1
		try:
			parser.package=package
			parser.environment=vscript_default_environment if environment is None else environment
			source=parser.parse(script, lexer=lexer, debug=0, tracking=0).compose(0)
		finally:
			parser.package=None
			parser.environment=None
		if lines: source[0:0]=((None, 0, line) for line in lines)
		if not quiet:
			debug( "- - - - - - - - - - - - - - - - - - - -")
			for line, data in enumerate(source):
				debug( (u"  %s %s %s%s"%(unicode(line+1).ljust(4),
					unicode("" if data[0] is None else data[0]).ljust(4),
					"    "*data[1], data[2].expandtabs(4))).encode("utf-8"))
			debug( "- - - - - - - - - - - - - - - - - - - -")
		code=u"\n".join([u"%s%s"%(u"\t"*ident, string) for line, ident, string in source])
		if bytecode:
			code=compile(code, filename or vscript_source_string, u"exec") # CHECK: code=compile(code, vscript_source_string, u"exec")
		if use:
			use_code, use_source=vcompile(use, package=package, environment=environment, safe=True)
			weakuses[code]=use_code, use_source
		return code, source
	except errors.generic as error:
		check_exception(None, error, error_type=errors.generic.compilation, quiet=quiet)
		if anyway: return vscript_default_code, vscript_default_source
		else: raise
	except errors.python as error:
		check_exception(source, errors.system_error(unicode(error)), error_type=errors.generic.compilation, quiet=quiet)
		raise
	finally:
		if not safe:
			del mutex

def vexecute(code, source, object=None, namespace=None, environment=None, use=None, quiet=None):
	try:
		try:
			if namespace is None:
				namespace={}
			if environment is None:
				namespace[u"v_this"]=v_vdomobject(object) if object else v_nothing
				namespace.update(vscript_default_action_namespace)
			else:
				namespace.update(environment)
			if use:
				use_code, use_source=weakuses[code]
				vexecute(use_code, use_source, namespace=namespace, environment=environment)
			exec code in namespace
		except exitloop:
			exclass, exexception, extraceback=sys.exc_info()
			del exclass, exexception
			raise errors.invalid_exit_statement, None, extraceback
		except AttributeError, error:
			exclass, exexception, extraceback=sys.exc_info()
			path, line, function, text=traceback.extract_tb(extraceback)[-1]
			if path==vscript_source_string:
				if not quiet:
					debug( "- - - - - - - - - - - - - - - - - - - -")
					debug( (u"Python (AttributeError): %s"%error.message).encode("utf-8"))
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
		except ValueError as error:
			exclass, exexception, extraceback=sys.exc_info()
			path, line, function, text=traceback.extract_tb(extraceback)[-1]
			if path==vscript_source_string:
				if not quiet:
					debug( "- - - - - - - - - - - - - - - - - - - -")
					debug((u"Python (ValueError): %s"%error).encode("utf-8"))
				del exclass, exexception
				raise errors.type_mismatch, None, extraceback
			else:
				del exclass, exexception, extraceback
				raise
		except TypeError as error:
			exclass, exexception, extraceback=sys.exc_info()
			path, line, function, text=traceback.extract_tb(extraceback)[-1]
			if path==vscript_source_string:
				if not quiet:
					debug("- - - - - - - - - - - - - - - - - - - -")
					debug ((u"Python (TypeError): %s"%error).encode("utf-8"))
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
	except errors.generic as error:
		check_exception(source, error, quiet=quiet)
		raise
	except errors.python as error:
		check_exception(source, error, quiet=quiet)
		raise

def vevaluate(code, source, object=None, namespace=None, environment=None, use=None, quiet=None, result=None):
	if result is None:
		result=variant()
	if namespace is None:
		namespace={"v_result": result}
	else:
		namespace["v_result"]=result
	vexecute(code, source, object=object, namespace=namespace, environment=environment, use=use, quiet=quiet)
	return namespace["v_result"].subtype
