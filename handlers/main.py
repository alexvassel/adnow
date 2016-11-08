# -*- coding: utf-8 -*-
import urllib.parse

from tornado import gen
from tornado.httpclient import AsyncHTTPClient

import forms
from helpers import PeeweeRequestHandler, GHUB_URL
import models


class Repos(PeeweeRequestHandler):
    title = 'Репозитории'

    def get(self):
        repos = models.Repo.select().order_by(models.Repo.date_added.desc())
        self.render('index.html', title=self.title, repos=repos)


class CreateRepo(PeeweeRequestHandler):
    title = 'Добавить репозиторий'

    def get(self):
        self.render('create.html', title=self.title, form=forms.AddRepoForm())

    @gen.coroutine
    def post(self):
        form = forms.AddRepoForm(self.request.arguments)

        if not form.validate():
            self.render('create.html', title=self.title, form=form)

        print(GHUB_URL.match(form.href.data).groups())

        url = 'http://ya.ru'
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(url)
