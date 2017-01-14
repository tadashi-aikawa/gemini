#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import shutil
import sys
from io import StringIO

from unittest.mock import MagicMock
from unittest.mock import patch

import gemini
import datetime
from requests.exceptions import ConnectionError


class ResponseBuilder():
    """
    Create mock of requests.models.Response.
    """
    def __init__(self):
        self._text = None
        self._json = None
        self._url = None
        self._status_code = None
        self._content_type = None
        self._content = None
        self._seconds = None
        self._microseconds = None

    def text(self, text):
        self._text = text
        return self

    def json(self, json):
        self._json = json
        return self

    def url(self, url):
        self._url = url
        return self

    def status_code(self, status_code):
        self._status_code = status_code
        return self

    def content_type(self, content_type):
        self._content_type = content_type
        return self

    def content(self, content):
        self._content = content
        return self

    def second(self, seconds, microseconds):
        self._seconds = seconds
        self._microseconds = microseconds
        return self

    def build(self):
        m = MagicMock()
        m.text = self._text
        m.url = self._url
        m.status_code = self._status_code
        m.headers = {
            "content-type": self._content_type
        }
        m.content = self._content
        m.elapsed.seconds = self._seconds
        m.elapsed.microseconds = self._microseconds
        m.json.return_value = self._json
        return m


class CreateProxiesTest:
    def test_normal(self):
        proxy = '1.2.3.4'
        actual = gemini.create_proxies(proxy)

        assert actual['http'] == 'http://1.2.3.4'
        assert actual['https'] == 'https://1.2.3.4'

    def test_none(self):
        proxy = None
        actual = gemini.create_proxies(proxy)

        assert actual == {}


class TestCreateTrial:
    def test_normal(self):
        status = 'status'
        req_time = datetime.datetime(2000, 1, 2, 0, 10, 20, 123456)
        path = '/path'
        qs = {
            'q1': ['1'],
            'q2': ['10000', '2']
        }
        headers = {
            'header1': '1',
            'header2': '2'
        }
        res_one = ResponseBuilder().url('URL_ONE') \
                                   .status_code(200) \
                                   .content('a') \
                                   .second(1, 234567) \
                                   .build()
        res_other = ResponseBuilder().url('URL_OTHER') \
                                     .status_code(400) \
                                     .content('ab') \
                                     .second(9, 876543) \
                                     .build()
        file_one = 'file_one'
        file_other = 'file_other'

        actual = gemini.create_trial(res_one, res_other, file_one, file_other, status, req_time, path, qs, headers)
        expected = {
            "request_time": '2000/01/02 00:10:20',
            "status": 'status',
            "path": '/path',
            "queries": {
                'q1': ['1'],
                'q2': ['10000', '2']
            },
            "headers": {
                "header1": "1",
                "header2": "2",
            },
            "one": {
                "file": 'file_one',
                "url": 'URL_ONE',
                "status_code": 200,
                "byte": 1,
                "response_sec": 1.23
            },
            "other": {
                "file": 'file_other',
                "url": 'URL_OTHER',
                "status_code": 400,
                "byte": 2,
                "response_sec": 9.88
            }
        }

        assert actual == expected

    def test_file_is_none(self):
        status = 'status'
        req_time = datetime.datetime(2000, 1, 2, 0, 10, 20, 123456)
        path = '/path'
        qs = {
            'q1': ['1'],
            'q2': ['10000', '2']
        }
        headers = {
            'header1': '1',
            'header2': '2'
        }
        res_one = ResponseBuilder().url('URL_ONE') \
                                   .status_code(200) \
                                   .content('a') \
                                   .second(1, 234567) \
                                   .build()
        res_other = ResponseBuilder().url('URL_OTHER') \
                                     .status_code(400) \
                                     .content('ab') \
                                     .second(9, 876543) \
                                     .build()
        file_one = None
        file_other = None

        actual = gemini.create_trial(res_one, res_other, file_one, file_other, status, req_time, path, qs, headers)
        expected = {
            "request_time": '2000/01/02 00:10:20',
            "status": 'status',
            "path": '/path',
            "queries": {
                'q1': ['1'],
                'q2': ['10000', '2']
            },
            "headers": {
                "header1": "1",
                "header2": "2",
            },
            "one": {
                "url": 'URL_ONE',
                "status_code": 200,
                "byte": 1,
                "response_sec": 1.23
            },
            "other": {
                "url": 'URL_OTHER',
                "status_code": 400,
                "byte": 2,
                "response_sec": 9.88
            }
        }

        assert actual == expected


