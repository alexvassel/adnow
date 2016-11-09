# -*- coding: utf-8 -*-
import json

from tornado import gen
from tornado.httpclient import AsyncHTTPClient

import forms
from helpers import (PeeweeRequestHandler, GHUB_URL, API_PATTERN, GITHUB_USERAGENT,
                     get_commit_from_json)
import models


class Repos(PeeweeRequestHandler):
    title = 'Репозитории'

    def get(self):
        repos = models.Repo.select().order_by(models.Repo.date_added.desc())
        self.render('index.html', title=self.title, repos=repos)


class RepoDetails(PeeweeRequestHandler):
    title = 'Коммиты репозитория'

    def get(self, repo_id):
        repo = models.Repo.get(id=repo_id)
        self.render('details.html', title=self.title, repo=repo, commit_model=models.Commit)


class CreateRepo(PeeweeRequestHandler):
    title = 'Добавить репозиторий'
    response = None

    def get(self):
        self.render('create.html', title=self.title, form=forms.AddRepoForm())

    @gen.coroutine
    def post(self):
        form = forms.AddRepoForm(self.request.arguments)

        if not form.validate():
            self.render('create.html', title=self.title, form=form)

        owner_name, repo_name = GHUB_URL.match(form.href.data).groups()

        repo = models.Repo(name=repo_name, owner_name=owner_name, href=form.href.data)

        url = API_PATTERN.format(owner_name, repo_name)

        yield self.get_commits(url)

        response = json.loads(self.response.body.decode())

        # Сохраняем репозиторий и его коммиты в транзакции
        with models.database.atomic():
            repo.save()
            models.Commit.insert_many(get_commit_from_json(response, repo=repo.id)).execute()

        self.redirect(self.reverse_url('details', repo.id))

    @gen.coroutine
    def get_commits(self, url):
        """получения коммитов репозитория вынесено"""
        # https://developer.github.com/v3/#user-agent-required
        http_client = AsyncHTTPClient(defaults=dict(user_agent=GITHUB_USERAGENT))
        self.response = yield http_client.fetch(url)
