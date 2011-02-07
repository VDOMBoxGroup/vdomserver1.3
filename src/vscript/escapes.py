
_escapeignore="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

def escape(string):
    return u"".join(char if char in _escapeignore \
    	else u"%%u%04X"%ord(char) for char in string).replace(u"%u00", u"%")

def unescape(string):
	escapes=string.split(u"%")
	for index, chain in enumerate(escapes[1:]):
		try:
			escapes[index+1]=unichr(int(chain[1:5], 16))+chain[5:] if chain.startswith(u"u") \
				else unichr(int(chain[:2], 16))+chain[2:]
		except ValueError:
			pass
	return u"".join(escapes)

_escapemap={u"&": u"&amp;", u">": u"&gt;", u"<": u"&lt;", u'"': u"&quot;"}

def escape_page(string):
	return u"".join(_escapemap[char] if char in _escapemap \
		else u"&#%04X"%ord(char) if char>u"\x80" \
		else char for char in string)

def unescape_page(string):
	escapes=string.split(u"&#")
	for index, chain in enumerate(escapes[1:]):
		try:
			escapes[index+1]=unichr(int(chain[:4], 16))+chain[4:]
		except ValueError:
			pass
	return u"".join(escapes).replace(u"&quot", u'"').replace(u"&lt;", u"<").replace(u"&gt;", u">").replace(u"&amp;", u"&")
