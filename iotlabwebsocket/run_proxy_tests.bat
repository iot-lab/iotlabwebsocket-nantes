@echo off
:: Script to run all proxy tests on Windows

:: Function to show a section header
echo.
echo ==========================================================
echo   IoT Lab WebSocket Proxy Test Suite
echo ==========================================================
echo.
echo This script will run tests to verify that the HTTP proxy configuration is working correctly.
echo.

:: Check proxy environment
if "%http_proxy%"=="" (
  if "%HTTP_PROXY%"=="" (
    echo Warning: No HTTP proxy environment variables are set.
    echo You can set them with:
    echo set http_proxy=http://172.20.12.74:3128
    echo set HTTP_PROXY=http://172.20.12.74:3128
    echo.
    echo For now, the tests will use the default proxy: http://172.20.12.74:3128
  ) else (
    echo Using proxy from environment: %HTTP_PROXY%
  )
) else (
  echo Using proxy from environment: %http_proxy%
)

echo.
echo ==========================================================
echo   Running Basic HTTP proxy test
echo ==========================================================
echo Command: python test_proxy.py
echo.

:: Run the basic proxy test
python test_proxy.py
set basic_test_result=%ERRORLEVEL%

if %basic_test_result%==0 (
  echo.
  echo ✅ Basic HTTP proxy test passed!
) else (
  echo.
  echo ❌ Basic HTTP proxy test failed with exit code %basic_test_result%
)

echo.
echo ==========================================================
echo   Test Results Summary
echo ==========================================================
echo.

if %basic_test_result%==0 (
  echo 🎉 All tests passed! Your proxy configuration is working correctly.
  echo.
  echo You can now deploy your changes to srveh and run the service with:
  echo   python -m iotlabwebsocket --http-proxy http://172.20.12.74:3128
  echo.
  echo Or simply relying on the environment variables:
  echo   python -m iotlabwebsocket
  echo.
  exit /b 0
) else (
  echo ⚠️ Some tests failed. Please check the logs above for details.
  echo.
  echo If you need help troubleshooting, check these common issues:
  echo 1. Make sure the proxy address and port are correct
  echo 2. Verify that the proxy is accessible from your machine
  echo 3. Check for any network restrictions
  echo.
  exit /b 1
) 