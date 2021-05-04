#!/usr/bin/env python

import click
import logging

MAX_AGE = 1 * 60 * 60 # 1h


def _initialize_logging():
    import logging.config

    config = {
        "version": 1,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "tornado.application": {
                "level": "INFO"
            },
            "tornado.general": {
                "level": "INFO"
            },
            "findmyoctoprint": {
                "level": "INFO"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }

    logging.config.dictConfig(config)
    logging.captureWarnings(True)

    import warnings
    warnings.simplefilter("always")


@click.command("findmyoctoprint")
@click.option("--address", default="0.0.0.0", help="The host under which to run")
@click.option("--port", default=5000, help="The port under which to run")
@click.option("--cors", default=None, help="Setting for Allowed-Origin-Host CORS header")
def main(address=None, port=5000, cors=None):
    from server import run_server
    from db import InMemoryDb

    _initialize_logging()

    db = InMemoryDb(MAX_AGE)

    run_server(port, db, address=address, cors=cors)

if __name__ == "__main__":
    main()