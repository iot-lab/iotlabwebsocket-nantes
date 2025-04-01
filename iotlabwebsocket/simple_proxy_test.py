#!/usr/bin/env python3
"""Simple HTTP proxy test using requests library."""

import os
import sys
import requests
import socket
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("proxy-test")

def test_proxy():
    """Test HTTP requests through proxy."""
    logger.info("Testing proxy connection...")
    
    # Get proxy from environment or use the provided one
    proxy = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY') or "http://172.20.12.74:3128"
    logger.info(f"Using proxy: {proxy}")
    
    # Setup proxy dict for requests
    proxies = {
        "http": proxy,
        "https": proxy
    }
    
    # Try to fetch something from an external URL
    try:
        logger.info("Sending HTTP request...")
        response = requests.get("https://www.iot-lab.info", proxies=proxies, timeout=10)
        logger.info(f"Connection successful! Response code: {response.status_code}")
        
        # Also test a second request to verify consistent behavior
        logger.info("Testing a second request...")
        response2 = requests.get("https://www.iot-lab.info/testbed/", proxies=proxies, timeout=10)
        logger.info(f"Second request successful! Response code: {response2.status_code}")
        
        print("\n✅ Proxy test successful - HTTP requests are using the proxy")
        return True
    except requests.exceptions.ProxyError as e:
        logger.error(f"Proxy connection failed: {str(e)}")
        print("\n❌ Proxy test failed - Could not connect to proxy")
        print(f"   Error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        print("\n❌ Proxy test failed - HTTP requests are NOT using the proxy")
        print(f"   Error: {str(e)}")
        return False

def test_tcp_connection():
    """Test direct TCP connection (should not use proxy)."""
    try:
        logger.info("Testing direct TCP connection...")
        
        # Try to connect to localhost or any available test server
        host = "localhost"
        port = 22  # SSH port, should be available on most systems
        
        logger.info(f"Connecting to {host}:{port} (direct TCP, should not use proxy)")
        
        # Use socket for direct TCP connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        sock.close()
        
        logger.info("TCP connection successful!")
        print("\n✅ TCP connection test successful")
        return True
    except Exception as e:
        logger.error(f"TCP connection failed: {str(e)}")
        print("\n❌ TCP connection test failed")
        print(f"   Error: {str(e)}")
        return False

def test_proxy_connectivity():
    """Test if we can connect directly to the proxy."""
    logger.info("Testing direct connection to proxy...")
    
    # Get proxy from environment or use the provided one
    proxy = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY') or "http://172.20.12.74:3128"
    logger.info(f"Using proxy: {proxy}")
    
    # Parse proxy URL
    if proxy.startswith('http://'):
        proxy_parts = proxy[7:].split(':')
    else:
        proxy_parts = proxy.split(':')
        
    proxy_host = proxy_parts[0]
    proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 3128
    
    logger.info(f"Extracted proxy host: {proxy_host}, port: {proxy_port}")
    
    # Try to connect directly to the proxy
    try:
        logger.info(f"Attempting to connect to {proxy_host}:{proxy_port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((proxy_host, proxy_port))
        sock.close()
        
        logger.info("Successfully connected to proxy!")
        print(f"\n✅ Proxy connectivity test successful - Can connect to {proxy_host}:{proxy_port}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to proxy: {str(e)}")
        print(f"\n❌ Proxy connectivity test failed - Cannot connect to {proxy_host}:{proxy_port}")
        print(f"   Error: {str(e)}")
        return False

def main():
    """Run the test."""
    logger.info("Starting proxy configuration test")
    
    # First, test direct connectivity to the proxy
    proxy_conn_result = test_proxy_connectivity()
    
    if not proxy_conn_result:
        print("\n⚠️ Cannot connect to the proxy server. Please check:")
        print("   1. If the proxy address and port are correct")
        print("   2. If your network allows connections to the proxy")
        print("   3. If the proxy server is running")
        print("   4. If there are any firewall rules blocking the connection")
        print("\nTests will continue but will likely fail...")
    
    # Test HTTP proxy for requests
    result = test_proxy()
    
    # Test TCP connection
    tcp_result = test_tcp_connection()
    
    # Print overall status
    if proxy_conn_result and result and tcp_result:
        print("\n🎉 All tests passed! Your configuration should work correctly")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Please review the logs")
        sys.exit(1)

if __name__ == "__main__":
    main() 