import os
import time
import zlib
import errno
import socket
import struct
import platform
import threading

ip = ""
domain = ""

#ICMP echo 
ECHO_REPLY = 0
ECHO_REQUEST = 8

ICMP_HEADER_FORMAT = "!BBHHH"
ICMP_TIME_FORMAT = "!d"

IP_HEADER_FORMAT = "!BBHHHBBHII"

def checksum(source: bytes) -> int:
    BITS = 16 
    carry = 1 << BITS 
    result = sum(source[::2]) + (sum(source[1::2]) << (BITS // 2)) 
    while result >= carry: 
        result = sum(divmod(result, carry)) 
    return ~result & ((1 << BITS) - 1)

def read_icmp_header(raw: bytes) -> dict:
    icmp_header_keys = ('type', 'code', 'checksum', 'id', 'seq')
    return dict(zip(icmp_header_keys, struct.unpack(ICMP_HEADER_FORMAT, raw)))

def read_ip_header(raw: bytes) -> dict:
    def stringify_ip(ip: int) -> str:
        return ".".join(str(ip >> offset & 0xff) for offset in (24, 16, 8, 0)) 

    ip_header_keys = ('version', 'tos', 'len', 'id', 'flags', 'ttl', 'protocol', 'checksum', 'src_addr', 'dest_addr')
    ip_header = dict(zip(ip_header_keys, struct.unpack(IP_HEADER_FORMAT, raw)))
    ip_header['src_addr'] = stringify_ip(ip_header['src_addr'])
    ip_header['dest_addr'] = stringify_ip(ip_header['dest_addr'])
    return ip_header


def send_packet(sock: socket, dest_addr: str, icmp_id: int, seq: int, size: int):
    pseudo_checksum = 0 
    icmp_header = struct.pack(ICMP_HEADER_FORMAT, ECHO_REQUEST, 0, pseudo_checksum, icmp_id, seq)

    padding = (size - struct.calcsize(ICMP_TIME_FORMAT)) * "Q"
    icmp_payload = struct.pack(ICMP_TIME_FORMAT, time.time()) + padding.encode()
    real_checksum = checksum(icmp_header + icmp_payload)
    icmp_header = struct.pack(ICMP_HEADER_FORMAT, ECHO_REQUEST, 0, socket.htons(real_checksum), icmp_id, seq)
    packet = icmp_header + icmp_payload
    sock.sendto(packet, (dest_addr, 0))

def receive_packet(sock: socket, icmp_id: int, seq: int, timeout: int):
    has_ip_header = (os.name != 'posix') or (platform.system() == 'Darwin') or (sock.type == socket.SOCK_RAW)
    if has_ip_header:
        ip_header_slice = slice(0, struct.calcsize(IP_HEADER_FORMAT))
        icmp_header_slice = slice(ip_header_slice.stop, ip_header_slice.stop + struct.calcsize(ICMP_HEADER_FORMAT))
    else:
        icmp_header_slice = slice(0, struct.calcsize(ICMP_HEADER_FORMAT))
    

    while True:
        recv_data, addr = sock.recvfrom(1500)
        time_recv = time.time()

        icmp_header_raw, icmp_payload_raw = recv_data[icmp_header_slice], recv_data[icmp_header_slice.stop:]
        icmp_header = read_icmp_header(icmp_header_raw)

        if not has_ip_header:
            icmp_id = sock.getsockname()[1] 
       
        if icmp_header['id'] and icmp_header['id'] != icmp_id: 
            continue
      
        if icmp_header['id'] and icmp_header['seq'] == seq:
            if icmp_header['type'] == ECHO_REQUEST: 
                continue
            if icmp_header['type'] == ECHO_REPLY:
                time_sent = struct.unpack(ICMP_TIME_FORMAT, icmp_payload_raw[0:struct.calcsize(ICMP_TIME_FORMAT)])[0]
                return time_recv - time_sent 


def ping(ip, domain, count, ttl, size, timeout, tstep):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError as err:
        if err.errno == errno.EPERM: 
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
        else:
            raise err
    with sock:
        if ttl:
            try: 
                if sock.getsockopt(socket.IPPROTO_IP, socket.IP_TTL):
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            except OSError as err:
                print(err)
            try:
                if sock.getsockopt(socket.SOL_IP, socket.IP_TTL):
                    sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            except OSError as err:
                print(err)
        
        thread_id = threading.get_native_id() if hasattr(threading, 'get_native_id') else threading.currentThread().ident
        process_id = os.getpid()
        icmp_id = zlib.crc32("{}{}".format(process_id, thread_id).encode()) & 0xffff 
        
        icmp_seq = 1
        while count>=icmp_seq:
            try:
                send_packet(sock=sock, dest_addr=ip, icmp_id=icmp_id, seq=icmp_seq, size=size)
                delay = receive_packet(sock=sock, icmp_id=icmp_id, seq=icmp_seq, timeout=timeout) * 1000
            except:
                print(err)
                return
            ping_body_str = "{} bytes from {} ({}): icmp_seq={} ttl={} time={:.1f} ms".format(
                size, domain, ip, icmp_seq, ttl, delay)
            print(ping_body_str)

            icmp_seq+=1
            time.sleep(tstep)

def startup(domain_ip, count, ttl, timeout, size, tstep):
    try:
        ip = socket.gethostbyname(domain_ip)
    except socket.gaierror as err:
        print(err)
        return 0
    try:
        domain = socket.gethostbyaddr(domain_ip)[0]
    except:
        domain = ""

    ping_start_str = "PING {} ({} ({})) {} data bytes".format(domain_ip, domain, ip, size)
    print(ping_start_str)
    ping(ip, domain, count, ttl, size, timeout, tstep)