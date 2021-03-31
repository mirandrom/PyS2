__version__ = "1.1.0"

import logging
from s2 import api, models


def _setup_logger():
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s\t%(levelname)s %(filename)s:%(lineno)s -- %(message)s"
        ))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


_setup_logger()
