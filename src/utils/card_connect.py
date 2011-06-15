import socket, time

def send_reply(msg, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.sendto(msg, ('localhost', int(port)))

def send_to_card(data):
	send_reply(data, VDOM_CONFIG["LOCALHOST-CARD-PORT"])


def send_to_card_and_wait( message, key, timeout = 1, delta = 0.1 ):
	"""Sends a message to sb-driver and waits for an option with a key"""
	send_to_card( message )
	cicle = 0
	while key not in system_options:
		cicle += 1
		if cicle * delta > timeout:
			return None
		time.sleep(delta)
	return system_options[key]
