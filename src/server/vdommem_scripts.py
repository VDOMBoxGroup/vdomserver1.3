
from utils.encode import *

def wrap_object(obj):
	p_id = ""
	if obj.parent:
		p_id = obj.parent.id
	result = "<Object Name=\"%s\" ID=\"%s\" Type=\"%s\" ParentID=\"%s\">\n" % (obj.original_name, obj.id, obj.type.id, p_id)
	result += "<Attributes>\n"
	for a in obj.get_attributes().values():
		result += "<Attribute Name=\"%s\"><![CDATA[%s]]></Attribute>\n" % (a.name, a.original_value)
#	for a in obj.attr_names:
#		if obj.attr_names[a]:
#			result += "<Attribute Name=\"%s\"><![CDATA[%s]]></Attribute>\n" % (a, getattr(obj, a))
	result += "</Attributes>\n"
	result += "<Objects/>\n"
	result += "</Object>"
	return result

def wrap_objects_list(l):
	result = "<Objects>"
	for o in l:
		result += wrap_object(o)
	return result + "</Objects>"

def wrap_objects_tree(obj):
	p_id = ""
	if obj.parent:
		p_id = obj.parent.id
	result = "<Object Name=\"%s\" ID=\"%s\" Type=\"%s\" ParentID=\"%s\">\n" % (obj.original_name, obj.id, obj.type.id, p_id)
	result += "<Attributes>\n"
	for a in obj.get_attributes().values():
		result += "<Attribute Name=\"%s\"><![CDATA[%s]]></Attribute>\n" % (a.name, a.original_value)
	result += "</Attributes>\n"
	result += "<Objects>\n"
	for o in obj.objects_list:
		result += wrap_objects_tree(o)
	result += "</Objects>\n"
	result += "</Object>\n"
	return result

def wrap_application_info(app):
	result = ""
	for key in app.info_map:
		cap = app.info_map[key][2]
		result += "<%s>%s</%s>\n" % (cap, attrvalue(getattr(app, app.info_map[key][0])), cap)
	result += "<Numberofpages>%d</Numberofpages>\n" % len(app.objects)
	result += "<Numberofobjects>%d</Numberofobjects>\n" % app.objects_amount()
	return "<Information>\n%s</Information>\n" % result

def wrap_application(app):
	return "<Application ID=\"%s\" Name=\"%s\">%s</Application>" % (app.id, app.name, wrap_application_info(app))
