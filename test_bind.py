import socket

multicast_ip = "224.0.0.251"
listen_port = 5353
target_ipv4 = socket.gethostbyname(socket.gethostname())

sock_m = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock_m.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    sock_m.bind((multicast_ip, listen_port))
    print("Bound to multicast IP")
except Exception as e:
    print("Failed to bind to multicast IP:", e)

sock_u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock_u.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    sock_u.bind((target_ipv4, listen_port))
    print("Bound to unicast IP")
except Exception as e:
    print("Failed to bind to unicast IP:", e)