@patch('gemini.now')
@patch('gemini.concurrent_request')
class TestChallenge:
    """
    Only make mock for gemini.concurrent_request.
    Because it uses http requests.
    """
    @classmethod
    def setup_class(cls):
        os.mkdir("tmpdir")

    @classmethod
    def teardown_class(cls):
        shutil.rmtree("tmpdir")

    def test_different(self, concurrent_request, now):
        res_one = ResponseBuilder().text('{"items": [1, 2, 3]}') \
                                   .json({"items": [1, 2, 3]}) \
                                   .url('URL_ONE') \
                                   .status_code(200) \
                                   .content_type('application/json;utf-8') \
                                   .content('{"items": [1, 2, 3]}') \
                                   .second(1, 234567) \
                                   .build()

        res_other = ResponseBuilder().text('{"items": [1, 2, 3, 4]}') \
                                     .json({"items": [1, 2, 3, 4]}) \
                                     .url('URL_OTHER') \
                                     .status_code(400) \
                                     .content_type('application/json;utf-8') \
                                     .content('{"items": [1, 2, 3, 4]}') \
                                     .second(9, 876543) \
                                     .build()
        concurrent_request.return_value = res_one, res_other
        now.return_value = datetime.datetime(2000, 1, 1, 0, 0, 0)

        args = {
            "seq": 1,
            "session": None,
            "host_one": None,
            "host_other": None,
            "path": "/challenge",
            "output_encoding": "utf8",
            "res_dir": "tmpdir",
            "qs": {
                "q1": ["1"],
                "q2": ["2-1", "2-2"]
            },
            "headers": {
                "header1": "1",
                "header2": "2",
            },
            "proxies_one": None,
            "proxies_other": None
        }

        actual = gemini.challenge(args)

        expected = {
            "request_time": '2000/01/01 00:00:00',
            "status": 'different',
            "path": '/challenge',
            "queries": {
                "q1": ["1"],
                "q2": ["2-1", "2-2"]
            },
            "headers": {
                "header1": "1",
                "header2": "2",
            },
            "one": {
                "file": "one1",
                "url": 'URL_ONE',
                "status_code": 200,
                "byte": 20,
                "response_sec": 1.23
            },
            "other": {
                "file": "other1",
                "url": 'URL_OTHER',
                "status_code": 400,
                "byte": 23,
                "response_sec": 9.88
            }
        }

        assert actual == expected

    def test_same(self, concurrent_request, now):
        res_one = ResponseBuilder().text('a') \
                                   .url('URL_ONE') \
                                   .status_code(200) \
                                   .content_type('text/plain;utf-8') \
                                   .content('a') \
                                   .second(1, 234567) \
                                   .build()

        res_other = ResponseBuilder().text('a') \
                                     .url('URL_OTHER') \
                                     .status_code(200) \
                                     .content_type('text/plain;utf-8') \
                                     .content('a') \
                                     .second(9, 876543) \
                                     .build()
        concurrent_request.return_value = res_one, res_other
        now.return_value = datetime.datetime(2000, 1, 1, 0, 0, 0)

        args = {
            "seq": 1,
            "session": None,
            "host_one": None,
            "host_other": None,
            "path": "/challenge",
            "output_encoding": "utf8",
            "res_dir": "tmpdir",
            "qs": {
                "q1": ["1"],
                "q2": ["2-1", "2-2"]
            },
            "headers": {
                "header1": "1",
                "header2": "2",
            },
            "proxies_one": None,
            "proxies_other": None
        }
        actual = gemini.challenge(args)

        expected = {
            "request_time": '2000/01/01 00:00:00',
            "status": 'same',
            "path": '/challenge',
            "queries": {
                'q1': ['1'],
                'q2': ['2-1', '2-2']
            },
            "headers": {
                "header1": "1",
                "header2": "2",
            },
            "one": {
                "url": 'URL_ONE',
                "status_code": 200,
                "byte": 1,
                "response_sec": 1.23
            },
            "other": {
                "url": 'URL_OTHER',
                "status_code": 200,
                "byte": 1,
                "response_sec": 9.88
            }
        }

        assert actual == expected

    def test_different_without_order(self, concurrent_request, now):
        res_one = ResponseBuilder().text('{"items": [1, 2, 3]}') \
                                   .json({"items": [1, 2, 3]}) \
                                   .url('URL_ONE') \
                                   .status_code(200) \
                                   .content_type('application/json;utf-8') \
                                   .content('{"items": [1, 2, 3]}') \
                                   .second(1, 234567) \
                                   .build()

        res_other = ResponseBuilder().text('{"items": [3, 2, 1]}') \
                                     .json({"items": [3, 2, 1]}) \
                                     .url('URL_OTHER') \
                                     .status_code(200) \
                                     .content_type('application/json;utf-8') \
                                     .content('{"items": [3, 2, 1]}') \
                                     .second(9, 876543) \
                                     .build()
        concurrent_request.return_value = res_one, res_other
        now.return_value = datetime.datetime(2000, 1, 1, 0, 0, 0)

        args = {
            "seq": 1,
            "session": None,
            "host_one": None,
            "host_other": None,
            "path": "/challenge",
            "output_encoding": "utf8",
            "res_dir": "tmpdir",
            "qs": {
                "q1": ["1"],
                "q2": ["2-1", "2-2"]
            },
            "headers": {
                "header1": "1",
                "header2": "2",
            },
            "proxies_one": None,
            "proxies_other": None
        }
        actual = gemini.challenge(args)

        expected = {
            "request_time": '2000/01/01 00:00:00',
            "status": 'same without order',
            "path": '/challenge',
            "queries": {
                'q1': ['1'],
                'q2': ['2-1', '2-2']
            },
            "headers": {
                "header1": "1",
                "header2": "2",
            },
            "one": {
                "file": "one1",
                "url": 'URL_ONE',
                "status_code": 200,
                "byte": 20,
                "response_sec": 1.23
            },
            "other": {
                "file": "other1",
                "url": 'URL_OTHER',
                "status_code": 200,
                "byte": 20,
                "response_sec": 9.88
            }
        }

        assert actual == expected

    def test_failure(self, concurrent_request, now):
        concurrent_request.side_effect = ConnectionError
        now.return_value = datetime.datetime(2000, 1, 1, 0, 0, 0)

        args = {
            "seq": 1,
            "session": None,
            "host_one": "http://one",
            "host_other": "http://other",
            "path": "/challenge",
            "output_encoding": "utf8",
            "res_dir": "tmpdir",
            "qs": {
                "q1": ["1"]
            },
            "headers": {
                "header1": "1",
                "header2": "2",
            },
            "proxies_one": None,
            "proxies_other": None
        }
        actual = gemini.challenge(args)

        expected = {
            "request_time": '2000/01/01 00:00:00',
            "status": 'failure',
            "path": '/challenge',
            "queries": {
                'q1': ['1']
            },
            "headers": {
                "header1": "1",
                "header2": "2",
            },
            "one": {
                "url": 'http://one/challenge?q1=1',
            },
            "other": {
                "url": 'http://other/challenge?q1=1',
            }
        }

        assert actual == expected


