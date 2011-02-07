
import os, sys, time, unittest
import src.session.manager as manager
import src.session.session as session

class TEST(unittest.TestCase):
	"""session manager module test class"""

	def test1(self):
		"""create and delete session manager"""
		obj = manager.VDOM_session_manager.get()
		time.sleep(1)
		obj = None
		return True

	def test2(self):
		"""create & remove session"""
		sm = manager.VDOM_session_manager.get()
		sys.stderr.write("Tout = %d, Dir = \"%s\"\n" % (sm.timeout(), sm.save_directory()))
		sid = sm.create_session()
		sys.stderr.write(sid + "\n")
		self.assertEqual(1, sm.remove_session(sid))

	def test3(self):
		"""put & get session variable"""
		sm = manager.VDOM_session_manager.get()
		sid = sm.create_session()
		s = sm.get_session(sid)
		s.value("abc", 123)
		self.assertEqual(123, s.value("abc"))

	def test4(self):
		"""put session variable, save session to file & restore from it, read session variable"""
		sm = manager.VDOM_session_manager.get()
		s = session.VDOM_session()
		s.value("abc", 123)
		string = s.save()
		filename = sm.save_directory() + s.id() + ".sid"
		file = open(filename, "wb")
		file.write(string)
		file.close()
		s1 = sm.get_session(s.id())
		self.assertEqual(123, s1.value("abc"))
		os.remove(filename)

	def test5(self):
		"""try to access expired session"""
		sm = manager.VDOM_session_manager.get()
		sm.timeout(0.1)
		s = session.VDOM_session()
		s.value("abc", 123)
		string = s.save()
		filename = sm.save_directory() + s.id() + ".sid"
		file = open(filename, "wb")
		file.write(string)
		file.close()
		time.sleep(1)
		self.assertRaises(Exception, sm.get_session, s.id())
		os.remove(filename)
