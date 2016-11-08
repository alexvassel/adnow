# -*- coding: utf-8 -*-

import datetime

import peewee

DB = 'repos.sqlite'

database = peewee.SqliteDatabase(DB)


class Base(peewee.Model):
    class Meta:
        database = database
        indexes = ((('date_added',), True),)


class Repo(Base):
    href = peewee.CharField()
    name = peewee.CharField(max_length=20)
    date_added = peewee.DateTimeField(default=datetime.datetime.utcnow)
    owner_name = peewee.CharField(max_length=20)


class Commit(Base):
    author = peewee.CharField(max_length=20)
    message = peewee.CharField(null=True)
    date_added = peewee.DateTimeField()
    sha = peewee.CharField(max_length=40)
    repo = peewee.ForeignKeyField(Repo, related_name='commits')

