#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals, absolute_import

import time
import logging

_logger = logging.getLogger("findmyoctoprint.db")

class AbstractDb(object):

    def __init__(self, max_age):
        self._max_age = max_age

    def record(self, remote_ip, data):
        pass

    def candidates_for(self, remote_ip):
        return dict()

    def dump(self):
        return dict()


class InMemoryDb(AbstractDb):

    def __init__(self, *args, **kwargs):
        AbstractDb.__init__(self, *args, **kwargs)
        self._registry = dict()

    def record(self, remote_ip, data):
        candidates_for_ip = self._registry.get(remote_ip, dict())

        uuid = data["uuid"]
        data["_timestamp"] = time.time()
        candidates_for_ip[uuid] = data

        self._registry[remote_ip] = candidates_for_ip

    def candidates_for(self, remote_ip):
        self._cleanup(remote_ip)
        return self._registry.get(remote_ip, dict())

    def dump(self):
        self._cleanup_all()
        return self._registry

    def _cleanup_all(self):
        cutoff = time.time() - self._max_age

        for remote_ip in self._registry:
            self._cleanup(remote_ip, cutoff=cutoff)

    def _cleanup(self, remote_ip, cutoff=None):
        if remote_ip not in self._registry:
            return

        if cutoff is None:
            cutoff = time.time() - self._max_age

        self._registry[remote_ip] = dict((uuid, data)
                                         for uuid, data in self._registry[remote_ip].items()
                                         if data["_timestamp"] >= cutoff)
