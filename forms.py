# -*- coding: utf-8 -*-
import re

from wtforms_tornado import Form
from wtforms import fields
from wtforms import validators

from helpers import GHUB_URL


class AddRepoForm(Form):
    href = (fields.StringField('Адрес', [validators.required(message='Обязательное поле')]))

    def validate_href(self, field):
        """Валидация адреса репозитория по регулярному выражения"""
        if GHUB_URL.search(field.data) is None:
            raise validators.ValidationError(''''Ожидаем адрес в формате
            https://github.com/<имя пользователя>/<имя репозитория>''')
