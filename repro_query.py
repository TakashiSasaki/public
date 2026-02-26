import socket
import struct
import threading
import time

MDNS_GROUP = "224.0.0.251"
MDNS_PORT = 5353

def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", MDNS_PORT))
    
    # Join group
    mreq = struct.pack("4sl", socket.inet_aton(MDNS_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    print("Listener started...")
    while True:
        data, addr = sock.recvfrom(1024)
        print(f"Received {len(data)} bytes from {addr}")

def send():
    time.sleep(1)
    print("Sender starting...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Default TTL is 1, default LOOP is 1
    # Let's try sending a simple DNS query header (ID=0, QD=1)
    payload = struct.pack("!HHHHHH", 0, 0, 1, 0, 0, 0) + b"\x04test\x05local\x00" + struct.pack("!HH", 1, 1)
    sock.sendto(payload, (MDNS_GROUP, MDNS_PORT))
    print("Sent query")
    sock.close()

t = threading.Thread(target=listen, daemon=True)
t.start()
send()
time.sleep(2)
print("Done")
