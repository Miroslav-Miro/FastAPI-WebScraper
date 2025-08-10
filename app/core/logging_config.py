"""
Logging configuration for the Web Scraper API.

Sets up the root logger with a stream handler outputting to stdout,
configures the logging level based on environment variables,
and adjusts logging verbosity for external libraries.
"""

import logging
import os
import sys


def configure_logging() -> None:
    """
    Configure application-wide logging settings.

    - Sets log level from the LOG_LEVEL environment variable (default INFO).
    - Clears any existing handlers and attaches a StreamHandler to stdout.
    - Applies a consistent log message format with timestamps and logger names.
    - Sets urllib3 logging to WARNING level to reduce noise.
    - Adjusts SQLAlchemy engine logging verbosity based on SQLALCHEMY_ECHO environment variable.
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s %(name)s - %(message)s")
    )
    root.addHandler(h)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine.Engine").setLevel(
        logging.INFO if os.getenv("SQLALCHEMY_ECHO") == "1" else logging.WARNING
    )
