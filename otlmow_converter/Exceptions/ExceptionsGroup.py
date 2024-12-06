from typing import Sequence


class ExceptionsGroup(Exception):
    def __init__(self, message, exceptions: Sequence[BaseException] = None, objects: Sequence = None):
        super().__init__(message)
        if exceptions is None:
            exceptions = []
        self.exceptions = exceptions
        self.objects = []

    def add_exception(self, error: BaseException):
        self.exceptions.append(error)

    def __str__(self):
        return (f'ExceptionGroup with {len(self.exceptions)} error(s): ' +
                ('\n'.join([str(error) for error in self.exceptions])))

