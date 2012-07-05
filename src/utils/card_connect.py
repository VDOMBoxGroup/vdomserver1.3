import socket, time,__builtin__

def send_reply(msg, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.sendto(msg, ('localhost', int(port)))

def send_to_card(data):
	send_reply(data, VDOM_CONFIG["LOCALHOST-CARD-PORT"])


def send_to_card_and_wait( message, key, timeout = 1, delta = 0.1 ):
	"""Sends a message to sb-driver and waits for an option with a key"""
	if key in system_options:
		del system_options[key]
	send_to_card( message )
	cicle = 0
	while key not in system_options:
		cicle += 1
		if cicle * delta > timeout:
			return None
		time.sleep(delta)
	return system_options[key]



def get_system_attribute(part_type_attribute_id):
	return send_to_card_and_wait("getlicense 0 %s" % str(part_type_attribute_id),"0/%s" %str(part_type_attribute_id) )

def system_options_reinit():
	__builtin__.system_options = {"server_license_type": "0",	# online server, 1=development
	                              "firmware" : "N/A",
	                              "card_state" : "2",	# 0 - red, 1 - green, 2 - red blinkin, 3 - green blinking
	                              "object_amount" : "15000"}
	
	