"""script that runs all available tests"""

import os, sys, unittest
import gettext
gettext.install("vdom2_tests")
sys.path.append("..")

if( len(sys.argv) > 1 ):
	files = sys.argv
	exceptions = [sys.argv[ 0 ]]
else:
	files = os.listdir(".")
	#print files
	exceptions = ["__init__.py", "__run.py"]

# for each file
for file in files:
	# check if need to process this file
	if file in exceptions:
		continue
	try:
		fname = os.path.splitext(file)[0]
	except: continue
	try:
		if os.path.splitext(file)[1] != ".py":
			continue
	except: continue
	if fname == "":
		continue

	# start
	sys.stderr.write("\n\n")
	sys.stderr.write('='*70)
	sys.stderr.write("\n'" + fname + "'\n")

	# import module
	try:
		exec "import " + fname
		exec "reload(" + fname + ")"
	except ImportError, e:
		sys.stderr.write(_("Import error: "))
		sys.stderr.write(str(e))
		continue
	except:
		sys.stderr.write(_("Unspecified error: "))
		sys.stderr.write(str(sys.exc_info()[0]))
		continue

	# import test class and run unittest
	try:
		exec "from " + fname + " import TEST"
	except:
		sys.stderr.write(_("Module \"%s\" error: %s") % (fname, str(sys.exc_info()[0])))
		exec "del(" + fname + ")"
		continue

	suite = unittest.TestLoader().loadTestsFromTestCase(TEST)
	unittest.TextTestRunner(verbosity=2).run(suite)

	# delete module
	exec "del(" + fname + ")"
