
import options

if not options.skip_wrappers:
	try:
		from sqlite import v_vdomdbconnection, v_vdomdbrecordset
		from imaging import v_vdomimaging
		from vdombox import v_vdombox
	except Exception as error:
		print "- - - - - - - - - - - - - - - - - - - -"
		print "Unable to import wrapper: %s"%error
		raise error
