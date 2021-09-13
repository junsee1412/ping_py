import os
import threading
import zlib
def run():
    return 1,2,3,4,5

# for i in run():
#     print(i)
thread_id = threading.get_native_id() if hasattr(threading, 'get_native_id') else threading.currentThread().ident 
process_id = os.getpid()
icmp_id = zlib.crc32("{}{}".format(process_id, thread_id).encode()) & 0xffff

print("hahah {:.1f}".format(icmp_id))
try:
    x = input('Enter a number in the range 1-10: ')
    if x<1 or x>10:
        raise Exception
    print( 'Great! You listened to me and entered a valid number')
 
except:
    print( 'Your number seems to be outside the range 1-10')