#!/usr/bin/python

"""
inject utility
"""

import sys
import xml.dom
from xml.dom.minidom import parse
from xml.dom import Node
import base64



def load_file(filename):
	file=open(filename, "rb")
	resource=file.read()
	file.close()
	return resource

def save_file(filename, value):
	file=open(filename, "w+b")
	file.write(value)
	file.close()

def search_element(element, element_name):
	for node in element.childNodes:
		if node.nodeType==Node.ELEMENT_NODE and node.nodeName.upper()==element_name.upper():
			return node
	return None

def search_cdata(element):
	for node in element.childNodes:
		if node.nodeType==Node.CDATA_SECTION_NODE:
			return node
	return None

def search_information_section(type, section):
	information=search_element(type, "Information")
	section=search_element(information, section)
	if section==None:
		section=document.createElement(section)
		information.appendChild(section)
	return section



try:
	xml=sys.argv[1]
	name=sys.argv[2]
#	filename=sys.argv[3]
except:
	sys.stdout.write("Incorrect parameters\n")
	sys.exit(0)

#document=parse(xml)

#type=document.documentElement
value=base64.b64encode(load_file(name))
save_file(xml, value)

#if name=="Icon":
	#section=search_information_section(type, "Icon")
#elif name=="EditorIcon":
	#section=search_information_section(type, "EditorIcon")
#elif name=="StructureIcon":
	#section=search_information_section(type, "StructureIcon")
#else:
	#sys.stdout.write("Unknown section name\n")
	#sys.exit(0)

#cdata=search_cdata(section)
#if cdata:
	#section.replaceChild(value, cdata)
#else:
	#section.appendChild(value)

#save_file(xml, document.toxml())
