
import codecs, htmlescape, xmlescape


codecs.register(htmlescape.search)
codecs.register(xmlescape.search)
