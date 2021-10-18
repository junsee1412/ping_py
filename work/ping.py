import os
import socket
import struct
import select
import time
import platform
import zlib
import threading
import errno

from . import errors
from .enums import ICMP_DEFAULT_CODE, IcmpType, IcmpTimeExceededCode, IcmpDestinationUnreachableCode

DEBUG = False  # DEBUG: Show debug info for developers. (default False)
EXCEPTIONS = False  # EXCEPTIONS: Raise exception when delay is not available.
LOGGER = None  # LOGGER: Record logs into console or file.

IP_HEADER_FORMAT = "!BBHHHBBHII"
ICMP_HEADER_FORMAT = "!BBHHH"  # According to netinet/ip_icmp.h. !=network byte order(big-endian), B=unsigned char, H=unsigned short
ICMP_TIME_FORMAT = "!d"  # d=double
SOCKET_SO_BINDTODEVICE = 25  # socket.SO_BINDTODEVICE


def _raise(err):
    if EXCEPTIONS:
        raise err


def checksum(source: bytes) -> int:
    BITS = 16  # 16-bit long
    carry = 1 << BITS  # 0x10000
    result = sum(source[::2]) + (sum(source[1::2]) << (BITS // 2))  # Even bytes (odd indexes) shift 1 byte to the left.
    while result >= carry:  # Ones' complement sum.
        result = sum(divmod(result, carry))  # Each carry add to right most bit.
    return ~result & ((1 << BITS) - 1)  # Ensure 16-bit


def read_icmp_header(raw: bytes) -> dict:
    icmp_header_keys = ('type', 'code', 'checksum', 'id', 'seq')
    return dict(zip(icmp_header_keys, struct.unpack(ICMP_HEADER_FORMAT, raw)))


def read_ip_header(raw: bytes) -> dict:
    def stringify_ip(ip: int) -> str:
        return ".".join(str(ip >> offset & 0xff) for offset in (24, 16, 8, 0))  # str(ipaddress.ip_address(ip))

    ip_header_keys = ('version', 'tos', 'len', 'id', 'flags', 'ttl', 'protocol', 'checksum', 'src_addr', 'dest_addr')
    ip_header = dict(zip(ip_header_keys, struct.unpack(IP_HEADER_FORMAT, raw)))
    ip_header['src_addr'] = stringify_ip(ip_header['src_addr'])
    ip_header['dest_addr'] = stringify_ip(ip_header['dest_addr'])
    return ip_header


def send_one_ping(sock: socket, dest_addr: str, icmp_id: int, seq: int, size: int):
    try:
        dest_addr = socket.gethostbyname(dest_addr)  # Domain name will translated into IP address, and IP address leaves unchanged.
    except socket.gaierror as err:
        raise errors.HostUnknown(dest_addr) from err
    pseudo_checksum = 0  # Pseudo checksum is used to calculate the real checksum.
    icmp_header = struct.pack(ICMP_HEADER_FORMAT, IcmpType.ECHO_REQUEST, ICMP_DEFAULT_CODE, pseudo_checksum, icmp_id, seq)
    padding = (size - struct.calcsize(ICMP_TIME_FORMAT)) * "Q"  # Using double to store current time.
    icmp_payload = struct.pack(ICMP_TIME_FORMAT, time.time()) + padding.encode()
    real_checksum = checksum(icmp_header + icmp_payload)  # Calculates the checksum on the dummy header and the icmp_payload.

    icmp_header = struct.pack(ICMP_HEADER_FORMAT, IcmpType.ECHO_REQUEST, ICMP_DEFAULT_CODE, socket.htons(real_checksum), icmp_id, seq)  # Put real checksum into ICMP header.
    packet = icmp_header + icmp_payload
    sock.sendto(packet, (dest_addr, 0))  # addr = (ip, port). Port is 0 respectively the OS default behavior will be used.


def receive_one_ping(sock: socket, icmp_id: int, seq: int, timeout: int) -> float:
    has_ip_header = (os.name != 'posix') or (platform.system() == 'Darwin') or (sock.type == socket.SOCK_RAW)  # No IP Header when unprivileged on Linux.
    if has_ip_header:
        ip_header_slice = slice(0, struct.calcsize(IP_HEADER_FORMAT))  # [0:20]
        icmp_header_slice = slice(ip_header_slice.stop, ip_header_slice.stop + struct.calcsize(ICMP_HEADER_FORMAT))  # [20:28]
    else:
        icmp_header_slice = slice(0, struct.calcsize(ICMP_HEADER_FORMAT))  # [0:8]
    timeout_time = time.time() + timeout  # Exactly time when timeout.
    while True:
        timeout_left = timeout_time - time.time()  # How many seconds left until timeout.
        timeout_left = timeout_left if timeout_left > 0 else 0  # Timeout must be non-negative
        selected = select.select([sock, ], [], [], timeout_left)  # Wait until sock is ready to read or time is out.
        if selected[0] == []:  # Timeout
            raise errors.Timeout(timeout)
        time_recv = time.time()
        recv_data, addr = sock.recvfrom(1500)  # Single packet size limit is 65535 bytes, but usually the network packet limit is 1500 bytes.
        if has_ip_header:
            ip_header_raw = recv_data[ip_header_slice]
            ip_header = read_ip_header(ip_header_raw)
        icmp_header_raw, icmp_payload_raw = recv_data[icmp_header_slice], recv_data[icmp_header_slice.stop:]
        icmp_header = read_icmp_header(icmp_header_raw)
        if not has_ip_header:  # When unprivileged on Linux, ICMP ID is rewrited by kernel.
            icmp_id = sock.getsockname()[1]  # According to https://stackoverflow.com/a/14023878/4528364
        if icmp_header['id'] and icmp_header['id'] != icmp_id:  # ECHO_REPLY should match the ID field.
            continue
        if icmp_header['type'] == IcmpType.TIME_EXCEEDED:  # TIME_EXCEEDED has no icmp_id and icmp_seq. Usually they are 0.
            if icmp_header['code'] == IcmpTimeExceededCode.TTL_EXPIRED:
                raise errors.TimeToLiveExpired()  # Some router does not report TTL expired and then timeout shows.
            raise errors.TimeExceeded()
        if icmp_header['type'] == IcmpType.DESTINATION_UNREACHABLE:  # DESTINATION_UNREACHABLE has no icmp_id and icmp_seq. Usually they are 0.
            if icmp_header['code'] == IcmpDestinationUnreachableCode.DESTINATION_HOST_UNREACHABLE:
                raise errors.DestinationHostUnreachable()
            raise errors.DestinationUnreachable()
        if icmp_header['id'] and icmp_header['seq'] == seq:  # ECHO_REPLY should match the SEQ field.
            if icmp_header['type'] == IcmpType.ECHO_REQUEST:  # filters out the ECHO_REQUEST itself.
                continue
            if icmp_header['type'] == IcmpType.ECHO_REPLY:
                time_sent = struct.unpack(ICMP_TIME_FORMAT, icmp_payload_raw[0:struct.calcsize(ICMP_TIME_FORMAT)])[0]
                return time_recv - time_sent


def ping(dest_addr: str, timeout: int = 4, unit: str = "s", src_addr: str = None, ttl: int = None, seq: int = 0, size: int = 56, interface: str = None) -> float:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError as err:
        if err.errno == errno.EPERM:  # [Errno 1] Operation not permitted
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
        else:
            raise err
    with sock:
        if ttl:
            try:  # IPPROTO_IP is for Windows and BSD Linux.
                if sock.getsockopt(socket.IPPROTO_IP, socket.IP_TTL):
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            except OSError as err:
                print("Set Socket Option `IP_TTL` in `IPPROTO_IP` Failed: {}".format(err))
            try:
                if sock.getsockopt(socket.SOL_IP, socket.IP_TTL):
                    sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            except OSError as err:
                print("Set Socket Option `IP_TTL` in `SOL_IP` Failed: {}".format(err))
        if interface:
            sock.setsockopt(socket.SOL_SOCKET, SOCKET_SO_BINDTODEVICE, interface.encode())  # packets will be sent from specified interface.
        if src_addr:
            sock.bind((src_addr, 0))  # only packets send to src_addr are received.
        thread_id = threading.get_native_id() if hasattr(threading, 'get_native_id') else threading.currentThread().ident  # threading.get_native_id() is supported >= python3.8.
        process_id = os.getpid()  # If ping() run under different process, thread_id may be identical.
        icmp_id = zlib.crc32("{}{}".format(process_id, thread_id).encode()) & 0xffff  # to avoid icmp_id collision.
        try:
            send_one_ping(sock=sock, dest_addr=dest_addr, icmp_id=icmp_id, seq=seq, size=size)
            delay = receive_one_ping(sock=sock, icmp_id=icmp_id, seq=seq, timeout=timeout)  # in seconds
        except errors.Timeout as err:
            _raise(err)
            return None
        except errors.PingError as err:
            _raise(err)
            return False
        if delay is None:
            return None
        if unit == "ms":
            delay *= 1000  # in milliseconds
        return delay