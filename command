#!/usr/bin/env python

import argparse
import sys
import work

def main(assigned_args: list = None):
    parser = argparse.ArgumentParser(description='Packet InterNet Groper.')
    parser.add_argument(dest="dest_addr", metavar="<destination> ", type=str, default=(""), help="dns name or ip address")
    parser.add_argument("-c", dest="count", metavar="<count>", type=int, default=sys.maxsize, help="stop after <count> replies")
    parser.add_argument("-t", dest="ttl", metavar="<ttl>", type=int, default=64, help="define time to live")
    parser.add_argument("-w", dest="timeout", metavar="<timeout>", type=float, default=4, help="time to wait for response")
    parser.add_argument("-s", dest="size", metavar="<size>", type=int, default=56, help="use <size> as number of data bytes to be sent")

    args = parser.parse_args(assigned_args)
    # work.ping(args.dest_addr)
    work.startup(args.dest_addr, count=args.count, ttl=args.ttl, timeout=args.timeout, size=args.size)

main()