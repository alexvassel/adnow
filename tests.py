# -*- coding: utf-8 -*-
from http import client
import json
import unittest

from tornado.testing import AsyncHTTPTestCase

from helpers import get_next_page, get_commit_from_json

from app import application


class ApplicationTestCase(AsyncHTTPTestCase):
    REPO_ADDRESS = 'https://github.com/alexvassel/adnow'

    def get_app(self):
        return application

    def test_redirect(self):
        response = self.fetch(self.get_app().reverse_url('index'), follow_redirects=False)
        self.assertEqual(response.code, client.MOVED_PERMANENTLY)

    def test_index(self):
        response = self.fetch(self.get_app().reverse_url('index'))
        self.assertEqual(response.code, client.OK)


class HeaderParsingTest(unittest.TestCase):
    data = '''<https://api.github.com/repositories/4164482/commits?page=782>; rel="next", <https://api.github.com/repositories/4164482/commits?page=782>; rel="last", <https://api.github.com/repositories/4164482/commits?page=1>; rel="first", <https://api.github.com/repositories/4164482/commits?page=780>; rel="prev"'''

    def test_header_parsing(self):
        expect = {'rel="next"': '<https://api.github.com/repositories/4164482/commits?page=782>',
                  'rel="prev"': '<https://api.github.com/repositories/4164482/commits?page=780>',
                  'rel="last"': '<https://api.github.com/repositories/4164482/commits?page=782>',
                  'rel="first"': '<https://api.github.com/repositories/4164482/commits?page=1>'}
        r = get_next_page(self.data)
        self.assertDictEqual(r, expect)

    def test_common(self):
        for kind in (str, list, dict, set, int, float):
            r = get_next_page(kind())
            self.assertIsInstance(r, dict)
            self.assertDictEqual(r, {})
        for obj in ([1], (1,), dict(a=1), 1, 1.0):
            self.assertRaises(AttributeError, get_next_page, obj)
        self.assertRaises(TypeError, get_next_page)
        self.assertRaises(ValueError, get_next_page, ' ')


class JsonParsingTest(unittest.TestCase):
    EXPECT = {'id': 42, 'keys': ['author', 'sha', 'date_added', 'message', 'repo']}

    data = open('fixtures/commits.json')

    def test_common(self):
        self.assertRaises(TypeError, get_commit_from_json)
        self.assertRaises(TypeError, get_commit_from_json, '')

        for d in get_commit_from_json('', ''):
            self.assertIs(d, None)

    def test_json_parsing(self):
        jsn = json.load(self.data)

        for r in get_commit_from_json(jsn, self.EXPECT['id']):
            self.assertIsInstance(r, dict)
            self.assertEqual(r['repo'], self.EXPECT['id'])
            self.assertListEqual(sorted(r), sorted(self.EXPECT['keys']))


if __name__ == '__main__':
    unittest.main()
