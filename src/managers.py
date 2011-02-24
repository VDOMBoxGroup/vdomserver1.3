
def register(name, manager_class):
	globals()[name]=manager_class()

