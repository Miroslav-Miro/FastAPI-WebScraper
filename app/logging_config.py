import logging
import os
import sys


def configure_logging() -> None:
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
