# -*- coding: utf-8 -*-

from tornado import ioloop, httpserver, web

from handlers import main

APP_SETTINGS = {'template_path': 'tpls', 'debug': True,
                'cookie_secret': 'some_secret', 'autoescape': None}

application = web.Application([
                web.URLSpec(r'/', main.Repos, name='index'),
                web.URLSpec(r'/repos/create', main.CreateRepo, name='create_repo'),
                (r'/static/(.*)', web.StaticFileHandler, {'path': 'static'})
    ], **APP_SETTINGS)

http_server = httpserver.HTTPServer(application)
http_server.listen(5000, address='0.0.0.0')
ioloop.IOLoop.current().start()
