# -*- coding: utf-8 -*-
import math

from tornado import gen
from tornado.escape import json_decode

import forms
from helpers import BaseHandler, GHUB_URL, API_PATTERN, get_commit_from_json, COMMITS
import models


class ShowRepos(BaseHandler):
    title = 'Репозитории'

    def get(self):
        repos = models.Repo.select().order_by(models.Repo.date_added.desc())
        self.render('index.html', title=self.title, repos=repos)


class ViewRepo(BaseHandler):
    title = 'Коммиты репозитория'

    def get(self, repo_id, page):
        page = int(page)
        repo = models.Repo.get(id=repo_id)
        all_commits = models.Commit.select().where(models.Commit.repo == repo)
        commits = (all_commits.order_by(models.Commit.date_added.desc()).
                   paginate(page, COMMITS['per_page']))
        total_records = all_commits.count()
        last_page = math.ceil(total_records / COMMITS['per_page'])

        self.render('details.html', title=self.title, repo=repo, commits=commits,
                    last_page=last_page, page=page, per_page=COMMITS['per_page'],
                    total_records=total_records)


class CreateRepo(BaseHandler):
    title = 'Добавить репозиторий'
    response = None

    def get(self):
        self.render('create.html', title=self.title, form=forms.AddRepoForm())

    @gen.coroutine
    def post(self):
        form = forms.AddRepoForm(self.request.arguments)

        if not form.validate():
            self.render('create.html', title=self.title, form=form)
            return

        owner_name, repo_name = GHUB_URL.match(form.href.data).groups()

        repo = models.Repo(name=repo_name, owner_name=owner_name, href=form.href.data)

        url = API_PATTERN.format(owner_name, repo_name)

        yield self.get_commits(url)

        repo.next_page = self.get_next_page_link()

        response = json_decode(self.response.body.decode())

        # Сохраняем репозиторий и его коммиты в транзакции
        with models.database.atomic():
            repo.save()
            models.Commit.insert_many(get_commit_from_json(response, repo=repo.id)).execute()

        self.redirect(self.reverse_url('view', repo.id, 1))


class UpdateRepo(BaseHandler):
    @gen.coroutine
    def post(self, repo_id):
        repo = models.Repo.get(id=repo_id)

        yield self.get_commits(repo.next_page)

        repo.next_page = self.get_next_page_link()

        response = json_decode(self.response.body.decode())

        # Сохраняем репозиторий и его коммиты в транзакции
        with models.database.atomic():
            repo.save()
            models.Commit.insert_many(get_commit_from_json(response, repo=repo.id)).execute()

        page = math.ceil(models.Commit.select().count() / COMMITS['per_page'])

        self.redirect(self.reverse_url('view', repo_id, page))
