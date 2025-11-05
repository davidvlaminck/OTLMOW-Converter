from pathlib import Path
from typing import Sequence

from otlmow_converter.Exceptions.ErrorInExcelLine import ErrorInExcelLine
from otlmow_converter.Exceptions.FailedToImportFileError import FailedToImportFileError


class BadLinesInExcelError(FailedToImportFileError):
    def __init__(self, message: str = '', file_path: Path = None, tab: str = None, exceptions: Sequence[ErrorInExcelLine] = None, objects: Sequence = None):
        super().__init__(message, file_path)
        self.tab = tab
        if exceptions is None:
            exceptions = []
        self.exceptions = exceptions
        self.objects = objects

    def add_exception(self, error: BaseException):
        self.exceptions.append(error)

    def __str__(self):
        return (f'BadLinesInExcelError in file {self.file_path} tab {self.tab} with {len(self.exceptions)} error(s).\n'
                f'Note that the line numbers are not including header lines' +
                ('\n'.join([str(error) for error in self.exceptions])))