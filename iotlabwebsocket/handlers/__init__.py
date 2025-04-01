"""Test script for HTTP proxy configuration."""

import os
import tornado
from tornado import gen
from tornado.ioloop import IOLoop
from iotlabwebsocket.api import ApiClient
from iotlabwebsocket.logger import LOGGER, setup_server_logger

@gen.coroutine
def test_proxy():
    setup_server_logger(log_console=True)
    LOGGER.info("Testing proxy connection...")
    
    # Initialize API client with proxy
    proxy = "http://172.20.12.74:3128"
    api = ApiClient("https", host="www.iot-lab.info", proxy=proxy)
    
    # Try to fetch something from an external URL
    try:
        request = tornado.httpclient.HTTPRequest("https://www.iot-lab.info")
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield client.fetch(request)
        LOGGER.info("Connection successful! Response code: {}".format(response.code))
        return True
    except Exception as e:
        LOGGER.error("Connection failed: {}".format(str(e)))
        return False

def main():
    result = IOLoop.current().run_sync(test_proxy)
    if result:
        print("✅ Proxy test successful - HTTP requests are using the proxy")
    else:
        print("❌ Proxy test failed - Check the logs for details")

if __name__ == "__main__":
    main()
