# -*- coding: utf-8 -*-
import re

from tornado.web import RequestHandler

from models import Repo, Commit

from models import database

GHUB_URL = re.compile(r'https://github.com/(?P<owner_name>[\w]{1,99})/(?P<repo_name>[\w]{1,99})$')


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


if __name__ == '__main__':
    create_tables()
