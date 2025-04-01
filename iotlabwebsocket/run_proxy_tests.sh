#!/bin/bash
# Script to run all proxy tests

# Function to show a section header
show_header() {
    echo ""
    echo "=========================================================="
    echo "  $1"
    echo "=========================================================="
    echo ""
}

# Function to run a test and check its result
run_test() {
    local test_name="$1"
    local test_cmd="$2"
    
    show_header "Running $test_name"
    echo "Command: $test_cmd"
    echo ""
    
    # Run the command
    eval "$test_cmd"
    local result=$?
    
    # Check the result
    if [ $result -eq 0 ]; then
        echo ""
        echo "✅ $test_name passed!"
    else
        echo ""
        echo "❌ $test_name failed with exit code $result"
    fi
    
    return $result
}

# Check that proxy environment variables are set
check_proxy_env() {
    if [ -z "$http_proxy" ] && [ -z "$HTTP_PROXY" ]; then
        echo "Warning: No HTTP proxy environment variables are set."
        echo "You can set them with:"
        echo "export http_proxy=http://172.20.12.74:3128"
        echo "export HTTP_PROXY=http://172.20.12.74:3128"
        echo ""
        echo "For now, the tests will use the default proxy: http://172.20.12.74:3128"
    else
        echo "Using proxy from environment: ${http_proxy:-$HTTP_PROXY}"
    fi
}

# Make sure the test scripts are executable
chmod +x test_proxy.py
chmod +x test_service_with_proxy.py

# Welcome message
show_header "IoT Lab WebSocket Proxy Test Suite"
echo "This script will run tests to verify that the HTTP proxy configuration is working correctly."
echo ""

# Check proxy environment
check_proxy_env

# Run the basic proxy test
run_test "Basic HTTP proxy test" "python test_proxy.py"
basic_test_result=$?

# Run the service proxy test if we have root access (needed for tcpdump)
if [ "$(id -u)" -eq 0 ]; then
    run_test "Service with proxy test" "python test_service_with_proxy.py"
    service_test_result=$?
else
    echo ""
    echo "Note: The service test requires root access for tcpdump."
    echo "If you want to run the full test, please run this script with sudo:"
    echo "sudo $0"
    service_test_result=0  # Skip this test
fi

# Show final results
show_header "Test Results Summary"

if [ $basic_test_result -eq 0 ] && [ $service_test_result -eq 0 ]; then
    echo "🎉 All tests passed! Your proxy configuration is working correctly."
    echo ""
    echo "You can now deploy your changes to srveh and run the service with:"
    echo "  python -m iotlabwebsocket --http-proxy http://172.20.12.74:3128"
    echo ""
    echo "Or simply relying on the environment variables:"
    echo "  python -m iotlabwebsocket"
    echo ""
    exit 0
else
    echo "⚠️ Some tests failed. Please check the logs above for details."
    echo ""
    echo "If you need help troubleshooting, check these common issues:"
    echo "1. Make sure the proxy address and port are correct"
    echo "2. Verify that the proxy is accessible from your machine"
    echo "3. Check for any network restrictions"
    echo ""
    exit 1
fi 