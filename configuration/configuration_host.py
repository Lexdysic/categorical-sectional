"""
Module to run a RESTful server to set and get the configuration.
"""


import datetime
import json
import os
import re
import shutil
import socket
import sys
import urllib
from http.server import BaseHTTPRequestHandler

import configuration

VIEW_NAME_KEY = 'name'
MEDIA_TYPE_KEY = 'media_type'
MEDIA_TYPE_VALUE = 'application/json'

# Based on https://gist.github.com/tliron/8e9757180506f25e46d9

# EXAMPLES
# Invoke-WebRequest -Uri "http://localhost:8080/settings" -Method GET -ContentType "application/json"
# Invoke-WebRequest -Uri "http://localhost:8080/settings" -Method PUT -ContentType "application/json" -Body '{"flip_horizontal": true}'
# curl -X PUT -d '{"declination": 17}' http://localhost:8080/settings

ERROR_JSON = {'success': False}


def get_settings(
    handler
):
    """
    Handles a get-the-settings request.
    """
    if configuration.CONFIG is not None:
        return configuration.CONFIG
    else:
        return ERROR_JSON


def set_settings(
    handler
):
    """
    Handles a set-the-settings request.
    """

    if configuration.CONFIG is not None:
        payload = handler.get_payload()
        print("settings/PUT:")
        print(payload)
        configuration.CONFIG.update_configuration(payload)
        return json.dumps(configuration.CONFIG, indent=4, sort_keys=True)
    else:
        return ERROR_JSON


class ConfigurationHost(BaseHTTPRequestHandler):
    """
    Handles the HTTP response for status.
    """

    HERE = os.path.dirname(os.path.realpath(__file__))
    ROUTES = {
        r'^/settings': {'GET': get_settings, 'PUT': set_settings, MEDIA_TYPE_KEY: MEDIA_TYPE_VALUE}
    }

    def do_HEAD(
        self
    ):
        self.handle_method('HEAD')

    def do_GET(
        self
    ):
        self.handle_method('GET')

    def do_POST(
        self
    ):
        self.handle_method('POST')

    def do_PUT(
        self
    ):
        self.handle_method('PUT')

    def do_DELETE(
        self
    ):
        self.handle_method('DELETE')

    def get_payload(
        self
    ) -> dict:
        try:
            payload_len = int(self.headers.getheader('content-length', 0))
            payload = self.rfile.read(payload_len)
            payload = json.loads(payload)
            return payload
        except:
            return {}

    def __handle_invalid_route__(
        self
    ):
        """
        Handles the response to a bad route.
        """
        self.send_response(404)
        self.end_headers()
        self.wfile.write('Route not found\n')

    def __handle_file_request__(
        self,
        route,
        method: str
    ):
        if method == 'GET':
            try:
                f = open(os.path.join(
                    ConfigurationHost.HERE, route['file']))
                try:
                    self.send_response(200)
                    if 'media_type' in route:
                        self.send_header(
                            'Content-type', route['media_type'])
                    self.end_headers()
                    shutil.copyfileobj(f, self.wfile)
                finally:
                    f.close()
            except:
                self.send_response(404)
                self.end_headers()
                self.wfile.write('File not found\n')
        else:
            self.send_response(405)
            self.end_headers()
            self.wfile.write('Only GET is supported\n')

    def __finish_get_put_delete_request__(
        self,
        route,
        method: str
    ):
        if method in route:
            content = route[method](self)
            if content is not None:
                self.send_response(200)
                if 'media_type' in route:
                    self.send_header(
                        'Content-type', route['media_type'])
                self.end_headers()
                if method != 'DELETE':
                    self.wfile.write(json.dumps(content))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write('Not found\n')
        else:
            self.send_response(405)
            self.end_headers()
            self.wfile.write(method + ' is not supported\n')

    def __handle_request__(
        self,
        route,
        method: str
    ):
        if method == 'HEAD':
            self.send_response(200)
            if 'media_type' in route:
                self.send_header('Content-type', route['media_type'])
            self.end_headers()
        else:
            if 'file' in route:
                self.__handle_file_request__(route, method)
            else:
                self.__finish_get_put_delete_request__(route, method)

    def handle_method(
        self,
        method: str
    ):
        route = self.get_route()
        if route is None:
            self.__handle_invalid_route__()
        else:
            self.__handle_request__(route, method)

    def get_route(
        self
    ):
        for path, route in ConfigurationHost.ROUTES.items():
            if re.match(path, self.path):
                return route
        return None
