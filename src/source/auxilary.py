
import re


patterns={
	"vscript": {
		"remove": re.compile("(?:^\s*[Rr][Ee][Mm].+$)|(?:'.+$)|(?:\"[^\"]*\")", re.MULTILINE),
		"search": re.compile("this(\.\s*[_A-Za-z][_0-9A-Za-z]*)+")}, # TODO: Add ^[_0-9A-Za-z] before this
	"python": {
		"remove": re.compile("(?:#.+$)|(?:[uU]?[rR]?(?:"\
			r"'''(?:[^']|\\'|'{1,2}(?!'))*'''|'(?:[^'\n]|\\')*'(?!')|"\
			r'"""(?:[^"]|\\"|"{1,2}(?!"))*"""|"(?:[^"\n]|\\")*"(?!"))'\
			")", re.MULTILINE),
		"search": re.compile("self(\.[_A-Za-z][_0-9A-Za-z]*)+")}} # TODO: Add ^[_0-9A-Za-z] before self



def enable_dynamic(object, action_name, context, names):
	objects={}
	for item in object.get_objects_list():
		objects[item.name]=item
	for name, subnames in names.iteritems():
		if name in objects:
			subobject=objects[name]
			#debug("[Compiler] Assume %s as dynamic, using in action %s (context %s)"%(subobject.id, action_name, context))
			if not hasattr(subobject, "dynamic"):
				subobject.dynamic={(action_name, context): 1}
			else:
				subobject.dynamic[(action_name, context)]=1
			if subnames:
				enable_dynamic(subobject, action_name, context, subnames)

def analyse_script_structure(source, language):
	#debug("[Compiler] Analyse action structure: %s"%language)
	source=patterns[language]["remove"].sub("\01", source)
	names={}
	for match in patterns[language]["search"].finditer(source):
		#debug("[Compiler] Name: %s"%match.group().lower())
		this=names
		for name in match.group().lower().split(".")[1:]:
			name=name.strip()
			if this is None:
				this={name: None}
				last[last_name]=this
				last=this
				last_name=name
				this=None
			elif name in this:
				last=this
				last_name=name
				this=this[name]
			else:
				this[name]=None
				last=this
				last_name=name
				this=None
	return names
