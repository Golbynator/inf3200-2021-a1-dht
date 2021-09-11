#!/usr/bin/env python3
import argparse
import json
import re
import signal
import socket
import socketserver
import threading
import http.client

from http.server import BaseHTTPRequestHandler,HTTPServer
from utility import get_chord_index, get_ipaddr, contained

#Change the modulo dynamically later!
# get_chord_index(socket.gethostname(), 512)
CHORD_INDEX = get_chord_index(socket.gethostname(), 512)
print(socket.gethostname())
print(CHORD_INDEX)
SUCCESSOR = None
PREDECESSOR = None

object_store = {}
neighbors = []



def find_successor(index):
    if contained(PREDECESSOR[1], CHORD_INDEX, index):
        return CHORD_INDEX
    else:
        return SUCCESSOR[1]

         
class NodeHttpHandler(BaseHTTPRequestHandler):

    def send_whole_response(self, code, content, content_type="text/plain"):

        if isinstance(content, str):
            content = content.encode("utf-8")
            if not content_type:
                content_type = "text/plain"
            if content_type.startswith("text/"):
                content_type += "; charset=utf-8"
        elif isinstance(content, bytes):
            if not content_type:
                content_type = "application/octet-stream"
        elif isinstance(content, object):
            content = json.dumps(content, indent=2)
            content += "\n"
            content = content.encode("utf-8")
            content_type = "application/json"

        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.send_header('Content-length',len(content))
        self.end_headers()
        self.wfile.write(content)

    def extract_key_from_path(self, path):
        return re.sub(r'/storage/?(\w+)', r'\1', path)

    def do_PUT(self):
        content_length = int(self.headers.get('content-length', 0))

        key = self.extract_key_from_path(self.path)
        value = self.rfile.read(content_length)

        print(f"This is the index:{get_chord_index(key, 512)} of the key:{key}")
        print(find_successor(get_chord_index(key, 512)))

        key_index = get_chord_index(key, 512)
        key_successor = find_successor(key_index)

        if key_successor == CHORD_INDEX:
            object_store[key] = value
        else:
            #Do a request
           
            if CHORD_INDEX == 80:
                print("hiohiojoi")
                exit()
           
            print(SUCCESSOR[0])
            
            conn = http.client.HTTPConnection(SUCCESSOR[0])
            conn.request("PUT", "/storage/"+key, value)
            #Do something about bad statuses
            resp = conn.getresponse()
            print(resp.status)

        #Send OK response
        print("er her")
        self.send_whole_response(200, "Value stored for " + key)    

            


    def do_GET(self):
        if self.path.startswith("/storage"):
            key = self.extract_key_from_path(self.path)

            key_index = get_chord_index(key, 512)
            key_successor = find_successor(key_index)

            if key_successor == CHORD_INDEX:
                #We are the sucessor
                if key in object_store:
                    self.send_whole_response(200, object_store[key])
                else:
                    self.send_whole_response(404,
                            "No object with key '%s' on this node" % key)
            else:
                #Forward the request
                conn = http.client.HTTPConnection(SUCCESSOR[0])
                
                #Do something about bad statuses
                resp = conn.getresponse()
                if resp.status == 200:
                    value = resp.read()
                    self.send_whole_response(200, value)        

        elif self.path.startswith("/neighbors"):
            self.send_whole_response(200, neighbors)

        else:
            self.send_whole_response(404, "Unknown path: " + self.path)

def arg_parser():
    PORT_DEFAULT = 8000
    #CHAAAAAANGE THIS
    DIE_AFTER_SECONDS_DEFAULT = 20 * 2
    parser = argparse.ArgumentParser(prog="node", description="DHT Node")

    parser.add_argument("-p", "--port", type=int, default=PORT_DEFAULT,
            help="port number to listen on, default %d" % PORT_DEFAULT)

    parser.add_argument("--die-after-seconds", type=float,
            default=DIE_AFTER_SECONDS_DEFAULT,
            help="kill server after so many seconds have elapsed, " +
                "in case we forget or fail to kill it, " +
                "default %d (%d minutes)" % (DIE_AFTER_SECONDS_DEFAULT, DIE_AFTER_SECONDS_DEFAULT/60))

    parser.add_argument("neighbors", type=str, nargs="*",
            help="addresses (host:port) of neighbour nodes")

    return parser

class ThreadingHttpServer(HTTPServer, socketserver.ThreadingMixIn):
    pass

def run_server(args):
    global server
    global neighbors
    global SUCCESSOR
    global PREDECESSOR
    server = ThreadingHttpServer(('', args.port), NodeHttpHandler)
    neighbors = args.neighbors
    #Maybe get Chord index of neighbors
    #Remember to node hash port number. Maybe need change setup.py to hash node + port
    PREDECESSOR = (neighbors[0], get_chord_index(neighbors[0].split(":")[0], 512))
    SUCCESSOR = (neighbors[1], get_chord_index(neighbors[1].split(":")[0], 512))
    print(PREDECESSOR, SUCCESSOR)

    def server_main():
        print("Starting server on port {}. Neighbors: {}".format(args.port, args.neighbors))
        server.serve_forever()
        print("Server has shut down")

    def shutdown_server_on_signal(signum, frame):
        print("We get signal (%s). Asking server to shut down" % signum)
        server.shutdown()

    # Start server in a new thread, because server HTTPServer.serve_forever()
    # and HTTPServer.shutdown() must be called from separate threads
    thread = threading.Thread(target=server_main)
    thread.daemon = True
    thread.start()

    # Shut down on kill (SIGTERM) and Ctrl-C (SIGINT)
    signal.signal(signal.SIGTERM, shutdown_server_on_signal)
    signal.signal(signal.SIGINT, shutdown_server_on_signal)

    # Wait on server thread, until timeout has elapsed
    #
    # Note: The timeout parameter here is also important for catching OS
    # signals, so do not remove it.
    #
    # Having a timeout to check for keeps the waiting thread active enough to
    # check for signals too. Without it, the waiting thread will block so
    # completely that it won't respond to Ctrl-C or SIGTERM. You'll only be
    # able to kill it with kill -9.
    thread.join(args.die_after_seconds)
    if thread.is_alive():
        print("Reached %.3f second timeout. Asking server to shut down" % args.die_after_seconds)
        server.shutdown()

    print("Exited cleanly")

if __name__ == "__main__":

    parser = arg_parser()
    args = parser.parse_args()
    run_server(args)
