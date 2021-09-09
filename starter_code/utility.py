import hashlib
import socket

def get_ipaddr(hostname=socket.gethostname()):
	return socket.gethostbyname(hostname)

def get_chord_index(val, chord_ring_size):
	hashed_val = hashlib.sha1(val.encode()).hexdigest()
	return int(hashed_val, 16) % chord_ring_size

def contained(start, end, val):
	if start <= end:
		return val > start and val <= end
	else:
		return val > start or val <= end	
