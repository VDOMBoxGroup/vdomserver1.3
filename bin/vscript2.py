
import sys, traceback, os, re, gettext
import __builtin__

from copy import copy, deepcopy

path=os.path.split(os.path.dirname(sys.argv[0]))[0]
sys.path.append(path or "..")
gettext.install("vdom2")

from src.config import *
__builtin__.VDOM_CONFIG = VDOM_CONFIG
__builtin__.VDOM_CONFIG_1 = VDOM_CONFIG_1

from src.vscript.engine import vsetup, vcompile, vexecute



def my_debug(data, tag="", console=None):
	print data

__builtin__.debug = my_debug



if len(sys.argv)==2:
	try:
		vsetup(skip_wrappers=1)
		script=open(sys.argv[1]).read()
		code, source=vcompile(script)
		vexecute(code, source)
	finally:
		print "[VScript] Press any key to continue"
		raw_input()
