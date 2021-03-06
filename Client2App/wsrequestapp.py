import requests
import json
import os
import urllib
from kivy.network.urlrequest import UrlRequest


class WSRequests:

    def __init__(self):
        self.url_base = 'http://localhost:8000/'
        self.token = self.load_token()

    def get_ws_data(self, action_url=None, params=None):
        if action_url is None or params is None:
            raise ValueError('Action url or parameters cannot be null')
        headers = {
            'Authorization': f'Token {self.token}'
        }
        req = UrlRequest(
            method='GET',
            url=f'{self.url_base}{action_url}',
            req_body=json.dumps(params),
            req_headers=headers,
            # timeout=10
        )
        req.wait()
        return req

    def load_token(self):
        return self.read_file_contents(path='token')

    def read_file_contents(self, path):
        if os.path.exists(path):
            with open(path) as infile:
                return infile.read().strip()