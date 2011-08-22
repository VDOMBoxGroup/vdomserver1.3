"""local server"""

import socket, sys, time, select

from utils.system import *

card_port = 4444
wait = 0

def send_reply(msg, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.sendto(msg, ('localhost', int(port)))

def send_to_card(data):
	send_reply(data, card_port)

def wait_for_options():
	global wait
	if not sys.platform.startswith("freebsd"):
		return
	wait = 1

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.bind(('localhost', VDOM_CONFIG["SERVER-LOCALHOST-PORT"]))
	except Exception, e:
		debug("Can't bind socket: %s" % str(e))
		return
	s.sendto("getoptions", ('localhost', card_port))

	debug("Waiting for options up to 10 seconds")
	while True:
		ret = select.select([s], [], [], 10.0)
		if len(ret[0]) > 0:
			(st, addr) = s.recvfrom(1024)
			execute(st)
		else:
			debug("Haven't got options within 10 seconds")
			break
		if not wait:
			debug("Have got options")
			debug("License is %s" % system_options["object_amount"])
			break

def send_option(name, value):
	send_to_card(" ".join(["option", name, value]))

def process_option(name, value):
	system_options[name] = value

def set_network():
	global wait
	if "server_ip" in system_options and "server_mask" in system_options and "server_router" in system_options:
		ip = system_options["server_ip"]
		mask = system_options["server_mask"]
		gw = system_options["server_router"]
		if ip is not "" and mask is not "":
			set_ip_and_mask(ip, mask)
			(_i, _m) = get_ip_and_mask()
			if _i == ip and _m == mask:
				f = open("/etc/ip", "w")
				f.write(ip + " netmask " + mask)
				f.close()
		if gw is not "":
			set_default_gateway(gw)
			_gw = get_default_gateway()
			if gw == _gw:
				f = open("/etc/gateway", "w")
				f.write(gw)
				f.close()
	if "server_pdns" in system_options and "server_sdns" in system_options:
		set_dns(system_options["server_pdns"], system_options["server_sdns"])
	wait = 0

def send_network():
	(ip, mask) = get_ip_and_mask()
	if ip and mask:
		send_option("server_ip", ip)
		send_option("server_mask", mask)
	gw = get_default_gateway()
	if gw:
		send_option("server_router", gw)
	pdns, sdns = get_dns()
	send_option("server_pdns", pdns)
	send_option("server_sdns", sdns)

def execute(data):
	parts = data.split(" ")
	if "option" == parts[0]:
		name = value = ""
		if len(parts) > 1:
			name = parts[1]
		if len(parts) > 2:
			value = parts[2]
		process_option(name, value)
	elif "options" == parts[0]:
		set_network()
	elif "getnetwork" == parts[0]:
		send_network()
