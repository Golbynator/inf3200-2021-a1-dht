import http.client
import sys

assert len(sys.argv) == 2 and type(sys.argv[1]) == str, \
"Wrong useage!\nCorrect useage: python3 test.py <node>"

start_node = sys.argv[1]

#Simple PUT request
def put(key, val):
    print(start_node)
    
    conn = http.client.HTTPConnection(start_node)
    conn.request("PUT", "/storage/"+key, val)
    resp = conn.getresponse()
    if resp.status != 200:
        print(f"Failed to put value: '{val}' with key: '{key}'. Got status code {resp.status}")
        return

    print(f"Was able to PUT value: '{val}' with key:'{key}'")       


#Simple GET request
def get(key):
    conn = http.client.HTTPConnection(start_node)
    conn.request("GET", "/storage/"+key)
    
    resp = conn.getresponse()
    if resp.status != 200:
        print(f"Failed to get value: '{value}' with key: '{key}'. Got bad status code {resp.status}")
        return
  
    value = resp.read()
    value = value.decode()
    print(f"Retrieved value:'{value}' from key:'{key}' ")  


def put_test():
    key = "compute-3-16"
    val = "Test 1 value"
    put(key, val)

def get_test():
    key = "compute-3-16"
    get(key)

def change_val_test():
    key = "compute-3-16"
    val = "Changed value"
    put(key, val)
    get(key)


def colliding_keys_test():
    key = "compute-3-16"
    same_hash_key = "compute-6-54"
    val = "Just some nonesense"
    put(key, val)
    get(key)
    get(same_hash_key) 


if __name__ == "__main__":
    print("Doing tests")
    put_test()
    get_test()
    change_val_test()
    colliding_keys_test()
    





