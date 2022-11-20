import logging


class BadTypeWarning(RuntimeWarning):
    def __init__(self, msg):
        logging.warning(msg)
