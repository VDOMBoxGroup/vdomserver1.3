
def getany(options, name, default=None):
	if options and name in options:
		return options[name]
	else:
		return default
