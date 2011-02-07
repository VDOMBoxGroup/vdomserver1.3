
import unittest, sys
import src.session.session as session

class TEST(unittest.TestCase):
	"""session module test class"""

	def test1(self):
		"""create session and show it`s id"""
		s = session.VDOM_session()
		return s.id()

	def test2(self):
		"""put & get value"""
		s = session.VDOM_session()
		s.value("abc", 123)
		self.assertEqual(123, s.value("abc"))

	def test3(self):
		"""get key list"""
		s = session.VDOM_session()
		s.value("abc", 123)
		s.value("def", 456)
		s.value("ghi", 789)
		self.assertEqual(["abc", "def", "ghi"].sort(), s.get_key_list().sort())

	def test4(self):
		"""create N sessions and check their id uniqueness"""
		sess = []
		N = 100
		for i in xrange(N):
			s = session.VDOM_session()
			for j in xrange(len(sess)):
				if s.id() == sess[j].id():
					break
			else: sess.append(s)
		sys.stderr.write("\n%d/%d IDs are unique\n" % (len(sess), N))
		return 1

	def test5(self):
		"""put value with invalid key"""
		s = session.VDOM_session()
		l = [1, 2, 3]
		self.assertRaises(KeyError, s.value, l, 123)
