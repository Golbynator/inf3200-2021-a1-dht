import hashlib
import socket
from math import log2

MODULO = 512

test_nodes = ["compute-6-12", "compute-1-1", "compute-6-15", "compute-6-37", "compute-6-44", "compute-6-29", "compute-6-41", "compute-6-36",
"compute-6-33", "compute-6-9", "compute-6-49", "compute-6-38", "compute-8-7", "compute-3-19", "compute-3-4", "compute-0-0"]

def get_machine_name():
	name = socket.gethostname()

	if "compute" in name:
		name = name.split(".")
		name = name[0]

	return name	
		

def get_chord_index(val, chord_ring_size):
	hashed_val = hashlib.sha1(val.encode()).hexdigest()
	return int(hashed_val, 16) % chord_ring_size

def contained(start, end, val):
	if start <= end:
		return val > start and val <= end
	else:
		return val > start or val <= end


def generate_finger_table(node_index, neighbour_indice):
    table = []
	length_of_table = int(log2(MODULO))

	neighbour_iter = iter(neighbour_indice)
	neighbour_index = next(neighbour_iter)
	for i in range(length_of_table):
		succ_index = (node_index + 2**i) % MODULO

		while(not contained(node_index, neighbour_index, succ_index)):
			neighbour_index = next(neighbour_iter)

		table.append(neighbour_index)

	return table		
		 
		


