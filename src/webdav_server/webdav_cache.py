import collections, os
import functools
import wsgidav.util as util
import managers
import posixpath
def lru_cache(maxsize=100):
	'''Least-recently-used cache decorator.

	Arguments to the cached function must be hashable.
	Cache performance statistics stored in f.hits and f.misses.
	http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

	'''
	def decorating_function(user_function):
		cache = collections.OrderedDict()    # order: least recent to most recent

		@functools.wraps(user_function)
		def wrapper(*args, **kwds):
			key = args
			if kwds:
				key += tuple(sorted(kwds.items()))
			try:
				result = cache.pop(key)
				wrapper.hits += 1
			except KeyError:
				result = user_function(*args, **kwds)
				wrapper.misses += 1
				if len(cache) >= maxsize:
					cache.popitem(0)    # purge least recently used cache entry
			if result:
				cache[key] = result         # record recent use of this key
			return result

		def invalidate(app_id, obj_id, path):
			key = (app_id, obj_id, path.encode("utf8"))
			try:
				result = cache.pop(key)
				cache[key] = (result[0], 1)
			except:
				pass
			for key in cache:
				if (key[0], key[1]) == (app_id, obj_id) and util.isChildUri(util.toUnicode(path), util.toUnicode(key[2])):
					del cache[key]


		def get_children_names(app_id, obj_id, path):
			cnames = []			
			func_name = "getMembers"
			xml_data = """{"path": "%s"}""" % path
			ret = managers.dispatcher.dispatch_action(app_id, obj_id, func_name, "",xml_data)
			if ret:
				cnames = list(ret.keys()) if isinstance(ret, dict) else ret
			parent = cache.get((app_id, obj_id, path))
			if parent and parent[1] == 1:
				cache.pop((app_id, obj_id, path))
				cache[(app_id, obj_id, path)] = (parent[0], 0)				
			#else:
			#	for key in cache:
			#		if (key[0], key[1]) == (app_id, obj_id) and util.isChildUri(path, key[2]) and \
			#		   os.path.normpath(path) == os.path.normpath(util.getUriParent(key[2])):
			#			cnames.append(util.getUriName(key[2]))
			return cnames
		
		def change_property_value(app_id, obj_id, path, propname, value):
			props = cache.get((app_id, obj_id, path))[0]
			if props:
				try:
					props[propname] = value
					cache[(app_id, obj_id, path)] = (props, 0)
				except:
					pass
			
					
		def change_parents_property(app_id, obj_id, path, propname, value):
			change_property_value(app_id, obj_id, path, propname, value)
			for key in cache:
				if (key[0], key[1]) == (app_id, obj_id) and posixpath.normpath(util.getUriParent(path)) == os.path.normpath(key[2]):
					change_parents_property(app_id, obj_id, key[2], propname, value)			

		def clear():
			cache.clear()
			wrapper.hits = wrapper.misses = 0
			
		wrapper.invalidate = invalidate
		wrapper.get_children_names = get_children_names
		wrapper.change_property_value = change_property_value
		wrapper.change_parents_property = change_parents_property
		wrapper.hits = wrapper.misses = 0
		wrapper.clear = clear
		return wrapper
	return decorating_function