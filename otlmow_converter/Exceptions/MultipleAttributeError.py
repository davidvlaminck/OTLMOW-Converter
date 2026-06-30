from typing import Sequence

from otlmow_converter.Exceptions.OTLAttributeError import OTLAttributeError


class MultipleAttributeError(Exception):
    def __init__(self, message, exceptions: Sequence[OTLAttributeError] = None):
        super().__init__(message)
        if exceptions is None:
            exceptions = []
        self.exceptions = exceptions

    def add_exception(self, error: OTLAttributeError):
        self.exceptions.append(error)

    def __str__(self):
        return (f'MultipleAttributeError with {len(self.exceptions)} error(s):\n' +
                ('\n'.join([('- ' + str(error)) for error in self.exceptions])))

