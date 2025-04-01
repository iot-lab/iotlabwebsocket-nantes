#!/usr/bin/env python3
"""Test script to verify HTTP proxy connection."""

import os
import sys
import urllib.request
import socket

# Get proxy from environment or command line
proxy = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
print("Using proxy: {}".format(proxy))

if not proxy:
    print("No proxy configured. Please set http_proxy environment variable or provide as argument.")
    sys.exit(1)

# Configure proxy for urllib
proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

print("Attempting to connect to www.iot-lab.info through proxy...")
try:
    # Make a request through the proxy
    response = urllib.request.urlopen('https://www.iot-lab.info', timeout=10)
    print("Connection successful! Status code: {}".format(response.status))
    print("Response headers: {}".format(response.headers))
    
    # Also try to directly connect to the proxy to verify connectivity
    proxy_host = proxy.replace('http://', '').split(':')[0]
    proxy_port = int(proxy.replace('http://', '').split(':')[1]) if ':' in proxy else 3128
    
    print("Attempting direct connection to proxy {}:{}...".format(proxy_host, proxy_port))
    sock = socket.socket()
    sock.settimeout(5)
    sock.connect((proxy_host, proxy_port))
    sock.close()
    print("Direct connection to proxy successful!")
    
    print("\nProxy is properly configured and working!")
except Exception as e:
    print("Connection failed: {}".format(e))
    print("\nProxy may not be properly configured or accessible.")
    sys.exit(1)