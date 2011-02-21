
import sys, os, traceback, threading
from thread import VDOM_thread, VDOM_daemon


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


def get_thread_line(thread):
	for thread_ident, stack in sys._current_frames().items():
		if thread_ident==thread.ident:
			trace=traceback.extract_stack(stack)
			path, line, function, statement=traceback.extract_stack(stack)[-1]
			path=normalize_source_path(path)
			statement=normalize_source_statement(statement)
			return path, line, function, statement
	

def show_active_threads(ident=""):
	for thread in threading.enumerate():
		path, line, function, statement=get_thread_line(thread)
		print "%s%-20s %1s %1s %6s %s"%(ident, thread.name,
			"D" if thread.daemon else " ",
			"V" if isinstance(thread, (VDOM_thread, VDOM_daemon)) else " ",
			thread.ident,
			"%s, line %s, in %s"%(path, line, function))

def show_active_threads_stack(ident=""):
	for thread in threading.enumerate():
		print "%s%-20s %1s %1s %6s"%(ident, thread.name,
			"D" if thread.daemon else " ",
			"V" if isinstance(thread, (VDOM_thread, VDOM_daemon)) else " ",
			thread.ident)
		path, line, function, statement=get_thread_line(thread)
		show_thread_stack(thread, ident=ident+"    ")

def show_thread_stack(thread, ident=""):
	for thread_ident, stack in sys._current_frames().items():
		if thread_ident!=thread.ident: continue
		trace=traceback.extract_stack(stack)
		for path, line, function, statement in traceback.extract_stack(stack):
			path=normalize_source_path(path)
			statement=normalize_source_statement(statement)
			print "%s%s, line %s, in %s%s"%(ident, path, line, function,
				": %s"%statement if statement else "")
