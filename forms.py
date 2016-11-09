# -*- coding: utf-8 -*-
from wtforms_tornado import Form
from wtforms import fields
from wtforms import validators

from helpers import GHUB_URL, GHUB_PATTERN


class AddRepoForm(Form):
    href = (fields.StringField('Адрес (в формате {})'.format(GHUB_PATTERN),
                               [validators.required(message='Обязательное поле')]))

    def validate_href(self, field):
        """Валидация адреса репозитория по регулярному выражения"""
        if GHUB_URL.search(field.data) is None:
            raise validators.ValidationError('Ошибка в адресе')
