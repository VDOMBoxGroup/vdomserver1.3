
import re, codecs
from htmlentitydefs import name2codepoint, codepoint2name


encode_table={unichr(codepoint): "&%s;"%name for codepoint, name in codepoint2name.iteritems()}
encode_regex=re.compile("(%s)"%"|".join(map(re.escape, encode_table.keys())))

decode_table={"&%s;"%name: unichr(codepoint) for name, codepoint in name2codepoint.iteritems()}
decode_regex=re.compile("(?:&#(\d{1,5});)|(&\w{1,8};)")


class HtmlEscapeCodec(codecs.Codec):
	
	def encode(self, input, errors='strict'):
		output=encode_regex.sub(lambda match: encode_table[match.group(0)], input)
		return output, len(output)

	def decode(self, input, errors='strict'):
		def substitute(match):
			code, entity=match.group(1, 2)
			return unichr(int(code)) if code else decode_table.get(entity, entity)
		output=decode_regex.sub(substitute, input)
		return output, len(output)


class HtmlEscapeIncrementalEncoder(codecs.IncrementalEncoder):
	
	def encode(self, input, final=False):
		raise NotImplementedError 

class HtmlEscapeIncrementalDecoder(codecs.IncrementalDecoder):
	
	def decode(self, input, final=False):
		raise NotImplementedError 


class HtmlEscapeStreamReader(HtmlEscapeCodec, codecs.StreamReader):
	pass

class HtmlEscapeStreamWriter(HtmlEscapeCodec, codecs.StreamWriter):
	pass


def search(encoding):
	if encoding=='htmlescape':
		return codecs.CodecInfo(name='htmlescape',
			encode=HtmlEscapeCodec().encode,
			decode=HtmlEscapeCodec().decode,
			incrementalencoder=HtmlEscapeIncrementalEncoder,
			incrementaldecoder=HtmlEscapeIncrementalDecoder,
			streamreader=HtmlEscapeStreamReader,
			streamwriter=HtmlEscapeStreamWriter)
	return None
