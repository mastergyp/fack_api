#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado
from tornado.options import options
from apps.handlers import Main, ProjectHandler, ApiHandler, ProjectPlusHandler, ApiPlusHandler

application = tornado.web.Application([(r"/ph", ProjectHandler),
                                       (r"/ph/(\d+)", ProjectPlusHandler),
                                       (r"/ah/(\d+)", ApiHandler),
                                       (r"/ah/(\d+)/(\d+)", ApiPlusHandler),
                                       (r"/.*", Main)],
                                      debug=True,
                                      template_path="templates",
                                      static_path="static")

if __name__ == "__main__":
    options.parse_command_line()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
