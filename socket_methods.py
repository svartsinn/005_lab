import mimetypes
import os
from datetime import datetime
from time import mktime
from urllib.parse import unquote
from wsgiref.handlers import format_date_time

from constants import *


class SocketRequestHandler:
    _request_data = ''
    _method = None
    _query_string = ''
    _query_params = ''
    _http = ''
    _path = '/'
    _headers = []

    def __init__(self, request_bytes):
        if self.is_length_exceeded(request_bytes) or not self.is_complete(request_bytes):
            return
        self._request_data = request_bytes.decode('utf-8')
        request_string, headers_string = self.request_data.split(CLRF, 1)
        self._method, self.query_string, self.http = request_string.split(' ')
        params = self.query_string.split('?', 1)
        self._path = unquote(params[0])
        self._query_params = params[1] if len(params) > 1 else ''
        self._headers = headers_string.splitlines()[:-1]

    @staticmethod
    def is_complete(request_bytes):
        return CLRF * 2 in request_bytes.decode('utf-8')

    @staticmethod
    def is_length_exceeded(request_bytes):
        return len(request_bytes.decode('utf-8')) > MAX_LENGTH

    @property
    def request_data(self):
        return self._request_data

    @property
    def path(self):
        return self._path

    @property
    def method(self):
        return self._method


class SocketResponseHandler:
    _allowed_methods = ['GET', 'HEAD']
    _status = OK
    _body = b''
    _content_type = 'text/html'
    _content_length = 0

    def __init__(self, request, document_root):
        self._request = request
        if not self._request.request_data:
            self._status = BAD_REQUEST
            return
        if self._request.method not in ALLOWED_METHODS:
            self._status = NOT_ALLOWED
            return
        self._file_path = self.build_file_path(document_root)
        if not os.path.exists(self._file_path):
            self._status = NOT_FOUND
            return
        self._content_type = self.get_content_type()
        self._content_length = self.get_file_size()
        if request.method == 'HEAD':
            return
        self._body = self.get_content()

    def build_file_path(self, document_root):
        path = self._request.path
        path += 'index.html' if path.endswith('/') else ''
        root = document_root if document_root else os.path.dirname(os.path.abspath(__file__))
        return root + os.path.normpath(path)

    def get_content(self):
        with open(self._file_path, 'rb') as file:
            return file.read()

    def get_file_size(self):
        return os.path.getsize(self._file_path)

    def get_content_type(self):
        content_type, encoding = mimetypes.guess_type(self._file_path)
        return content_type

    def get_headers(self):
        return [
            f'HTTP/1.1 {self._status} {self.get_reason_phrase()}',
            f'Date: {format(format_date_time(mktime(datetime.now().timetuple())))}',
            f'Content-Type: {self._content_type}',
            f'Content-Length: {self._content_length}',
            'Server: Poor man\'s server',
            'Connection: close',
        ]

    def get_reason_phrase(self):
        return STATUS_CODES[self._status]

    def to_bytes(self):
        return (CLRF.join(self.get_headers()) + CLRF * 2).encode('utf-8') + self._body
