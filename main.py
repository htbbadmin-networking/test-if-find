#!/usr/bin/python3


'''
Assumptions:


'''

import os
import re
import sys
import socket
import argparse
import subprocess
from getpass import getpass

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="SSH Username")
    parser.add_argument("-i", "--target-ip", help="Target IP Address")
    parser.add_argument("-m", "--max-hops", help="Maximum TTL", default=8)
    args = parser.parse_args()
    args_dict = args.__dict__
    for key in args_dict.keys():
        if args_dict[key] == None:
            newvalue = input("Please specify " + key + ": ")
            setattr(args, key, newvalue)
    return args

def trace(addr, max_hops):
    command = "tracepath -m " + str(max_hops) + " " + addr
    path = subprocess.check_output(command, shell=True)
    return path

def parse_path(path, target_ip):
    path = path.decode().split("\n")
    path.reverse()
    path.remove("     Resume: pmtu 1500 ")
    path.remove("     Too many hops: pmtu 1500")
    new_path = []
    for line in path:
        if 'no reply' not in line and target_ip not in line:
            new_path.append(line)
    return new_path

def main():
    args = get_args()
    target_ip = args.target_ip
    username = args.username
    max_hops = args.max_hops
    #password = getpass('Enter SSH Password: ')
    path = trace(target_ip, max_hops)
    path = parse_path(path, target_ip)
    last_hop = path[1]
    ip = re.compile('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
    test = ip.search(last_hop)
    print(test.group())

if __name__ == '__main__':
    main()
