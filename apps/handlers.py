#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import os
import urlparse
import tornado.web
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))), 'db/database.sqlite')


def _execute(*query):
    connection = sqlite3.connect(DB_PATH)
    cursorobj = connection.cursor()
    try:
        cursorobj.execute(*query)
        result = cursorobj.fetchall()
        connection.commit()
    except Exception:
        raise
    connection.close()
    return result

last_pid = _execute('''select * from projects where active=1 limit 1''')
if bool(last_pid):
    ACTIVE_PID = last_pid[0][0]
else:
    ACTIVE_PID = 1

METHODS = {"get": 0, "post": 1, "put": 2, "patch": 3, "delete": 4, "copy": 5,
               "head": 6, "options": 7, "link": 8, "unlink": 9, "purge": 10}


class ProjectHandler(tornado.web.RequestHandler):
    def get(self, *args):
        #项目列表
        pids = _execute("select * from projects")
        self.render('projects.html', projects=pids, title="项目管理页面")

    def _clear_active(self):
        #清除所有活动的项目
        _execute('''update projects set active=? where active=?''', (0, 1))


    def post(self, *args):
        #添加项目
        project_name = self.get_argument("name", "未命名项目")
        self._clear_active()
        _execute('''insert into projects (name) values ('%s') ''' % project_name)

        self.write({"error": 0, "msg": "ok"})

    def put(self, *args):
        #修改项目
        project_name = self.get_argument("name", "未命名项目")
        pid = int(self.get_argument("pid", None) or 0)
        _execute('''update projects  set name='%s' where pid=%d ''' % (project_name, pid))
        self.write({"error": 0, "msg": "ok"})

    def delete(self, path_string):
        #删除项目
        pid = int(path_string[3:])
        if not bool(pid):
            return self.write({"error": 1, "msg": "missing pid"})
        pid = int(pid)
        _execute('''delete from projects where pid=%d ''' % pid)
        self.write({"error": 0, "msg": "ok"})

    def patch(self, path_string):
        #激活项目
        pid = int(path_string[3:])
        self._clear_active()
        _execute('''update projects set active=? where pid=?''', (1, pid))
        ACTIVE_PID = pid
        self.write({"error": 0, "msg": "ok"})

class ApiHandler(tornado.web.RequestHandler):

    def get(self, pid, *args):
        #apis列表|单独获取某个api
        if "/" in pid:
            pid, aid = pid.split("/")
            api = _execute("select * from apis where pid=%s and id=%s" % (pid, aid))
            print api
            self.render('api.html', api=api, title="查看API页面")
        else:
            apis = _execute("select * from apis where pid=%s" % (pid))
            self.render('apis.html', apis=apis, title="API管理页面")

    def post(self, pid, *args):
        #添加API
        pid = pid[:pid.index("/")] if "/" in pid else pid

        api_name = self.get_argument("name", "未命名接口")
        method = METHODS.get(self.get_argument("method", "get").lower(), 0)
        handler = self.get_argument("handler", "")
        data = self.get_argument("data", "{'foo': 'bar'}")
        exist = _execute('''select * from apis where pid=? and method=? and handler=?''', (int(pid), method, handler))
        if not bool(exist):
            _execute('''insert into apis (name, pid, method, data, handler) values (?, ?, ?, ?, ?) ''',
                     (api_name, int(pid), method, data, handler))
            self.write({"error": 0, "msg": "ok"})
        else:
            return self.write({"error": 1, "msg": "already exists"})

    def put(self, pid, *args):
        #修改API
        if "/" not in pid:
            return self.write({"error": 1, "msg": "argument error"})

        pid, aid = pid.split("/")
        api_name = self.get_argument("name", "未命名接口")
        method = METHODS.get(self.get_argument("method", "get").lower(), 0)
        handler = self.get_argument("handler", "")
        data = self.get_argument("data", "{'foo': 'bar'}")

        exist = _execute('''select * from apis where pid=? and method=? and handler=?''', (int(pid), method, handler))
        if bool(exist) and exist[0][0] != int(aid):
            return self.write({"error": 1, "msg": "already exists"})

        _execute('''update apis set name=?, method=?, data=?, handler=? where pid=? and id=?''',
                 (api_name, method, data, handler, int(pid), int(aid)))
        self.write({"error": 0, "msg": "ok"})


    def delete(self, pid_string, *args):
        #删除API
        pid, aid = pid_string.split("/")
        if bool(pid) and bool(aid):
            _execute('''delete from projects where pid=? and id=?''', (int(pid), int(aid)))
            self.write({"error": 0, "msg": "ok"})
        else:
            return self.write({"error": 1, "msg": "missing pid or aid"})

class Main(tornado.web.RequestHandler):
    def get(self):
        parse_result = urlparse.urlparse(self.request.uri)
        method = METHODS.get(self.request.method.lower(),None)
        handler = parse_result.path[1:]
        result = _execute('''select data from apis where pid=? and handler=? and method=?''',
                          (ACTIVE_PID, handler, method))
        if bool(result):
            self.write(result[0][0])
        else:
            return self.write({"error": 1, "msg": "not in record"})

    def post(self):
        self.get()

    def put(self):
        self.get()

    def patch(self):
        self.get()

    def delete(self):
        self.get()

    def copy(self):
        self.get()

    def head(self):
        self.get()

    def options(self):
        self.get()

    def link(self):
        self.get()

    def unlink(self):
        self.get()

    def purge(self):
        self.get()