import logging


class UnexpectedIfcTypeWarning(UserWarning):
    def __init__(self, msg):
        logging.warning(msg)