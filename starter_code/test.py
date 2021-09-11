import http.client
import sys

assert len(sys.argv) == 2 and type(sys.argv[1]) == str, \
"Wrong useage!\nCorrect useage: python3 test.py <node>"

start_node = sys.argv[1]

#Simple PUT request
def test1():
    key = "test_key"
    val = "OK"
    print(start_node)
    
    conn = http.client.HTTPConnection(start_node)
    conn.request("PUT", "/storage/"+key, val)
    resp = conn.getresponse()
    if resp.status != 200:
        print("Test 1 failed. Got status code {resp.status}")    

    print("Test 1 OK")



if __name__ == "__main__":
    print("Doing tests")
    test1()





