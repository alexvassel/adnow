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


def get_commit_from_json(jsn, repo):
    for commit in jsn:
        cmt = commit.get('commit')
        author = cmt.get('author').get('name') if cmt.get('author') else None
        message = commit.get('commit').get('message')
        sha = commit['sha']
        date_added = cmt.get('author').get('date') if cmt.get('author') else None
        yield dict(author=author, message=message, sha=sha, date_added=date_added, repo=repo)


if __name__ == '__main__':
    create_tables()
