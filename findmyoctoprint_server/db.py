#!/usr/bin/env python


import time
import logging
import threading

_logger = logging.getLogger("findmyoctoprint.db")

class AbstractDb:

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
        self._registry_mutex = threading.RLock()

    def record(self, remote_ip, data):
        candidates_for_ip = self._registry.get(remote_ip, dict())

        uuid = data["uuid"]
        data["_timestamp"] = time.time()
        candidates_for_ip[uuid] = data

        with self._registry_mutex:
            self._registry[remote_ip] = candidates_for_ip

    def candidates_for(self, remote_ip):
        self._cleanup(remote_ip)
        with self._registry_mutex:
            return self._registry.get(remote_ip, dict())

    def dump(self):
        self._cleanup_all()
        with self._registry_mutex:
            return self._registry

    def _cleanup_all(self):
        cutoff = time.time() - self._max_age

        with self._registry_mutex:
            for remote_ip in self._registry:
                try:
                    self._cleanup(remote_ip, cutoff=cutoff)
                except:
                    _logger.exception(f"Error while trying to clean up registry for {remote_ip}")

    def _cleanup(self, remote_ip, cutoff=None):
        if remote_ip not in self._registry:
            return

        if cutoff is None:
            cutoff = time.time() - self._max_age

        with self._registry_mutex:
            self._registry[remote_ip] = {uuid: data
                                             for uuid, data in self._registry[remote_ip].items()
                                             if data["_timestamp"] >= cutoff}
