import subprocess as sb
import sys

from random import sample, randint
from utility import get_chord_index



assert len(sys.argv) == 2 and sys.argv[1].isdigit() ,\
"Wrong useage!\n Correct useage: 'python3 setup.py <num_nodes>'"


NUM_NODES = int(sys.argv[1])
MODULO = 512

#Get all available nodes
#available_nodes = sb.run("/share/apps/ifi/available-nodes.sh", capture_output=True).stdout.decode()
available_nodes = sb.run(["cat", "nodes.txt"], capture_output=True).stdout.decode()
available_nodes = available_nodes.split("\n")
print(f"{len(available_nodes)} available nodes\n")


#Pick NUM_NODES random nodes
chord_nodes = sample(available_nodes, NUM_NODES) 
print(f"We are using this/these nodes:\n{chord_nodes}\n")

#Give the nodes an index in the chord node, using hashing. Then sort it after increasing hash
chord_nodes = [(node, get_chord_index(node, MODULO)) for node in chord_nodes]
chord_nodes = sorted(chord_nodes, key=lambda tup: tup[1])

#Visualize the chord ring:
print(f"Chord ring layout: name (index)")
for node in chord_nodes:
	print(f"{node[0]} ({node[1]})->", end="")
print(f"{chord_nodes[0][0]} ({chord_nodes[0][1]})")


#Initialize the ditributed hash table
#Currently running without fingertable
if NUM_NODES == 1:
	#sb.run(["ssh", "-f", chord_nodes[0], "python3", "dummynode.py", "-p", str(randint(49152, 65535))])
	sb.run(["python3", "dummynode.py", "-p", str(randint(49152, 65535))])
else:
	for i in range(len(chord_nodes)):
		prec = f"{chord_nodes[i-1][0]}:{randint(49152, 65535)}"
		succ = f"{chord_nodes[(i+1)%NUM_NODES][0]}:{randint(49152, 65535)}"
		#sb.run(["ssh", "-f", chord_nodes[i], "python3", "dummynode.py", "-p", str(randint(49152, 65535)), prec, succ])		




