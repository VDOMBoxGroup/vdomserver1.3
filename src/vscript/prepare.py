
import sys, os

import ply.lex as lex
import ply.yacc as yacc

import lexemes, syntax

tablepath=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), VDOM_CONFIG["TEMP-DIRECTORY"]))
tablename="vscript_%s_table"%os.path.splitext(os.path.basename(sys.argv[0]))[0]

if VDOM_CONFIG["DISABLE-VSCRIPT"]:
	print "VScript are disabled through configuration"
	lexer=None
	parser=None
else:
	print "Preparing VScript engine... ",
	lexer=lex.lex(module=lexemes, debug=0)
	parser=yacc.yacc(module=syntax, debug=0, start="source", tabmodule=tablename, outputdir=tablepath)
	print "Done"
