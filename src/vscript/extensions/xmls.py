
import xml.dom.minidom
from .. import errors, types
from ..subtypes import *
from ..variables import *
from ..conversions import *



default_indent="\t"
default_newline="\n"



def wrap(node):
	if node is None:
		return v_nothing
	elif node.nodeType==node.ELEMENT_NODE:
		return v_xmlelement(node)
	elif node.nodeType==node.ATTRIBUTE_NODE:
		return v_xmlattribute(node)
	elif node.nodeType==node.DOCUMENT_NODE:
		return v_xmldocument(node)
	else:
		return v_xmlnode(node)



v_xmlerror=xml.dom.DOMException
v_xmldomstirngsizeerror=xml.dom.DomstringSizeErr
v_xmlhierarchyrequesterror=xml.dom.HierarchyRequestErr
v_xmlindexsizeerror=xml.dom.IndexSizeErr
v_xmlinuseattributeerror=xml.dom.InuseAttributeErr
v_xmlinvalidaccesserror=xml.dom.InvalidAccessErr
v_xmlinvalidcharactererror=xml.dom.InvalidCharacterErr
v_xmlinvalidmodificationerror=xml.dom.InvalidModificationErr
v_xmlinvalidstateerror=xml.dom.InvalidStateErr
v_xmlnamespaceerror=xml.dom.NamespaceErr
v_xmlnotfounderror=xml.dom.NotFoundErr
v_xmlnotsupportederror=xml.dom.NotSupportedErr
v_xmlnodataallowederror=xml.dom.NoDataAllowedErr
v_xmlnodataallowederror=xml.dom.NoModificationAllowedErr
v_xmlsyntaxerror=xml.dom.SyntaxErr
v_xmlwrongdocumenterror=xml.dom.WrongDocumentErr



class v_xmlnodeiterator(object):

	def __init__(self, iterator):
		self.iterator=iterator

	def __iter__(self):
		return self

	def next(self):
		node=self.iterator.next()
		return wrap(node)

