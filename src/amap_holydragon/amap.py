# coding:utf-8
"""
amap

Usage:
  amap [-h | --help]
  amap <ip_address_or_domain_name> [-n | --nmap] [-x <filename> | --xml=<filename>]

Options:
  -h --help  Show help information
  -n --nmap  Use nmap to scan
  -x <filename> --xml=<filename>  Output XML file

"""

from docopt import docopt
import socket
import subprocess
import json


def amap():
    arguments = docopt(__doc__)
    print(arguments)
    target_host = get_target_host(arguments)
    # if '--nmap' in arguments:
    #     nmap_output(target_host, arguments['<filename>'])
    # else:
    #     amap_output(target_host, arguments['<filename>'])


def get_target_host(arguments):
    target_host = arguments['<ip_address_or_domain_name>']
    # Validation Judgement
    try:
        socket.getaddrinfo(target_host, None)
    except:
        print('Invalid IP address or domain name!')
        exit(1)
    return target_host


def nmap_output(target_host, filename):
    if filename is None:
        result = subprocess.run(["nmap", target_host], capture_output=True, text=True).stdout
    else:
        result = subprocess.run(["nmap", target_host, "-oX", filename], capture_output=True, text=True).stdout
    print(result)



def amap_output(target_host, filename):
    result = json.loads(
        subprocess.run(["curl", "http://amap.fofa.info/" + target_host], capture_output=True, text=True).stdout)
    # Timeout
    i = 0
    while 'error' in result and i < 2:
        result = json.loads(
            subprocess.run(["curl", "http://amap.fofa.info/" + target_host], capture_output=True, text=True).stdout)
        i = i + 1
    print(result)

