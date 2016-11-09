# -*- coding: utf-8 -*-

from tornado import ioloop, httpserver, web

from handlers import main
from helpers import APP_SETTINGS

application = web.Application([
                web.URLSpec(r'/', main.Repos, name='index'),
                web.URLSpec(r'/repos/create', main.CreateRepo, name='create'),
                web.URLSpec(r'/repos/(\d+)', main.RepoDetails, name='details'),
    ], **APP_SETTINGS)

http_server = httpserver.HTTPServer(application)
http_server.listen(5000, address='0.0.0.0')
ioloop.IOLoop.current().start()
