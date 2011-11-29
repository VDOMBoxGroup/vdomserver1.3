
import sys, os
import ply.lex as lex
import ply.yacc as yacc
from . import lexemes, syntax


tablepath=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), VDOM_CONFIG["TEMP-DIRECTORY"]))
lexer_table_name="vscript_%s_lexer_table"%os.path.splitext(os.path.basename(sys.argv[0]))[0]
parser_table_name="vscript_%s_parser_table"%os.path.splitext(os.path.basename(sys.argv[0]))[0]
optimize=1


if VDOM_CONFIG["DISABLE-VSCRIPT"]:
	print "VScript are disabled through configuration"
	lexer=None
	parser=None
else:
	print "Preparing VScript engine...",
	lexer=lex.lex(module=lexemes, debug=0, optimize=optimize, outputdir=tablepath, lextab=lexer_table_name)
	parser=yacc.yacc(module=syntax, debug=0, start="source", optimize=optimize, outputdir=tablepath, tabmodule=parser_table_name)
	print "Done"
