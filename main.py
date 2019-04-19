#!/usr/bin/python3

import os
import re
import sys
import socket
import argparse
import subprocess

from getpass import getpass
from napalm import get_network_driver

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

def init_device(address, username):
    driver = get_network_driver('ios')
    password = getpass('Enter SSH Password: ')
    device = driver(address, username, password)
    print('Connecting to ' + address + '...')
    device.open()
    return device


def trace(addr, max_hops):
    print("Tracing path to " + addr)
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

    path = trace(target_ip, max_hops)
    path = parse_path(path, target_ip)
    last_hop = path[1]
    ip = re.compile('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
    test = ip.search(last_hop)
    last_hop = test.group()
    print("Last address in path: " + last_hop)
    connect = input("Connect to " + last_hop + "? (Y/n): ")
    if "yes" in connect.lower() or "y" in connect.lower():
        device = init_device(last_hop, username)
        command = "show ip route {}".format(target_ip)
        out = device._send_command(command)
        for line in out.split('\n'):
            if '*' in line:
                print(line)
    else:
        print("Bye...")

if __name__ == '__main__':
    main()
