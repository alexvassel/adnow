# -*- coding: utf-8 -*-
import re

from tornado.web import RequestHandler

from models import Repo, Commit

from models import database

APP_SETTINGS = {'template_path': 'tpls', 'debug': True,
                'cookie_secret': 'some_secret', 'autoescape': None}

# Регулярное выражение для проверко корректности введенного пользователем адреса репозитория
GHUB_URL = re.compile(r'https://github.com/(?P<owner_name>[\w]{1,99})/(?P<repo_name>[\w]{1,99})$')

# Щаблон адреса githib API
API_PATTERN = 'https://api.github.com/repos/{}/{}/commits'

# https://developer.github.com/v3/#user-agent-required
GITHUB_USERAGENT = 'Awesome-Octocat-App'

# БД создасться в корне директории проекта
DB = 'repos.sqlite'


# http://docs.peewee-orm.com/en/latest/peewee/database.html#tornado
class PeeweeRequestHandler(RequestHandler):
    def prepare(self):
        database.connect()
        return super().prepare()

    def on_finish(self):
        if not database.is_closed():
            database.close()
        return super().on_finish()


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


if __name__ == '__main__':
    create_tables()
