#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals, absolute_import

import tornado.ioloop
import tornado.web
import json
import signal
import platform

import logging

_logger = logging.getLogger("findmyoctoprint.server")

class Handler(tornado.web.RequestHandler):

    def initialize(self, cors):
        self._cors = cors

    def set_default_headers(self):
        self.set_header("Server", "FindMyOctoPrint")
        self.set_header("Cache-Control", "no-cache")

    def _response(self, status_code, result, data=None):
        if data is None:
            data = dict()

        data["result"] = result

        self.set_status(status_code)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        if self._cors is not None:
            self.set_header("Access-Control-Allow-Origin", self._cors)
        self.write(json.dumps(data))

    def _success_response(self, status_code=None, data=None):
        if status_code is None:
            status_code = 200
        self._response(status_code, "success", data)

    def _error_response(self, status_code, data):
        self._response(status_code, "error", data)

    def _bad_request(self, reason):
        self._error_response(400, dict(reason=reason))

    def _remote_ip(self):
        # check X-Real-Ip and X-Forwarded-For headers before falling back to request client IP
        return self.request.headers.get("X-Real-Ip", self.request.headers.get("X-Forwarded-For", self.request.remote_ip))


class ApiHandler(Handler):

    def initialize(self, db, cors):
        Handler.initialize(self, cors)
        self._db = db

    def get(self, *args, **kwargs):
        remote_ip = self._remote_ip()
        candidates = self._db.candidates_for(remote_ip)
        self._success_response(data=dict(candidates=candidates,
                                         remote_ip=remote_ip))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body)
        if not isinstance(data, dict):
            self._bad_request("data is not an object")
            return

        if "uuid" not in data:
            self._bad_request("data does not contain uuid")
            return
        if "query" not in data:
            self._bad_request("data does not contain query")
            return
        if "urls" not in data:
            self._bad_request("data does not contain urls")

        remote_ip = self._remote_ip()
        self._db.record(remote_ip, data)
        self._success_response(data=dict(remote_ip=remote_ip))


class DumpHandler(Handler):
    """This should be limited to access from localhost in the used reverse proxy."""

    def initialize(self, db, cors):
        Handler.initialize(self, cors)
        self._db = db

    def get(self, *args, **kwargs):
        self._success_response(data=self._db.dump())


def run_server(port, db, address=None, cors=None, prefix=None):
    _logger.info("Starting Find My OctoPrint server...")

    import os
    static_web_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

    ioloop = tornado.ioloop.IOLoop()
    ioloop.install()

    def sigterm_handler(*args, **kwargs):
        # will stop tornado on SIGTERM, making the program exit cleanly
        def shutdown_tornado():
            ioloop.stop()

        ioloop.add_callback_from_signal(shutdown_tornado)
    signal.signal(signal.SIGTERM, sigterm_handler)

    app = tornado.web.Application([
        tornado.web.url(r"/registry", ApiHandler, dict(db=db, cors=cors)),
        tornado.web.url(r"/dump", DumpHandler, dict(db=db, cors=cors)),
        tornado.web.url(r"/(.*)", tornado.web.StaticFileHandler, dict(path=static_web_path,
                                                                      default_filename="index.html"))
    ])
    app.listen(port, address=address)

    if platform.system() == "Windows":
        # periodic no-op callback to allow us to detect Ctrl+C
        periodic_callback = tornado.ioloop.PeriodicCallback(lambda: None, 500, io_loop=ioloop)
        periodic_callback.start()

    _logger.info("Binding to {}:{}".format(address if address else "0.0.0.0", port))
    try:
        ioloop.start()
    except (KeyboardInterrupt, SystemExit):
        pass

    _logger.info("Goodbye...")
