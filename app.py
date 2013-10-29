#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado
from apps.handlers import Main, ProjectHandler, ApiHandler

application = tornado.web.Application([(r"/(ph|ph/\d+)", ProjectHandler),
                                       (r"/ah/(\d+|\d+/\d+)", ApiHandler),
                                       (r"/.*", Main)],
                                      debug=True,
                                      template_path="templates",
                                      static_path="static")

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()