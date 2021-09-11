import subprocess as sb
import sys

from random import sample, randint, choice
from utility import get_chord_index

assert len(sys.argv) == 2 and sys.argv[1].isdigit() ,\
"Wrong useage!\n Correct useage: 'python3 setup.py <num_nodes>'"

DO_TESTS = True
NUM_NODES = int(sys.argv[1])
MODULO = 512

#Get all available nodes
#available_nodes = sb.run("/share/apps/ifi/available-nodes.sh", capture_output=True).stdout.decode()
available_nodes = sb.run(["cat", "nodes.txt"], capture_output=True).stdout.decode()
available_nodes = available_nodes.split("\n")
print(f"{len(available_nodes)} available nodes\n")


#Pick NUM_NODES random nodes
org_chord_nodes = sample(available_nodes, NUM_NODES)
print(f"We are using this/these nodes:\n{org_chord_nodes}\n")

#Give the nodes an index in the chord node using hashing, and a random portnumber. Then sort it after increasing hash
chord_nodes = [(node, get_chord_index(node, MODULO), randint(49152, 65535)) for node in org_chord_nodes]
chord_nodes = sorted(chord_nodes, key=lambda tup: tup[1])

#Visualize the chord ring:
print(f"Chord ring layout: name:port (index)")
for node in chord_nodes:
	print(f"{node[0]}:{node[2]} ({node[1]})->", end="")
print(f"{chord_nodes[0][0]}:{chord_nodes[0][2]} ({chord_nodes[0][1]})")


#Initialize the ditributed hash table
#Currently running without fingertable
#Had a problem using the "$PWD" command, so I opted to write the entire ptah instead
if NUM_NODES == 1:
	#sb.run(["ssh", "-f", chord_nodes[0][0], "python3", "$PWD/dummynode.py", "-p", str(randint(49152, 65535))])
	sb.run(["python3", "dummynode.py", "-p", str(chord_nodes[0][2])])
else:
	for i in range(len(chord_nodes)):
		prec = f"{chord_nodes[i-1][0]}:{chord_nodes[i-1][2]}"
		succ = f"{chord_nodes[(i+1)%NUM_NODES][0]}:{chord_nodes[(i+1)%NUM_NODES][2]}"
		sb.run(["ssh", "-f", chord_nodes[i][0], "python3", "ds1/starter_code/dummynode.py", "-p", str(chord_nodes[i][2]), prec, succ])

print("Done with setup!")		

if DO_TESTS:	
	node = choice(available_nodes)
	while node in org_chord_nodes:
		node = choice(available_nodes)

	connector_node = f"{chord_nodes[0][0]}:{chord_nodes[0][2]}"	

	print(f"Connecting to node {node}")
	sb.run(["ssh", "-f", node, "python3", "ds1/starter_code/test.py", connector_node])


    	


