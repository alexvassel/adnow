# -*- coding: utf-8 -*-

from tornado import web

from handlers import main
from helpers import APP_SETTINGS

application = web.Application([
                web.URLSpec(r'/repos', main.ShowRepos, name='show'),
                web.URLSpec(r'/repos/create', main.CreateRepo, name='create'),
                web.URLSpec(r'/repos/(\d+)', main.ViewRepo, name='view'),
                web.URLSpec(r'/repos/(\d+)/update', main.UpdateRepo, name='update'),
                web.URLSpec(r'/', web.RedirectHandler, {'url': '/repos'}, name='index')
    ], **APP_SETTINGS)
