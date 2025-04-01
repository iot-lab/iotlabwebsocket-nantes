# HTTP Proxy Configuration for IoT Lab WebSocket Service

This document explains how to configure and use the HTTP proxy with the IoT Lab WebSocket service.

## Overview

The IoT Lab WebSocket service has been modified to support HTTP proxy configuration. This allows the service to make outgoing HTTP requests through a proxy server when accessing external resources.

## Configuration Options

There are three ways to configure the HTTP proxy:

1. **Environment Variables** (Recommended)
   ```bash
   # Linux/Unix
   export http_proxy=http://172.20.12.74:3128
   export HTTP_PROXY=http://172.20.12.74:3128
   
   # Windows
   set http_proxy=http://172.20.12.74:3128
   set HTTP_PROXY=http://172.20.12.74:3128
   ```

2. **Command Line Argument**
   ```bash
   python -m iotlabwebsocket --http-proxy http://172.20.12.74:3128
   ```

3. **System-wide Configuration** (On srveh)
   The proxy is already configured in `/etc/profile.d/proxy_http.sh` on the srveh server.

## Testing the Proxy Configuration

We've provided two test scripts to verify that the proxy configuration is working correctly:

- **test_proxy.py**: A basic test that verifies HTTP requests are routed through the proxy
- **run_proxy_tests.bat**: A Windows batch script that runs the basic test and provides a summary

To run the tests:

```bash
# On Windows
run_proxy_tests.bat

# On Linux/Unix
./run_proxy_tests.sh
```

## Implementation Details

The following components were modified to support HTTP proxy:

1. **ApiClient** (`api.py`)
   - Added proxy parameter to the constructor
   - Modified HTTP client methods to use the configured proxy
   - Added proxy parsing logic to handle different proxy formats

2. **WebApplication** (`web_application.py`)
   - Added global HTTP client configuration with proxy settings
   - Initializes proxy settings when the application starts

3. **Command Line Parser** (`parser.py`)
   - Added a new `--http-proxy` argument to allow specifying proxy from command line
   - Made it read from environment variables by default

4. **Service Initialization** (`service_cli.py`)
   - Added logic to pass proxy settings from command line or environment to ApiClient

## Troubleshooting

If the service is not using the proxy correctly, check the following:

1. **Verify Environment Variables**: Make sure the environment variables are correctly set
   ```bash
   # Linux/Unix
   echo $http_proxy
   echo $HTTP_PROXY
   
   # Windows
   echo %http_proxy%
   echo %HTTP_PROXY%
   ```

2. **Check Proxy Format**: The proxy should be in the format `http://host:port`

3. **Verify Access**: Ensure your machine can access the proxy server
   ```bash
   # Test connectivity to the proxy
   telnet 172.20.12.74 3128
   ```

4. **Check Logs**: Enable console logging with `--log-console` to see debug messages
   ```bash
   python -m iotlabwebsocket --log-console
   ```

5. **Capture Traffic**: Use tcpdump to verify traffic is going through the proxy
   ```bash
   sudo tcpdump -nei ens3 host 172.20.12.74 and port 3128
   ```

## Additional Notes

- The TCP client connections to IoT nodes remain direct TCP connections and do not use the HTTP proxy
- HTTPS requests are also routed through the HTTP proxy
- The WebSocket connections themselves don't use the proxy; only the API requests do 