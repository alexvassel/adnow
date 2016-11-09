# -*- coding: utf-8 -*-

import datetime

import peewee

# БД создасться в корне директории проекта
DB = 'repos.sqlite'

database = peewee.SqliteDatabase(DB)


class Base(peewee.Model):
    class Meta:
        database = database
        # Обеим таблицам создаем индекс по дате
        indexes = ((('date_added',), False),)


class Repo(Base):
    # Не даем создавать два репозитория с одинаковым адресом
    href = peewee.CharField(unique=True)
    name = peewee.CharField(max_length=20)
    date_added = peewee.DateTimeField(default=datetime.datetime.utcnow)
    owner_name = peewee.CharField(max_length=20)


class Commit(Base):
    author = peewee.CharField(max_length=20, null=True)
    message = peewee.CharField(null=True)
    date_added = peewee.DateTimeField()
    sha = peewee.CharField(max_length=40)
    repo = peewee.ForeignKeyField(Repo, related_name='commits')