class v_xmlnodelist(generic):

	def __init__(self, nodes):
		self.nodes=nodes if nodes else []


	def __call__(self, *arguments, **keywords):
		if "let" in keywords:
			self.let(*arguments, **keywords)
		elif "set" in keywords:
			self.set(*arguments, **keywords)
		else:
			# Experimental hack to simulate non-object behaviour
			# Allow both let and set assigment and pass as_value for example
			if arguments:
				return self.get(*arguments, **keywords)
			else:
				return self



	def get(self, index, *arguments, **keywords):
		if arguments:
			raise errors.wrong_number_of_arguments
		return wrap(self.nodes.item(as_integer(index)))

	def let(self, *arguments, **keywords):
		raise errors.object_has_no_property

	def set(self, *arguments, **keywords):
		raise errors.object_has_no_property

	
	
	def v_length(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("length")
		else:
			return integer(self.nodes.length)

	def v_item(self, index):
		return wrap(self.nodes.item(as_integer(index)))

	def __len__(self):
		return self.nodes.length

	def __iter__(self):
		return v_xmlnodeiterator(iter(self.nodes))

class v_xmlnode(generic):
	
	def __init__(self, node):
		self.node=node

	def v_unlink(self):
		self.node.unlink()

	def v_type(self):
		raise errors.not_implemented

	def v_parent(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("parent")
		else:
			return wrap(self.node.parentNode)

	def v_prev(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("prev")
		else:
			return wrap(self.node.previousSibling)

	def v_next(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("next")
		else:
			return wrap(self.node.nextSibling)

	def v_hasattributes(self):
		return boolean(self.node.hasAttributes())

	def v_attributes(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("attributes")
		else:
			return v_xmlattributemap(self.node.attributes)

	def v_hasnodes(self):
		return boolean(self.node.hasChildNodes())

	def v_nodes(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("nodes")
		else:
			return v_xmlnodelist(self.node.childNodes)

	def v_first(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("first")
		else:
			return wrap(self.node.firstChild)

	def v_last(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("last")
		else:
			return wrap(self.node.lastChild)

	def v_name(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("name")
		else:
			name=self.node.nodeName
			return string(name) if isinstance(name, basestring) else v_null

	def v_localname(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("localname")
		else:
			name=self.node.localName
			return string(name) if isinstance(name, basestring) else v_null

	def v_prefix(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("prefix")
		else:
			name=self.node.prefix
			return string(name) if isinstance(name, basestring) else v_null

	def v_namespaceuri(self, let=None, set=None):
		raise errors.not_implemented
		if let is not None or set is not None:
			raise errors.object_has_no_property("namespaceuri")
		else:
			uri=self.node.namespaceURI
			return string(uri) if isinstance(uri, basestring) else v_null

	def v_value(self, let=None, set=None):
		if let is not None:
			self.node.nodeValue=None if let is v_null else as_string(let)
		elif set is not None:
			raise errors.object_has_no_property("value")
		else:
			value=self.node.nodeValue
			return string(value) if isinstance(value, basestring) else v_null

	def v_iselement(self):
		return boolean(self.node.nodeType==self.node.ELEMENT_NODE)

	def v_isattribute(self):
		return boolean(self.node.nodeType==self.node.ATTRIBUTE_NODE)

	def v_istext(self):
		return boolean(self.node.nodeType==self.node.TEXT_NODE)

	def v_iscdata(self):
		return boolean(self.node.nodeType==self.node.CDATA_SECTION_NODE)

	def v_isentity(self):
		raise errors.not_implemented
		return boolean(self.node.nodeType==self.node.ENTITY_NODE)

	def v_isprocessinginstruction(self):
		raise errors.not_implemented
		return boolean(self.node.nodeType==self.node.PROCESSING_INSTRUCTION_NODE)
	
	def v_iscomment(self):
		return boolean(self.node.nodeType==self.node.COMMENT_NODE)

	def v_isdocument(self):
		return boolean(self.node.nodeType==self.node.DOCUMENT_NODE)
		
	def v_isdocumenttype(self):
		raise errors.not_implemented
		return boolean(self.node.nodeType==self.node.DOCUMENT_TYPE_NODE)

	def v_isnotation(self):
		raise errors.not_implemented
		return boolean(self.node.nodeType==self.node.NOTATION_NODE)

	def v_issamenode(self, node):
		node=as_is(node)
		if isinstance(v_xmlnode, node):
			return boolean(self.node.isSameNode(node.node))
		else:
			return boolean(v_false_value)

	def v_append(self, node):
		node=as_is(node)
		if isinstance(node, v_xmlnode):
			self.node.appendChild(node)
		else:
			raise errors.invalid_procedure_call(name="append")

	def v_insert(self, node, reference):
		node, reference=as_is(node), as_is(reference)
		if isinstance(node, v_xmlnode) and isinstance(reference, v_xmlnode):
			self.node.insertBefore(node, reference)
		else:
			raise errors.invalid_procedure_call(name="insert")

	def v_remove(self, node):
		node=as_is(node)
		if isinstance(node, v_xmlnode):
			self.node.removeChild(node)
		else:
			raise errors.invalid_procedure_call(name="remove")

	def v_replace(self, node, reference):
		node, reference=as_is(node), as_is(reference)
		if isinstance(node, v_xmlnode) and isinstance(reference, v_xmlnode):
			self.node.replaceChild(reference, node)
		else:
			raise errors.invalid_procedure_call(name="replace")
	
	def v_normalize(self):
		self.node.normalize()
	
	def v_clone(self, deep=None):
		if deep is None:
			return wrap(self.node.cloneNode())
		else:
			return wrap(self.node.cloneNode(as_boolean(deep)))

	def v_compose(self, indent=None, newline=None):
		if indent is None and newline is None:
			return as_string(self.node.toxml())
		else:
			return as_string(self.node.toprettyxml(
				indent=default_indent if indent is None else as_string(indent),
				newline=default_newline if newline is None else as_string(newline)))



class v_xmlattributeiterator(object):

	def __init__(self, iterator):
		self.iterator=iterator

	def __iter__(self):
		return self

	def next(self):
		attribute=self.iterator.next()
		return v_xmlattribute(attribute)

class v_xmlattributemap(generic):

	def __init__(self, attributes):
		self.attributes=attributes

	def v_length(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("length")
		else:
			return integer(self.attributes.length)

	def v_item(self, index):
		return v_xmlattribute(self.attributes.item(as_integer(index)))

	def __len__(self):
		return self.attributes.length

	def __iter__(self):
		return v_xmlattributeiterator(iter(self.attributes.values()))

class v_xmlattribute(v_xmlnode):

	def v_name(self, let=None, set=None):
		if let is not None:
			self.node.name=as_string(let)
		elif set is not None:
			raise errors.object_has_no_property("name")
		else:
			return string(self.node.name)



class v_xmlelementiterator(v_xmlnodeiterator):

	def next(self):
		while 1:
			node=self.iterator.next()
			if node.nodeType==node.ELEMENT_NODE: return v_xmlelement(node)

class v_xmlelementlist(v_xmlnodelist):

	def __iter__(self):
		return v_xmlelementiterator(iter(self.nodes))

class v_xmlelement(v_xmlnode):

	def v_name(self, let=None, set=None):
		if let is not None:
			self.node.tagName=as_string(let)
		elif set is not None:
			raise errors.object_has_no_property("name")
		else:
			return string(self.node.tagName)

	def v_elements(self, let=None, set=None):
		if let is not None or set is not None:
			raise errors.object_has_no_property("elements")
		else:
			return v_xmlelementlist(self.node.childNodes)

	def v_search(self, name):
		return v_xmlelementlist(self.node.getElementsByTagName(as_string(name)))

	def v_searchns(self, namespaceuri, name):
		return v_xmlelementlist(self.node.getElementsByTagNameNS(
			as_string(namespaceuri), as_string(name)))

	def v_hasattribute(self, name):
		return boolean(self.node.hasAttribute(as_string(name)))

	def v_hasattributens(self, namespaceuri, name):
		return boolean(self.node.hasAttributeNS(
			as_string(namespaceuri), as_string(name)))

	def v_getattribute(self, name, default=None):
		if default is None:
			return string(self.node.getAttribute(as_string(name)))
		else:
			name=as_string(name)
			if self.node.hasAttribute(name):
				return string(self.node.getAttribute(name))
			else:
				return as_value(default)

	def v_getattributens(self, namespaceuri, name, default=None):
		if default is None:
			return string(self.node.getAttributeNS(
				as_string(namespaceuri), as_string(name)))
		else:
			name=as_string(name)
			if self.node.hasAttribute(name):
				return string(self.node.getAttributeNS(
					as_string(namespaceuri), name))
			else:
				return as_value(default)

	def v_getattributenode(self, name):
		node=self.node.getAttributeNode(as_string(name))
		return v_nothing if node is None else v_xmlattribute(node)

	def v_getattributenodens(self, namespaceuri, name):
		node=self.node.getAttributeNodeNS(as_string(namespaceuri), as_string(name))
		return v_nothing if node is None else v_xmlattribute(node)

	def v_setattribute(self, name, value):
		self.node.setAttribute(as_string(name), as_string(value))

	def v_setattributens(self, namespaceuri, name, value):
		self.node.setAttributeNS(as_string(namespaceuri),
			as_string(name), as_string(value))

	def v_setattributenode(self, node):
		node=as_is(node)
		if isinstance(node, v_xmlattribute):
			node=self.node.setAttributeNode(node)
			return v_nothing if node is None else wrap(node)
		else:
			raise errors.invalid_procedure_call(name="setattributenode")

	def v_setattributenodens(self, namespaceuri, node):
		node=as_is(node)
		if isinstance(node, v_xmlattribute):
			node=self.node.setAttributeNodeNS(as_string(namespaceuri), node)
			return v_nothing if node is None else wrap(node)
		else:
			raise errors.invalid_procedure_call(name="setattributenode")

	def v_removeattribute(self, name):
		self.node.removeAttribute(as_string(name))

	def v_removeattributens(self, namespaceuri, name):
		self.node.removeAttributeNS(as_string(namespaceuri), as_string(name))



class v_xmldocument(v_xmlelement):
	
	def __init__(self):
		self.document=xml.dom.minidom.Document()
		self.node=self.document.documentElement

	def v_parse(self, value):
		value=as_string(value)
		self.document=xml.dom.minidom.parseString(value.encode("utf-8") if isinstance(value, unicode) else value)
		self.node=self.document.documentElement

	def v_doctype(self):
		raise errors.not_implemented		

	def v_createelement(self, name):
		return v_xmlelement(self.node.createElement(as_string(name)))

	def v_createelementns(self, namespaceuri, name):
		return v_xmlelement(
			self.node.createElementNS(as_string(namespaceuri), as_string(name)))

	def v_createtextnode(self, value):
		return v_xmlnode(self.node.createTextNode(as_string(value)))

	def v_createcomment(self, value):
		return v_xmlnode(self.node.createTextNode(as_string(value)))

	def v_createprocessinginstruction(self, target, value):
		raise errors.not_implemented

	def v_createattribute(self, name):
		return v_xmlattribute(self.node.createAttribute(as_string(value)))

	def v_createattributens(self, namespaceuri, name):
		return v_xmlattribute(
			self.node.createAttributeNS(as_string(namespaceuri), as_string(value)))
