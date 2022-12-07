# Example Package

## Introduction

AMAP is command line interface tool similar to the famous NMAP. It scans an IP address or domain name to find active ports and related information.

It uses FOFA AMAP API to implement the function.

## Usage & Options

In your Python program entry

```python
# entry.py
from amap import amap

if __name__ == '__main__':
    amap()
```

In your command line

```bash
python entry.py 8.8.8.8
```

Usage:

  amap <ip_address_or_domain_name> [options]

Options:

  -h --help  Show help information

  -n --nmap  Use nmap tool to scan

## Information

* Python version >= 3.7 is required to run `subprocess.run()`
* Package `docopt` is required as a CLI builder