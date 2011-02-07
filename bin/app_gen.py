import sys, re, base64, os

file_re = re.compile(r"\#file\((.+?)\)", re.IGNORECASE)

sys.path.append("./")

from xml.dom.minidom import parse
from xml.dom import Node
import uuid

doc = parse(sys.argv[1])
root = doc.documentElement

files = {}	# map file name to resource ID
types = {}	# map type name to type ID

# types
ret = os.listdir("./types")
for fname in ret:
	if "xml" == fname.split(".")[-1].lower():
		d = parse("./types/" + fname)
		r = d.documentElement
		types[r.getElementsByTagName("Name")[0].firstChild.data] = r.getElementsByTagName("ID")[0].firstChild.data

print str(types)

def test(value):
	global files
	# file
	ret = file_re.split(value)
	for idx in xrange(len(ret)):
		if 1 == idx % 2:	# this is file name
			fname = ret[idx]
			if fname not in files:
				files[fname] = str(uuid.uuid4())
			ret[idx] = "#Res(%s)" % files[fname]
	return "".join(ret)

def process(node):
	for child in node.childNodes:
		if child.nodeType == Node.ELEMENT_NODE:
			if "id" == child.tagName.lower() and not child.hasChildNodes():
#				for child2 in child.childNodes:
#					if child2.nodeType == Node.ELEMENT_NODE:
#						child.removeChild(child2)
				child.appendChild(doc.createTextNode(str(uuid.uuid4())))
			newattr = {}
			oldattr = []
			for i in xrange(child.attributes.length):
				attr = child.attributes.item(i)
				if "id" == attr.name.lower() and "" == child.getAttribute(attr.name):
					newattr["ID"] = str(uuid.uuid4())
				elif "type" == attr.name.lower():
					v = child.getAttribute(attr.name)
					if v in types:
						newattr["Type"] = types[v]
					else:
						newattr["Type"] = v
				else:
					if "id" == attr.name.lower(): newattr["ID"] = child.getAttribute(attr.name)
					else: newattr[attr.name.capitalize()] = child.getAttribute(attr.name)
				oldattr.append(attr.name)
			for i in oldattr:
				child.removeAttribute(i)
			for i in newattr:
				child.setAttribute(i, newattr[i])
	for child in node.childNodes:
		if child.nodeType == Node.ELEMENT_NODE:
			if "id" != child.tagName.lower():
				child.tagName = child.tagName.capitalize()
			process(child)
		elif child.nodeType == Node.CDATA_SECTION_NODE or child.nodeType == Node.TEXT_NODE:
			child.data = test(child.data)


process(root)

res_elem = None
ret = doc.getElementsByTagName("Resources")
if len(ret) == 0:
	res_elem = doc.createElement("Resources")
	root.appendChild(doc.createTextNode("\t"))
	root.appendChild(res_elem)
	root.appendChild(doc.createTextNode("\n"))
	res_elem.appendChild(doc.createTextNode("\n"))
else:
	res_elem = ret[0]

print "Files:"
print str(files)
for fname in files:
	try:
		f = open(fname, "rb")
		data = f.read()
		f.close()
		data = base64.b64encode(data)
		res = doc.createElement("Resource")
		res.setAttribute("ID", files[fname])
		res.setAttribute("Name", fname)
		res.setAttribute("Type", fname.split(".")[-1])
		res_elem.appendChild(doc.createTextNode("\t\t"))
		res_elem.appendChild(res)
		res_elem.appendChild(doc.createTextNode("\n"))
		res.appendChild(doc.createCDATASection(data))
	except:
		print "File", fname, "processing error"
res_elem.appendChild(doc.createTextNode("\t"))

f = open(sys.argv[1] + ".out", "wb")
f.write(root.toxml().encode("utf-8"))
f.close()
