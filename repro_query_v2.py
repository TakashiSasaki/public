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
    # Note: On Windows, joining on ANY might not work if there are multiple IPs.
    # But for a simple test it might.
    mreq = struct.pack("4sl", socket.inet_aton(MDNS_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    sock.settimeout(2)
    try:
        data, addr = sock.recvfrom(1024)
        print(f"SUCCESS: Received {len(data)} bytes from {addr}")
    except socket.timeout:
        print("FAILURE: Timed out waiting for packet")
    finally:
        sock.close()

def send():
    time.sleep(0.5)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # RFC 6762 mandates TTL 255
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
    
    payload = struct.pack("!HHHHHH", 0, 0, 1, 0, 0, 0) + b"\x04test\x05local\x00" + struct.pack("!HH", 1, 1)
    sock.sendto(payload, (MDNS_GROUP, MDNS_PORT))
    print("Sent query")
    sock.close()

t = threading.Thread(target=listen)
t.start()
send()
t.join()
