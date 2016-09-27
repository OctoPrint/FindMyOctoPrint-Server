#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

INSTALL_REQUIRES = [
    "tornado",
    "click",
    "markupsafe"
]

def package_data_dirs(source, sub_folders):
    import os
    dirs = []

    for d in sub_folders:
        folder = os.path.join(source, d)
        if not os.path.exists(folder):
            continue

        for dirname, _, files in os.walk(folder):
            dirname = os.path.relpath(dirname, source)
            for f in files:
                dirs.append(os.path.join(dirname, f))

    return dirs


def params():
    name = "FindMyOctoPrint-Server"
    version = "1.0"

    description = "Discovery server for OctoPrint"

    install_requires = INSTALL_REQUIRES

    author = "Gina Häußge"
    author_email = "osd@foosel.net"

    packages = ["findmyoctoprint_server"]
    package_data = dict(findmyoctoprint_server=package_data_dirs("findmyoctoprint_server", ["static"]))

    zip_safe = False

    entry_points = dict(console_scripts=["findmyoctoprint=findmyoctoprint_server:main"])

    return locals()

setup(**params())
