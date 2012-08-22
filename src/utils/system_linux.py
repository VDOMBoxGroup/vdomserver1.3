import os, re, socket, sys
import shlex, subprocess
import managers
from subprocess import CalledProcessError
rexp_ifconfig = re.compile(r"inet addr:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*Mask:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", re.IGNORECASE | re.DOTALL)
rexp_gateway = re.compile(r"^0\.0\.0\.0\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", re.IGNORECASE | re.DOTALL | re.MULTILINE)
rexp_hostname = re.compile(r"^[\w.-]+$")

def reinit_network():
	try:
		subprocess.check_call(["/bin/sh","/opt/boot/networkconfig.sh"])
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: Network reinit failed. %s"%str(e),"system_linux")
		
def get_ip_and_mask(interface = "eth0"):
	"""return (ip, mask)"""
	try:
		outp = subprocess.check_output(["ifconfig",str(interface)])
		ret = rexp_ifconfig.search(outp, 0)
		if ret and ret.group():
			the_ip = ret.group(1)
			the_mask = ret.group(2)
			return (the_ip, the_mask)
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
	return (None, None)


def set_ip_and_mask(ip, mask):
	f = open("/etc/opt/ip", "w")
	f.write(ip)
	f.close()
	f = open("/etc/opt/netmask", "w")
	f.write(mask)
	f.close()
	reinit_network()



def get_default_gateway():
	try:
		outp = subprocess.check_output(["netstat", "-rn"])
		ret = rexp_gateway.search(outp, 0)
		if ret and ret.group():
			gate = ret.group(1)
			return gate
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
	return None

def set_default_gateway(gate):
	try:
		f = open("/etc/opt/gateway", "w")
		f.write(gate)
		f.close()
		reinit_network()
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")

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
		managers.log_manager.error_server("System call error: Getting DNS failed. %s"%str(e),"system_linux")
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
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
		
def set_hostname(hostname):
	try:
		res = rexp_hostname.match(hostname)
		if res:
			f = open("/etc/hostname", "wt")
			f.write(hostname)
			f.close()
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
		
def get_hostname():
	data = ""
	try:
		f = open("/etc/hostname", "rt")
		data = f.read()
		f.close()
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
	return data

def set_proxy(addr, port, login="", password=""):
	try:
		f = open("/etc/opt/proxy", "w")
		lines = list((addr, port, login, password))
		data = "\n".join(lines) if lines else ""
		f.write(data)
		f.close()
	except Exception, e:
		debug("Error: " + unicode(e))
		managers.log_manager.error_server("System call error: %s"%unicode(e),"system_linux")
	
def get_proxy():
	addr = port = login = passwd = ""	
	try:
		f = open("/etc/opt/proxy", "r")
		data = f.read()
		f.close()
		if data:
			data = data.split("\n")
			addr = data[0]
			port = data[1] if len(data) > 1 else ""
			login = data[2] if len(data) > 2 else ""
			passwd = data[3] if len(data) > 3 else ""
	except Exception, e:
		debug("Error: " + unicode(e))
		managers.log_manager.error_server("System call error: %s"%unicode(e),"system_linux")
	return (addr, port, login, passwd)

def get_date_and_time():
	try:
		outp = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S'])
		return outp.strip()
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
	return None

def vdom_df():
	"HDD info in megabytes"
	outp = subprocess.check_output(["/opt/boot/hdddev_info.sh"])
	(size, used, free, percent) = outp.strip().split("\n")
	return (size, used, free, percent)


def get_free_space():
	try:
		(size, used, free, percent) = vdom_df()
		return int(free)/1024.0
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
	return 0

def get_hd_size():
	try:
		(size, used, free, percent) = vdom_df()
		return int(size)/1024.0
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
	return 0

def get_external_drives():
	try:
		outp = subprocess.check_output(["/opt/boot/externaldrives.sh"])
		lines = outp.strip().split("\n")
		return [ { "device": line.split(';', 1)[0],
		"label": line.split(';', 1)[1].strip() }  for line in lines if line ]
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
	return []

def device_exists(dev):
	return os.path.exists(dev)

def mount_device(dev):
	"""returns mountpoint of the device. raise CalledProcessError if can't"""
	try:
		outp = subprocess.check_output(["/opt/boot/mountpoint.sh", dev])
		return outp.strip()
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")

def umount_device(dev):
	try:
		outp = subprocess.check_output(["umount", dev])
		return outp.strip()
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")

def get_vfs_users():
	r = []
	try:
		userlist = subprocess.check_output(["/sbin/vfs_users"])
		ll = userlist.splitlines()
		for s in ll:
			i = s.find(":")
			if i < 0: i = len(s)
			r.append(s[:i])
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
	return r

def open_debug_port():
	try:
		subprocess.check_call(["/bin/sh","/opt/boot/vdom_debug_port_on_off.sh", "--on"])
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: Open port failed. %s"%str(e),"system_linux")
		
def close_debug_port():
	try:
		subprocess.check_call(["/bin/sh","/opt/boot/vdom_debug_port_on_off.sh", "--off"])
	except Exception, e:
		debug("Error: " + str(e))
		managers.log_manager.error_server("System call error: Close port failed. %s"%str(e),"system_linux")

def move(src, dst):
	try:
		subprocess.check_call(["mv", src, dst])
	except CalledProcessError, e:
		debug ("Error: return code: %s"%str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
		
def copy(src, dst):
	try:
		subprocess.check_call(["cp", src, dst])
	except CalledProcessError, e:
		debug ("Error: return code: %s"%str(e))
		managers.log_manager.error_server("System call error: %s"%str(e),"system_linux")
		