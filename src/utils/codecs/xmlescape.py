
import re, codecs


encode_table={"<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&apos;", "&": "&amp;"}
encode_regex=re.compile("(%s)"%"|".join(map(re.escape, encode_table.keys())))

decode_table={entiry: symbol for symbol, entiry in encode_table.iteritems()}
decode_regex=re.compile("(%s)"%"|".join(map(re.escape, decode_table.keys())))


class XmlEscapeCodec(codecs.Codec):
	
	def encode(self, input, errors='strict'):
		output=encode_regex.sub(lambda match: encode_table[match.group(0)], input)
		return output, len(output)

	def decode(self, input, errors='strict'):
		output=decode_regex.sub(lambda match: decode_table[match.group(0)], input)
		return output, len(output)


class XmlEscapeIncrementalEncoder(codecs.IncrementalEncoder):
	
	def encode(self, input, final=False):
		raise NotImplementedError 

class XmlEscapeIncrementalDecoder(codecs.IncrementalDecoder):
	
	def decode(self, input, final=False):
		raise NotImplementedError 


class XmlEscapeStreamReader(XmlEscapeCodec, codecs.StreamReader):
	pass

class XmlEscapeStreamWriter(XmlEscapeCodec, codecs.StreamWriter):
	pass


def search(encoding):
	if encoding=='xmlescape':
		return codecs.CodecInfo(name='xmlescape',
			encode=XmlEscapeCodec().encode,
			decode=XmlEscapeCodec().decode,
			incrementalencoder=XmlEscapeIncrementalEncoder,
			incrementaldecoder=XmlEscapeIncrementalDecoder,
			streamreader=XmlEscapeStreamReader,
			streamwriter=XmlEscapeStreamWriter)
	return None
