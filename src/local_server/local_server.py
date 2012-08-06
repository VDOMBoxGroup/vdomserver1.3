"""local server"""

import socket, sys, time, select, json, traceback

from utils.system import *
from utils.card_connect import send_to_card,send_to_card_and_wait
import managers



card_port = 4444
wait = 0


def wait_for_options():
	global wait
	if not (FREEBSD or LINUX):
		print ("Platform %s does not support a smart card. Need %s or %s. " % (sys.platform, LINUX, FREEBSD))
		return
	wait = 1

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.bind(('localhost', VDOM_CONFIG["SERVER-LOCALHOST-PORT"]))
	except Exception, e:
		return
	s.sendto("getoptions", ('localhost', card_port))

	debug("Waiting for options up to 10 seconds")
	while True:
		ret = select.select([s], [], [], 10.0)
		if len(ret[0]) > 0:
			(st, addr) = s.recvfrom(1024)
			try:
				execute(st)
			except:
				debug("Have got invalid options:%s from %s"%st)
				traceback.print_exc(file=debugfile)			
				break
		else:
			debug("Haven't got options within 10 seconds")
			break
		if not wait:
			debug("Have got options")
			debug("License is %s" % system_options["object_amount"])
			break

def send_option(name, value):
	send_to_card(" ".join(["option", name, value]))



def process_vcard(cmd, json_str):
	
	debug( json_str )
	param = json.loads(json_str)
	
	
	if cmd == "error":
		system_options["vcard_error"] = param
	elif cmd == "systemlist":
		system_options["vcard_systemlist"] = param


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




def send_pong():
	send_to_card("pong")


def run_scheduler_task(num):
	managers.scheduler_manager.on_signal(num.strip('\n'))


def execute(data):
	parts = data.split(" ", 2)
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
	elif "getauth" == parts[0]:
		send_option("auth", managers.user_manager.get_user_by_name("root").password)
	elif "scheduler_task" == parts[0]:
		run_scheduler_task(parts[1])
	elif "ping" == parts[0]:
		send_pong()
	elif "vcard" == parts[0]:
		vcard, cmd, json_str = parts
		process_vcard( cmd, json_str )



#Depricated
def check_application_license(application_id, license_type):
	return send_to_card_and_wait( 
	    "getlicense %s %s" % (str(application_id), str(license_type)),
	    "%s/%s" % (str(application_id), str(license_type)) ) == "1"