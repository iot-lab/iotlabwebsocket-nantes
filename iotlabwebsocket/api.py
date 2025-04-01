"""Client class for REST API."""

import json
import os

import tornado
from tornado import gen

from . import DEFAULT_API_HOST, DEFAULT_API_PORT
from .logger import LOGGER


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

    def __eq__(self, other):
        return (
            self.protocol == other.protocol
            and self.host == other.host
            and self.port == other.port
            and self.username == other.username
            and self.password == other.password
            and self.proxy == other.proxy
        )

    @property
    def url(self):
        """Returns the base URL for experiments in the API."""
        return "{}://{}:{}/api/experiments".format(self.protocol, self.host, self.port)

    @staticmethod
    def _configure_client(client, proxy=None):
        """Configure HTTP client with proxy settings if available."""
        if proxy:
            tornado.httpclient.AsyncHTTPClient.configure(
                None, defaults=dict(proxy_host=proxy)
            )

    def _fetch_sync(self, request):
        request.headers["Content-Type"] = "application/json"
        # Configure proxy for sync client if available
        if self.proxy:
            # Parse proxy URL to extract host and port
            proxy_host = None
            proxy_port = None
            
            if self.proxy.startswith('http://'):
                proxy_parts = self.proxy[7:].split(':')
                proxy_host = proxy_parts[0]
                proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 3128
            else:
                # If proxy is not in URL format, use as is
                proxy_parts = self.proxy.split(':')
                proxy_host = proxy_parts[0]
                proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 3128
            
            LOGGER.debug("Using HTTP proxy for request: {}:{}".format(proxy_host, proxy_port))
            request.proxy_host = proxy_host
            request.proxy_port = proxy_port
        
        client = tornado.httpclient.HTTPClient()
        return client.fetch(request).buffer.read()

    @gen.coroutine
    def _fetch_async(self, request):
        request.headers["Content-Type"] = "application/json"
        # Configure global AsyncHTTPClient with proxy if available
        if self.proxy:
            # Parse proxy URL to extract host and port
            proxy_host = None
            proxy_port = None
            
            if self.proxy.startswith('http://'):
                proxy_parts = self.proxy[7:].split(':')
                proxy_host = proxy_parts[0]
                proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 3128
            else:
                # If proxy is not in URL format, use as is
                proxy_parts = self.proxy.split(':')
                proxy_host = proxy_parts[0]
                proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 3128
            
            LOGGER.debug("Using HTTP proxy for request: {}:{}".format(proxy_host, proxy_port))
            request.proxy_host = proxy_host
            request.proxy_port = proxy_port
                
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield client.fetch(request)
        raise gen.Return(response.buffer.read())

    def _request(self, exp_id, resource):
        _url = "{}/{}/{}".format(self.url, exp_id, resource)
        kwargs = {}
        if self.username and self.password:
            kwargs.update(
                {"auth_username": self.username, "auth_password": self.password}
            )
        return tornado.httpclient.HTTPRequest(_url, **kwargs)

    @staticmethod
    def _parse_nodes_response(response):
        return json.loads(response)["nodes"]

    def fetch_nodes_sync(self, exp_id):
        """Fetch the list of nodes using a synchronous call."""
        response = self._fetch_sync(self._request(exp_id, ""))
        return ApiClient._parse_nodes_response(response.decode())

    @gen.coroutine
    def fetch_nodes_async(self, exp_id):
        """Fetch the list of nodes using an asynchronous call."""
        response = yield self._fetch_async(self._request(exp_id, ""))
        raise gen.Return(ApiClient._parse_nodes_response(response.decode()))

    def fetch_token_sync(self, exp_id):
        """Fetch the experiment token using a synchronous call."""
        response = self._fetch_sync(self._request(exp_id, "token"))
        return json.loads(response.decode())["token"]

    @gen.coroutine
    def fetch_token_async(self, exp_id):
        """Fetch the experiment token using an asynchronous call."""
        response = yield self._fetch_async(self._request(exp_id, "token"))
        raise gen.Return(json.loads(response.decode())["token"])
