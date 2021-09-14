# import os
# import threading
# import zlib
# import socket
# import random
# def run():
#     return ["hihi", "hahah"]

# # for i in run():
# #     print(i)
# ran = random.randint(0, 99999) & 0xffff
# thread_id = threading.get_native_id() if hasattr(threading, 'get_native_id') else threading.currentThread().ident 
# process_id = os.getpid()
# icmp_id = zlib.crc32("{}{}".format(process_id, thread_id).encode()) & 0xffff

# print("hahah {:.1f}, {}".format(socket.htons(icmp_id), icmp_id))
# print("random {:.1f} {}".format(socket.htons(ran), ran))
# print(run()[1])

a = "b'aabcabcabc'".split("'")
print(a[1])