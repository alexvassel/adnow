# -*- coding: utf-8 -*-
import re

from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler

from models import Repo, Commit

from models import database

APP_SETTINGS = {'template_path': 'templates', 'debug': True,
                'cookie_secret': 'some_secret', 'autoescape': None}

GHUB_PATTERN = 'https://github.com/<имя пользователя>/<имя репозитория>'

# Регулярное выражение для проверки корректности введенного пользователем адреса репозитория
GHUB_URL = re.compile(r'https://github.com/(?P<owner_name>[\w-]{1,99})/(?P<repo_name>[\w-]{1,99})$')

# Шаблон адреса githib API
API_PATTERN = 'https://api.github.com/repos/{}/{}/commits'

# https://developer.github.com/v3/#user-agent-required
GITHUB_USERAGENT = 'Awesome-Octocat-App'


# http://docs.peewee-orm.com/en/latest/peewee/database.html#tornado
class BaseHandler(RequestHandler):
    response = None

    def prepare(self):
        database.connect()
        return super().prepare()

    def on_finish(self):
        if not database.is_closed():
            database.close()
        return super().on_finish()

    @gen.coroutine
    def get_commits(self, url):
        """получение коммитов репозитория вынесено"""
        # https://developer.github.com/v3/#user-agent-required
        http_client = AsyncHTTPClient(defaults=dict(user_agent=GITHUB_USERAGENT))
        self.response = yield http_client.fetch(url)

    def get_next_page_link(self):
        if self.response.headers.get('Link') is not None:
            links = get_next_page(self.response.headers['Link'])
            if links.get('rel="next"') is not None:
                return links['rel="next"'][1:-1]


def create_tables():
    """Создание БД"""
    database.connect()
    database.create_tables([Repo, Commit])


def get_commit_from_json(jsn, repo):
    """По входному json и id репозитория готовит данные для модели коммита"""
    for commit in jsn:
        cmt = commit.get('commit')
        author = cmt.get('author').get('name') if cmt.get('author') else None
        message = commit.get('commit').get('message')
        sha = commit['sha']
        date_added = cmt.get('author').get('date') if cmt.get('author') else None
        yield dict(author=author, message=message, sha=sha, date_added=date_added, repo=repo)


def get_next_page(header):
    """Ожидаем строку вида
    ''<https://api.github.com/repositories/4164482/commits?page=782>; rel="next", <https://api.github.com/repositories/4164482/commits?page=782>; rel="last", <https://api.github.com/repositories/4164482/commits?page=1>; rel="first", <https://api.github.com/repositories/4164482/commits?page=780>; rel="prev"'
    Возвращаем словари вида {'rel="next"': '<https://api.github.com/repositories/4164482/commits?page=782>'}
    """
    r = {}
    if not header:
        return r
    parts = header.split(', ')
    for part in parts:
        value, key = part.split('; ')
        r[key] = value
    return r


if __name__ == '__main__':
    create_tables()
