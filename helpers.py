# -*- coding: utf-8 -*-
import re

from tornado.web import RequestHandler

from models import Repo, Commit

from models import database

GHUB_URL = re.compile(r'https://github.com/(?P<owner_name>[\w]{1,99})/(?P<repo_name>[\w]{1,99})$')

API_PATTERN = 'https://api.github.com/repos/{}/{}/commits'

# https://developer.github.com/v3/#user-agent-required
GITHUB_USERAGENT = 'Awesome-Octocat-App'


class PeeweeRequestHandler(RequestHandler):
    def prepare(self):
        database.connect()
        return super().prepare()

    def on_finish(self):
        if not database.is_closed():
            database.close()
        return super().on_finish()


def create_tables():
    database.connect()
    database.create_tables([Repo, Commit])


def get_commit_from_json(jsn):
    for commit in jsn:
        author = commit.get('author').get('login') if commit.get('author') is not None else None
        message = commit.get('commit').get('message') if commit.get('commit') is not None else None
        yield dict(author=author, message=commit.get('message'))


if __name__ == '__main__':
    create_tables()