@patch('gemini.now')
@patch('gemini.challenge')
@patch('modules.requestcreator.from_format')
class TestMain:

    @classmethod
    def setup_class(cls):
        cls.held, sys.stdout = sys.stdout, StringIO()

    @classmethod
    def teardown_class(cls):
        sys.stdout = cls.held

    def test(self, from_format, challenge, now):
        from_format.return_value = [
            {
                'path': '/path',
                'qs': ['qs'],
                'headers': ['headers']
            }
        ]
        challenge.side_effect = [
            {
                "a": 1,
                "b": 2
            },
            {
                "c": 3,
                "d": 4
            }
        ]
        now.side_effect = [
            datetime.datetime(2000, 1, 1, 23, 50, 30),
            datetime.datetime(2000, 1, 2, 0, 0, 0)
        ]

        args = {
            'files': ['line1', 'line2'],
            'input_format': None,
            'output_encoding': 'utf8',
            'proxy_one': 'http://proxy/one',
            'proxy_other': 'http://proxy/other',
            'host_one': 'http://host/one',
            'host_other': 'http://host/other',
            'res_dir': 'tmpdir',
            'threads': 1
        }
        gemini.main(args)

        expected = {
            "summary": {
                "time": {
                    "start": '2000/01/01 23:50:30',
                    "end": '2000/01/02 00:00:00',
                    "elapsed_sec": 570
                },
                "one": {
                    "host": "http://host/one",
                    "proxy": "http://proxy/one"
                },
                "other": {
                    "host": "http://host/other",
                    "proxy": "http://proxy/other"
                }
            },
            "trials": [
                {
                    "a": 1,
                    "b": 2
                },
                {
                    "c": 3,
                    "d": 4
                }
            ]
        }

        assert json.loads(sys.stdout.getvalue()) == expected