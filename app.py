# -*- coding: utf-8 -*-

from tornado import ioloop, httpserver, web

from handlers import main
from helpers import APP_SETTINGS

application = web.Application([
                web.URLSpec(r'/repos/all/(\d+)', main.ShowRepos, name='show'),
                web.URLSpec(r'/repos/create', main.CreateRepo, name='create'),
                web.URLSpec(r'/repos/(\d+)/(\d+)', main.ViewRepo, name='view'),
                web.URLSpec(r'/repos/(\d+)/update', main.UpdateRepo, name='update'),
                web.URLSpec(r'/', web.RedirectHandler, {'url': '/repos/all/1'})
    ], **APP_SETTINGS)

http_server = httpserver.HTTPServer(application)
http_server.listen(5000, address='0.0.0.0')
ioloop.IOLoop.current().start()
