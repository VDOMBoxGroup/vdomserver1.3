
try:
	from wscript import v_wscript
	from regexp import v_regexp
	from dictionary import v_dictionary
	from list import v_list
	from connection import v_connectionerror, v_proxy, v_connection
	from jsons import v_asjson, v_tojson
	from xmls import (v_xmlnode, v_xmlattribute, v_xmlelement, v_xmldocument,
		v_xmlerror, v_xmldomstirngsizeerror, v_xmlhierarchyrequesterror,
		v_xmlindexsizeerror, v_xmlinuseattributeerror, v_xmlinvalidaccesserror,
	    v_xmlinvalidcharactererror, v_xmlinvalidmodificationerror, v_xmlinvalidstateerror,
	    v_xmlnamespaceerror, v_xmlnotfounderror, v_xmlnotsupportederror,
	    v_xmlnodataallowederror, v_xmlnodataallowederror, v_xmlsyntaxerror,
	    v_xmlwrongdocumenterror)
except Exception as error:
	print "- - - - - - - - - - - - - - - - - - - -"
	print "Unable to import extension: %s"%error
	raise error
