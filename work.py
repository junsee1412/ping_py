import socket
import struct
import time
import threading

# dest_addr = "vnpt.com.vn"
# dest_addr = "google.com"
ip = ""
domain = ""

def send_packet():
    return float(time.time_ns() / 100000)

def receive_packet():
    return float(time.time_ns() / 100000)

def ping(domain_ip, **kwargs):
    try:
        ip = socket.gethostbyname(domain_ip)
        domain = socket.gethostbyaddr(domain_ip)[0]
    except socket.gaierror as err:
        print(err)
        return 0

    size = kwargs.get("size")
    count = kwargs.get("count")
    ttl = kwargs.get("ttl")
    timeout = kwargs.get("timeout")

    icmp_seq = 1

    ping_start_str = "PING {domain_ip} ({domain} ({ip})) {size} data bytes".format(
        domain_ip = domain_ip, domain = domain, ip = ip, size = size)
    print(ping_start_str)

    while count>=icmp_seq:
        # send packet to target host
        send = float(time.time_ns() / 100000)
        time.sleep(0.0054)

        # receive packet from target host
        receive = receive_packet()
        # time_delay = receive - send
        time_delay = receive - send


        ping_body_str = "{size} bytes from {domain} ({ip}): icmp_seq={icmp_seq} ttl={ttl} time={time:.1f} ms".format(
            size = size, domain = domain, ip = ip, icmp_seq = icmp_seq, ttl = ttl, time = time_delay)
        print(ping_body_str)

        icmp_seq+=1
        time.sleep(1)
