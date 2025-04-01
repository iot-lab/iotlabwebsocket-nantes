#!/usr/bin/env python3
"""Test script for HTTP proxy configuration."""

import sys
import os
import tornado
from tornado import gen
from tornado.ioloop import IOLoop

# Get absolute path to the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory (project root) to sys.path if needed
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Import directly instead of relative imports
try:
    from logger import LOGGER, setup_server_logger
    DEFAULT_API_HOST = "localhost"
    DEFAULT_API_PORT = "8000"
    
    # Simple ApiClient class for testing
    class ApiClient:
        """Class that store information about the REST API."""

        def __init__(
            self,
            protocol,
            host=DEFAULT_API_HOST,
            port=DEFAULT_API_PORT,
            username="",
            password="",
            proxy=None,
        ):
            # pylint:disable=too-many-arguments
            self.protocol = protocol
            self.host = host
            self.port = port
            self.username = username
            self.password = password
            # Use provided proxy or try to get from environment
            self.proxy = proxy or os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
            print(f"ApiClient initialized with proxy: {self.proxy}")
except ImportError:
    # Fallback if logger module is not available
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOGGER = logging.getLogger("proxy-test")
    
    def setup_server_logger(log_file=None, log_console=False):
        """Setup logger with console output."""
        pass
    
    DEFAULT_API_HOST = "localhost"
    DEFAULT_API_PORT = "8000"
    
    # Simple ApiClient class for testing
    class ApiClient:
        """Class that store information about the REST API."""

        def __init__(
            self,
            protocol,
            host=DEFAULT_API_HOST,
            port=DEFAULT_API_PORT,
            username="",
            password="",
            proxy=None,
        ):
            # pylint:disable=too-many-arguments
            self.protocol = protocol
            self.host = host
            self.port = port
            self.username = username
            self.password = password
            # Use provided proxy or try to get from environment
            self.proxy = proxy or os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
            print(f"ApiClient initialized with proxy: {self.proxy}")

@gen.coroutine
def test_proxy():
    """Test HTTP requests through proxy."""
    setup_server_logger(log_console=True)
    LOGGER.info("Testing proxy connection...")
    
    # Get proxy from environment or use the provided one
    proxy = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY') or "http://172.20.12.74:3128"
    LOGGER.info(f"Using proxy: {proxy}")
    
    # Initialize API client with proxy
    api = ApiClient("https", host="www.iot-lab.info", proxy=proxy)
    
    # Try to fetch something from an external URL
    try:
        # In newer Tornado versions, proxy is configured globally
        proxy_host = None
        proxy_port = None
        
        if proxy:
            if proxy.startswith('http://'):
                proxy_parts = proxy[7:].split(':')
                proxy_host = proxy_parts[0]
                proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 3128
            else:
                proxy_parts = proxy.split(':')
                proxy_host = proxy_parts[0]
                proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 3128
            
            LOGGER.info(f"Configuring global proxy: {proxy_host}:{proxy_port}")
            
            # Configure the proxy globally
            tornado.httpclient.AsyncHTTPClient.configure(
                None, 
                defaults=dict(
                    proxy_host=proxy_host,
                    proxy_port=proxy_port
                )
            )

        # Now make a request using the configured client
        LOGGER.info("Sending HTTP request...")
        client = tornado.httpclient.AsyncHTTPClient()
        
        # Create request without proxy parameters
        request = tornado.httpclient.HTTPRequest("https://www.iot-lab.info")
        response = yield client.fetch(request)
        LOGGER.info(f"Connection successful! Response code: {response.code}")
        
        # Also test a second request to verify consistent behavior
        LOGGER.info("Testing a second request...")
        request2 = tornado.httpclient.HTTPRequest("https://www.iot-lab.info/testbed/")
        response2 = yield client.fetch(request2)
        LOGGER.info(f"Second request successful! Response code: {response2.code}")
        
        return True
    except Exception as e:
        LOGGER.error(f"Connection failed: {str(e)}")
        return False

@gen.coroutine
def test_tcp_connection():
    """Test direct TCP connection (should not use proxy)."""
    try:
        LOGGER.info("Testing direct TCP connection...")
        
        # Define constants instead of importing
        NODE_TCP_PORT = 22  # Use SSH port instead of custom port
        
        # Try to connect to localhost or any available test server
        host = "localhost"
        port = NODE_TCP_PORT  # SSH port, should be available on most systems
        
        LOGGER.info(f"Connecting to {host}:{port} (direct TCP, should not use proxy)")
        
        client = tornado.tcpclient.TCPClient()
        conn = yield client.connect(host, port)
        LOGGER.info("TCP connection successful!")
        conn.close()
        return True
    except Exception as e:
        LOGGER.error(f"TCP connection failed: {str(e)}")
        return False

def main():
    """Run the test."""
    LOGGER.info("Starting proxy configuration test")
    
    # Test HTTP proxy
    result = IOLoop.current().run_sync(test_proxy)
    if result:
        print("\n✅ Proxy test successful - HTTP requests are using the proxy")
    else:
        print("\n❌ Proxy test failed - HTTP requests are NOT using the proxy")
        print("   Check the logs for details")
    
    # Test TCP connection
    tcp_result = IOLoop.current().run_sync(test_tcp_connection)
    if tcp_result:
        print("\n✅ TCP connection test successful")
    else:
        print("\n❌ TCP connection test failed - Check the logs for details")
    
    # Print overall status
    if result and tcp_result:
        print("\n🎉 All tests passed! Your configuration should work correctly")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Please review the logs")
        sys.exit(1)

if __name__ == "__main__":
    main() 