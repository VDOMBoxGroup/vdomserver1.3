
import sys, os, traceback, threading
from threads import VDOM_thread, VDOM_daemon
import utils.console


path_python=sys.prefix
path_binary=os.path.dirname(sys.argv[0]) or os.getcwd()
path_server=os.path.split(path_binary)[0]


def normalize_source_path(path):
	global path_python, path_binary, path_server
	path=os.path.normpath(os.path.join(path_binary, path))
	if path.startswith(path_server): path="<server>%s"%path[len(path_server):]
	elif path.startswith(path_python): path="<python>%s"%path[len(path_python):]
	return path

def normalize_source_statement(statement, length=50):
	statement=statement.strip()
	return statement[:length-3]+"..." if len(statement)>length else statement

def show_trace(ident="", stack=None):
	if stack is None: stack=traceback.extract_stack()
	for path, line, function, statement in stack:
		path=normalize_source_path(path)
		statement=normalize_source_statement(statement)
		print "%*s %6s %s:%s:%s"%(-title_width, title, ident, path, line, function)
		title, ident="", ""

def show_threads_trace(ident="", title_width=30):
	threads={thread.ident: thread for thread in threading.enumerate()}
	for ident, frame in sys._current_frames().items():
		thread=threads.get(ident, None)
		if not thread: continue
		flags=tuple(flag for flag in ("Daemon" if thread.daemon else None, 
			"Smart" if isinstance(thread, (VDOM_thread, VDOM_daemon)) else None) if flag)
		details=" (%s)"%", ".join(flags) if flags else ""
		title="%s...%s"%(thread.name[:title_width-len(details)-3], details) \
			if len(thread.name)>title_width-len(details) else \
			"%s%s"%(thread.name, details)
		ident=thread.ident
		stack=traceback.extract_stack(frame)
		for path, line, function, statement in stack:
			path=normalize_source_path(path)
			statement=normalize_source_statement(statement)
			print "%*s %6s %s:%s:%s"%(-title_width, title, ident, path, line, function)
			title, ident="", ""
