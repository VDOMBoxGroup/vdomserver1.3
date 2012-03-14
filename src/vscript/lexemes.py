
from . import errors


prefix=u"v_"

reserved=(u"DIM", u"MOD", u"IS", u"NOT", u"AND", u"OR", u"XOR", u"TRUE", u"FALSE", u"USE",
	u"BYVAL", u"BYREF", u"CALL", u"PROPERTY", u"GET", u"LET", u"SET", u"SUB", u"FUNCTION",
	u"CLASS", u"PUBLIC", u"PRIVATE", u"DEFAULT", u"NEW", u"WITH", u"INHERITS", u"MYBASE", u"MYCLASS", u"MY",
	#u"PROTECTED", u"FRIEND",
	#u"NOTINHERITABLE", u"MUSTINHERIT",
	#u"OVERRIDABLE", u"OVERRIDES", u"NOTOVERRIDABLE", u"MUSTOVERRIDE",    
	u"IF", u"THEN", u"ELSE", u"ELSEIF", u"SELECT", u"CASE", u"DO", u"LOOP", u"WHILE", u"UNTIL", u"WEND",
	u"FOR", u"EACH", u"IN", u"TO", u"STEP", u"NEXT", u"TRY", u"CATCH", u"AS", u"FINALLY",
	u"END", u"EXIT", u"CONST", u"REDIM", u"PRESERVE", u"ERASE", u"RANDOMIZE", u"PRINT", u"TOUCH",
	u"EMPTY", u"NOTHING", u"NULL", u"NAN", u"INFINITY")
tokens=reserved+(u"PYTHON",
	u"VCR", u"VCRLF", u"VFORMFEED", u"VLF", u"VNEWLINE", u"VNULLCHAR", u"VNULLSTRING",
	u"VTAB", u"VVERTICALTAB", u"VBINARYCOMPARE", u"VTEXTCOMPARE", u"VDATABASECOMPARE",
	u"REM", u"NE", u"LE", u"GE", u"NUMBER", u"DOUBLE", u"DATE", u"STRING", u"NAME", u"NEWLINE")
literals=[u'&', u'(', u')', u'*', u'+', u',', u'-', u'.', u'/', u':', u'<', u'=', u'>', u'\\', u'^']


words=reserved
reserved={}
for word in words:
    reserved[word.lower()]=word
del words


def t_vcr(t):
	r'[Vv][Bb]?[Cc][Rr]'
	t.type=u"VCR"
	t.value=(t.lexer.lineno, "string(u\"\\r\")")
	return t

def t_vcrlf(t):
	r'[Vv][Bb]?[Cc][Rr][Ll][Ff]'
	t.type=u"VCRLF"
	t.value=(t.lexer.lineno, "string(u\"\\r\\n\")")
	return t

def t_vformfeed(t):
	r'[Vv][Bb]?[Ff][Oo][Rr][Mm][Ff][Ee][Ee][Dd]'
	t.type=u"VFORMFEED"
	t.value=(t.lexer.lineno, "string(u\"\\f\")")
	return t

def t_vlf(t):
	r'[Vv][Bb]?[Ll][Ff]'
	t.type=u"VLF"
	t.value=(t.lexer.lineno, "string(u\"\\n\")")
	return t

def t_vnewline(t):
	r'[Vv][Bb]?[Nn][Ee][Ww][Ll][Ii][Nn][Ee]'
	t.type=u"VNEWLINE"
	t.value=(t.lexer.lineno, "string(u\"\\n\")") # string(u\"\\r\\n\") FOR WINDOWS
	return t

def t_vnullchar(t):
	r'[Vv][Bb]?[Nn][Uu][Ll][Ll][Cc][Hh][Aa][Rr]'
	t.type=u"VNULLCHAR"
	t.value=(t.lexer.lineno, "string(u\"\\0\")")
	return t

def t_vnullstring(t):
	r'[Vv][Bb]?[Nn][Uu][Ll][Ll][Ss][Tt][Rr][Ii][Nn][Gg]'
	t.type=u"VNULLSTRING"
	t.value=(t.lexer.lineno, "string(u\"\\0\")")
	return t

