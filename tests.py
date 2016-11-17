# -*- coding: utf-8 -*-
from datetime import datetime
from http import client
import io
import json
from urllib.parse import urlencode
import os
import unittest

import mock
from tornado.httpclient import HTTPRequest, HTTPResponse
from tornado.concurrent import Future
from tornado.testing import AsyncHTTPTestCase

from app import application
from helpers import get_next_page, get_commit_from_json, create_tables
from models import DB, Repo, Commit


class ApplicationTestCase(AsyncHTTPTestCase):
    TEST_REPO = dict(href='https://github.com/alexvassel/adnow', name='test_name',
                     owner_name='test_owner_name', next_page='test_next_page')
    TEST_COMMIT = dict(author='test_author', message='test_message', sha='test_sha',
                       date_added=datetime.now())
    MESSAGES = dict(get_more='Подгрузить еще', no_records='записей нет')
    TEST_COUNT = 3
    data = open('fixtures/commits.json')

    def get_app(self):
        return application

    def setUp(self):
        create_tables()
        super().setUp()

    def tearDown(self):
        os.remove(DB)
        super().tearDown()

    def test_redirect(self):
        response = self.fetch(self.get_app().reverse_url('index'), follow_redirects=False)
        self.assertEqual(response.code, client.MOVED_PERMANENTLY)

    def test_index(self):
        response = self.fetch(self.get_app().reverse_url('index'))
        self.assertEqual(response.code, client.OK)

    def test_create_repo(self):
        response = self.fetch(self.get_app().reverse_url('create'))
        self.assertNotIn('errors', response.body.decode())
        response = self.fetch(self.get_app().reverse_url('create'), method='POST', body='')
        self.assertIn('errors', response.body.decode())
        data = {'href': self.TEST_REPO['href'] + '/'}
        response = self.fetch(self.get_app().reverse_url('create'), method='POST',
                              body=urlencode(data).encode())
        self.assertIn('errors', response.body.decode())

    def test_repo_commits(self):
        repo = Repo.create(**self.TEST_REPO)
        repo.save()

        response = self.fetch(self.get_app().reverse_url('view', repo.id))

        self.assertIn(self.MESSAGES['no_records'], response.body.decode())

        self.assertIn(self.MESSAGES['get_more'], response.body.decode())

        for commit in range(self.TEST_COUNT):
            commit_data = self.TEST_COMMIT
            commit_data.update({'repo': repo})
            c = Commit(**commit_data)
            c.save()

        response = self.fetch(self.get_app().reverse_url('view', repo.id))

        self.assertEqual(response.body.decode().count(self.TEST_COMMIT['message']),
                         self.TEST_COUNT)

        self.assertIn(self.MESSAGES['get_more'], response.body.decode())

        repo.next_page = None
        repo.save()

        response = self.fetch(self.get_app().reverse_url('view', repo.id))

        self.assertNotIn(self.MESSAGES['get_more'], response.body.decode())

    @mock.patch('helpers.BaseHandler.get_commits')
    def test_commits_create(self, get_commits):
        fixtures = self.data.buffer.read()
        jsn = json.loads(fixtures.decode())

        request = HTTPRequest(self.TEST_REPO['href'])
        response = HTTPResponse(request, client.OK, buffer=io.BytesIO(fixtures))

        future = Future()
        future.set_result(response)
        get_commits.return_value = future

        body = {'href': self.TEST_REPO['href']}
        response = self.fetch(self.get_app().reverse_url('create'), method='POST',
                              body=urlencode(body).encode())

        self.assertIn('всего {}'.format(len(jsn)), response.body.decode())
        self.assertEqual(len(jsn), Commit.select().count())
        self.assertEqual(1, Repo.select().count())


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
