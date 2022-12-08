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
import time

from docopt import docopt
import socket
import subprocess
import json
from time import localtime, strftime
from xml.dom import minidom


def amap():
    arguments = docopt(__doc__)
    target_host = get_target_host(arguments)
    if arguments['--nmap']:
        nmap_output(target_host, arguments)
    else:
        amap_output(target_host, arguments)


def get_target_host(arguments):
    target_host = arguments['<ip_address_or_domain_name>']
    # Validation Judgement
    try:
        socket.getaddrinfo(target_host, None)
    except:
        print('Invalid IP address or domain name!')
        exit(1)
    return target_host


def nmap_output(target_host, arguments):
    if arguments['--xml']:
        filename = arguments['--xml']
        result = subprocess.run(["nmap", target_host, "-oX", filename], capture_output=True, text=True).stdout
    else:
        result = subprocess.run(["nmap", target_host], capture_output=True, text=True).stdout
    print(result)


def amap_output(target_host, arguments):
    start_time = time.time()
    result = json.loads(
        subprocess.run(["curl", "http://amap.fofa.info/" + target_host], capture_output=True, text=True).stdout)
    # Timeout
    i = 0
    while 'error' in result and i < 2:
        result = json.loads(
            subprocess.run(["curl", "http://amap.fofa.info/" + target_host], capture_output=True, text=True).stdout)
        i = i + 1
    end_time = time.time()
    execute_time = end_time - start_time
    standard_output = get_standard_output(result, execute_time)
    if arguments['--xml']:
        filename = arguments['--xml']
        output_to_xml(result, filename, start_time, end_time)
    print(standard_output)


def get_standard_output(result, execute_time):
    output = "Starting Amap 1.0.0 ( https://github.com/holydragon57/amap ) at " + \
             strftime("%Y-%m-%d %H:%M", localtime()) + " 中国标准时间\n" + \
             "Amap scan report for "
    if result['domain'] != '':
        output += result['domain'] + " (" + result['ip'] + ")\n"
    else:
        output += result['ip'] + "\n"
    output += "PORT\tSTATE\tSERVICE\n"
    ports = result['ports']
    for port in ports:
        output += str(port['port']) + "/" + port['base_protocol'] + "\topen\t" + port['protocol'] + '\n'
    output += "\nAmap done: 1 IP address (1 host up) scanned in " + str(round(execute_time, 2)) + " seconds\n"
    return output


def output_to_xml(result, filename, start_time, end_time):
    xml_file = minidom.Document()
    xml_file.insertBefore(minidom.DocumentType("nmaprun"), xml_file.documentElement)

    nmaprun = xml_file.createElement("nmaprun")
    startstr = strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
    nmaprun.setAttribute("scanner", "amap")
    nmaprun.setAttribute("start", str(round(start_time)))
    nmaprun.setAttribute("startstr", startstr)

    hosthint = xml_file.createElement("hosthint")

    host = xml_file.createElement("host")
    host.setAttribute("starttime", str(round(start_time)))
    host.setAttribute("endtime", str(round(end_time)))

    address = xml_file.createElement("address")
    address.setAttribute("addr", result['ip'])
    address.setAttribute("addrtype", "ipv4")
    hosthint.appendChild(address)
    host.appendChild(address.cloneNode(deep=True))

    if result['domain'] != "":
        hostnames = xml_file.createElement("hostnames")
        hostname = xml_file.createElement("hostname")
        hostname.setAttribute("name", result['domain'])
        hostnames.appendChild(hostname)
        hosthint.appendChild(hostnames)
        host.appendChild(hostnames.cloneNode(deep=True))

    nmaprun.appendChild(hosthint)

    ports = xml_file.createElement("ports")
    for port in result['ports']:
        port_element = xml_file.createElement("port")
        port_element.setAttribute("protocol", port['base_protocol'])
        port_element.setAttribute("portid", str(port['port']))
        state = xml_file.createElement("state")
        state.setAttribute("state", "open")
        port_element.appendChild(state)
        service = xml_file.createElement("service")
        service.setAttribute("name", port['protocol'])
        port_element.appendChild(service)
        ports.appendChild(port_element)
    host.appendChild(ports)

    nmaprun.appendChild(host)

    execute_time = round(end_time - start_time, 2)
    runstats = xml_file.createElement("runstats")

    timestr = strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
    finished = xml_file.createElement("finished")
    finished.setAttribute("time", str(round(end_time)))
    finished.setAttribute("timestr", timestr)
    finished.setAttribute("summary", "Amap done at " + timestr + "; 1 IP address (1 host up) scanned in " +
                          str(execute_time) + " seconds")
    finished.setAttribute("elapsed", str(execute_time))
    finished.setAttribute("exit", "success")

    hosts = xml_file.createElement("hosts")
    hosts.setAttribute("up", "1")
    hosts.setAttribute("down", "0")
    hosts.setAttribute("total", "1")
    runstats.appendChild(finished)
    runstats.appendChild(hosts)

    nmaprun.appendChild(runstats)

    xml_file.appendChild(nmaprun)

    filepath = "./" + filename
    fp = open(filepath, "w")
    xml_file.writexml(fp, addindent="   ", newl="\n", encoding="UTF-8")