def t_vtab(t):
	r'(?:^|[^A-Za-z])[Vv][Bb]?[Tt][Aa][Bb](?:[^0-9A-Za-z]|$)'
	t.type=u"VTAB"
	t.value=(t.lexer.lineno, "string(u\"\\t\")")
	return t

def t_vverticaltab(t):
	r'[Vv][Bb]?[Vv][Ee][Rr][Tt][Ii][Cc][Aa][Ll][Tt][Aa][Bb]'
	t.type=u"VVERTICALTAB"
	t.value=(t.lexer.lineno, "string(u\"\\v\")")
	return t

def t_vbinarycompare(t):
	r'[Vv][Bb]?[Bb][Ii][Nn][Aa][Rr][Yy][Cc][Oo][Mm][Pp][Aa][Rr][Ee]'
	t.type=u"VBINARYCOMPARE"
	t.value=(t.lexer.lineno, "integer(0)")
	return t

def t_vtextcompare(t):
	r'[Vv][Bb]?[Tt][Ee][Xx][Tt][Cc][Oo][Mm][Pp][Aa][Rr][Ee]'
	t.type=u"VTEXTCOMPARE"
	t.value=(t.lexer.lineno, "integer(1)")
	return t

def t_vtextcompare(t):
	r'[Vv][Bb]?[Dd][Aa][Tt][Aa][Bb][Aa][Ss][Ee][Cc][Oo][Mm][Pp][Aa][Rr][Ee]'
	t.type=u"VDATABASECOMPARE"
	t.value=(t.lexer.lineno, "integer(2)")
	return t

def t_ne(t):
	r'<>'
	t.type=u"NE"
	t.value=(t.lexer.lineno, u"<>")
	return t

def t_le(t):
	r'<='
	t.type=u"LE"
	t.value=(t.lexer.lineno, u"<=")
	return t

def t_ge(t):
	r'>='
	t.type=u"GE"
	t.value=(t.lexer.lineno, ">=")
	return t

def t_comment(t):
	r'\'[^\n]*'
	pass

def t_rem(t):
	r'rem\s.*'
	t.type=u"REM"
	t.value=(t.lexer.lineno, unicode(t.value))
	return t

def t_multiline(t):
	r'_\n'
	pass

def t_double(t):
	r'\d+\.\d+([Ee][+-]?\d+)? | [+-]?\d+[Ee][+-]?\d+'
	t.type=u"DOUBLE"
	t.value=(t.lexer.lineno, unicode(t.value))
	return t

def t_number(t):
	r'\d+'
	t.type=u"NUMBER"
	t.value=(t.lexer.lineno, unicode(t.value))
	return t

def t_date(t):
	r'\#[^#]+\#'
	t.type=u"DATE"
	t.value=(t.lexer.lineno, unicode(t.value[1:-1]))
	return t

def t_string(t):
	r'\"([^\"\n]|(\"\"))*\"'
	t.type=u"STRING"
	t.value=(t.lexer.lineno, unicode(t.value[1:-1].replace(u"\"\"", u"\"")))
	return t

def t_character(t):
	r'\&[Hh][0-9A-Fa-f]+'
	t.type=u"STRING"
	t.value=(t.lexer.lineno, unichr(int(t.value[2:], 16)))
	return t

def t_python(t):
	r'`[^\n]*'
	value=unicode(t.value[1:])
	value=value.replace(u"\\n", u"\n")
	t.type=u"PYTHON"
	t.value=(t.lexer.lineno, unicode(value))
	return t

def t_name(t):
	r'[a-zA-Z][a-zA-Z0-9_]*'
	value=unicode(t.value.lower())
	t.type=reserved.get(value, u"NAME")
	t.value=(t.lexer.lineno, prefix+value) if t.type==u"NAME" else (t.lexer.lineno, value)
	return t

def t_newline(t):
	r'(\n|\r\n)+'
	t.lexer.lineno+=t.value.count(u"\n")
	t.type=u"NEWLINE"
	t.value=(t.lexer.lineno, unicode(t.value))
	return t

t_ignore=" \t"

def t_error(t):
	raise errors.invalid_character(t.value[0] if t is not None else "Unknown", line=t.lexer.lineno)
	t.lexer.skip(1)
