# -*- coding: utf-8 -*-

from tornado import ioloop, httpserver, web

from handlers import main
from helpers import APP_SETTINGS

application = web.Application([
                web.URLSpec(r'/', main.ShowRepos, name='index'),
                web.URLSpec(r'/repos/create', main.CreateRepo, name='create'),
                web.URLSpec(r'/repos/(\d+)', main.ViewRepo, name='view'),
                web.URLSpec(r'/repos/(\d+)/update', main.UpdateRepo, name='update')
    ], **APP_SETTINGS)

http_server = httpserver.HTTPServer(application)
http_server.listen(5000, address='0.0.0.0')
ioloop.IOLoop.current().start()
