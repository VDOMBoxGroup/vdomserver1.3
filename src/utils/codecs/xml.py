
import re, codecs


encode_table={"<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&apos;", "&": "&amp;"}
encode_regex=re.compile("(%s)"%"|".join(map(re.escape, encode_table.keys())))

decode_table={entiry: symbol for symbol, entiry in encode_table.iteritems()}
decode_regex=re.compile("(%s)"%"|".join(map(re.escape, decode_table.keys())))


class XmlCodec(codecs.Codec):
	
	def encode(self, input, errors='strict'):
		output=encode_regex.sub(lambda match: encode_table[match.group(0)], input)
		return output, len(output)

	def decode(self, input, errors='strict'):
		output=decode_regex.sub(lambda match: decode_table[match.group(0)], input)
		return output, len(output)


class XmlIncrementalEncoder(codecs.IncrementalEncoder):
	
	def encode(self, input, final=False):
		raise NotImplementedError 

class XmlIncrementalDecoder(codecs.IncrementalDecoder):
	
	def decode(self, input, final=False):
		raise NotImplementedError 


class XmlStreamReader(XmlCodec, codecs.StreamReader):
	pass

class XmlStreamWriter(XmlCodec, codecs.StreamWriter):
	pass


def search(encoding):
	if encoding=='xml':
		return codecs.CodecInfo(name='xml',
			encode=XmlCodec().encode,
			decode=XmlCodec().decode,
			incrementalencoder=XmlIncrementalEncoder,
			incrementaldecoder=XmlIncrementalDecoder,
			streamreader=XmlStreamReader,
			streamwriter=XmlStreamWriter)
	return None
