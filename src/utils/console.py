
import sys, os, struct


def get_windows_console_size():
	import ctypes

	handle=ctypes.windll.kernel32.GetStdHandle(-11)
	chars=ctypes.create_string_buffer(22)
	if ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, chars):
		bx, by, cx, cy, wa, x1, y1, x2, y2, mx, my=struct.unpack("hhhhHhhhhhh", chars.raw)
		width, height=x2-x1+1, y2-y1+1
	else:
		width, height=sys.maxint, sys.maxint
	return width, height

def get_linux_console_size():
	import fcntl, termios, subprocess

	try:
		data=fcntl.ioctl(1, termios.TIOCGWINSZ, '1234')
		height, width=struct.unpack('hh', data)
		return width, height
	except:
		pass
	
	try:
		descriptor=os.open(os.ctermid(), os.O_RDONLY)
		try:
			data=fcntl.ioctl(descriptor, termios.TIOCGWINSZ, '1234')
			height, width=struct.unpack('hh', data)
			return width, height
		finally:
			os.close(descriptor)
	except:
		pass

	try:
		stdout, stderr=subprocess.Popen(("stty", "size"), stdout=subprocess.PIPE).communicate()
		height, width=tuple(int(value) for value in stdout.split())
		return width, height
	except:
		pass

	try:
		height, width=tuple(int(os.getenv(value)) for value in ("LINES", "COLUMNS"))
		return width, height
	except:
		pass

	return sys.maxint, sys.maxint

def get_console_width():
	# sys.stdout.isatty()
	if sys.platform.startswith("win"):
	    width, height=get_windows_console_size()
	    return width
	elif sys.platform.startswith("freebsd") or sys.platform.startswith("linux"):
		width, height=get_linux_console_size()
	else:
		return sys.maxint


width=get_console_width()
