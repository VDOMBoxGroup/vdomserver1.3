import os, re, socket, sys
import shlex, subprocess


def reinit_network():
	f = os.popen("/bin/sh /opt/boot/networkconfig.sh")
	outp = f.read()
	f.close()

rexp = re.compile(r"inet addr:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*Mask:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", re.IGNORECASE | re.DOTALL)

def get_ip_and_mask(interface = "eth0"):
	# return (ip, mask)
	try:
		f = os.popen("ifconfig %s"%interface)
		outp = f.read()
		f.close()
		ret = rexp.search(outp, 0)
		if ret and ret.group():
			the_ip = ret.group(1)
			the_mask = ret.group(2)
			return (the_ip, the_mask)
	except Exception, e:
		debug("Error: " + str(e))
	return (None, None)


def set_ip_and_mask(ip, mask):
	f = open("/etc/opt/ip", "w")
	f.write(ip)
	f.close()
	f = open("/etc/opt/mask", "w")
	f.write(mask)
	f.close()
	reinit_network()

rexp1 = re.compile(r"^0\.0\.0\.0\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", re.IGNORECASE | re.DOTALL | re.MULTILINE)

def get_default_gateway():
	try:
		f = os.popen("netstat -rn")
		outp = f.read()
		f.close()
		ret = rexp1.search(outp, 0)
		if ret and ret.group():
			gate = ret.group(1)
			return gate
	except Exception, e:
		debug("Error: " + str(e))
	return None

def set_default_gateway(gate):
	try:
		f = open("/etc/opt/gateway", "w")
		f.write(gate)
		f.close()
		reinit_network()
	except Exception, e:
		debug("Error: " + str(e))

def get_dns():
	pdns = sdns = ""
	try:
		f = open("/etc/resolv.conf", "rt")
		data = f.read()
		f.close()
		x = data.splitlines()
		if len(x) > 0:
			pdns = x[0]
			if pdns.startswith("nameserver"):
				pdns = pdns[10:].strip()
			else:
				pdns = ""
		if len(x) > 1:
			sdns = x[1]
			if sdns.startswith("nameserver"):
				sdns = sdns[10:].strip()
			else:
				sdns = ""
	except Exception, e:
		debug("get_dns: " + str(e))
	return (pdns, sdns)

def set_dns(pdns, sdns):
	try:
		a = b = ""
		if pdns:
			a = "nameserver " + pdns
		if sdns:
			b = "nameserver " + sdns
		f = open("/etc/resolv.conf", "wt")
		f.write("\n".join([a, b]))
		f.close()
	except Exception, e:
		debug("Error: " + str(e))

def get_date_and_time():
	try:
		f = os.popen('date "+%Y%m%d%H%M.%S"')
		outp = f.read()
		f.close()
		outp = outp.strip()
		if 15 == len(outp):
			the_date = "%s.%s.%s %s:%s" % (outp[:4], outp[4:6], outp[6:8], outp[8:10], outp[10:])
			return the_date
	except Exception, e:
		debug("Error: " + str(e))
	return None

def vdom_df():
	"HDD info in megabytes"
	f = os.popen("/opt/boot/hdddev_info.sh")
	(size, used, free, percent) = f.readlines()
	f.close()
	return (size, used, free, percent)


def get_free_space():
	try:
		(size, used, free, percent) = vdom_df()
		return int(free)/1024.0
	except Exception, e:
		debug("Error: " + str(e))
	return 0

def get_hd_size():
	try:
		(size, used, free, percent) = vdom_df()
		return int(size)/1024.0
	except Exception, e:
		debug("Error: " + str(e))
	return 0

def get_external_drives():
	outp = subprocess.check_output(["/opt/boot/externaldrives.sh"])
	lines = outp.strip().split("\n")
	return [ { "device": line.split(';', 1)[0],
		"label": line.split(';', 1)[1].strip() }  for line in lines ]

def device_exists(dev):
	return os.path.exists(dev)

def mount_device(dev):
	"""returns mountpoint of the device. raise CalledProcessError if can't"""
	outp = subprocess.check_output(["/opt/boot/mountpoint.sh", dev])
	return outp.strip()

def umount_device(dev):
	outp = subprocess.check_output(["umount", dev])
	return outp.strip()

def get_vfs_users():
	r = []
	f = os.popen("/sbin/vfs_users")
	userlist = f.read()
	f.close()
	ll = userlist.splitlines()
	for s in ll:
		i = s.find(":")
		if i < 0: i = len(s)
		r.append(s[:i])
	return r

