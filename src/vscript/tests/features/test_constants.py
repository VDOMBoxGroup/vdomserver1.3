
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
	boolean, error, binary, date, array, dictionary, generic, nothing, \
	nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestConstants(VScriptTestCase):

	def test_vcrlf_constant(self):
		assert self.evaluate("vcrlf").is_string("\r\n")
		assert self.evaluate("vbcrlf").is_string("\r\n")

	def test_vcr_constant(self):
		assert self.evaluate("vcr").is_string("\r")
		assert self.evaluate("vbcr").is_string("\r")

	def test_vlf_constant(self):
		assert self.evaluate("vlf").is_string("\n")
		assert self.evaluate("vblf").is_string("\n")

	def test_vformfeed_constant(self):
		assert self.evaluate("vformfeed").is_string("\f")
		assert self.evaluate("vbformfeed").is_string("\f")

	def test_vnewline_constant(self):
		assert self.evaluate("vnewline").is_string("\n")
		assert self.evaluate("vbnewline").is_string("\n")

	def test_vnullchar_constant(self):
		assert self.evaluate("vnullchar").is_string("\0")
		assert self.evaluate("vbnullchar").is_string("\0")

	def test_vnullstring_constant(self):
		assert self.evaluate("vnullstring").is_string("\0")
		assert self.evaluate("vbnullstring").is_string("\0")

	def test_vtab_constant(self):
		assert self.evaluate("vtab").is_string("\t")
		assert self.evaluate("vbtab").is_string("\t")

	def test_vverticaltab_constant(self):
		assert self.evaluate("vverticaltab").is_string("\v")
		assert self.evaluate("vbverticaltab").is_string("\v")

	def test_vbinarycompare_constant(self):
		assert self.evaluate("vbinarycompare").is_integer(0)
		assert self.evaluate("vbbinarycompare").is_integer(0)

	def test_vtextcompare_constant(self):
		assert self.evaluate("vtextcompare").is_integer(1)
		assert self.evaluate("vbtextcompare").is_integer(1)

	def test_vdatabasecompare_constant(self):
		assert self.evaluate("vdatabasecompare").is_integer(2)
		assert self.evaluate("vbdatabasecompare").is_integer(2)
