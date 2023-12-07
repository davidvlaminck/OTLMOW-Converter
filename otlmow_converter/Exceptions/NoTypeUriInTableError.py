from pathlib import Path

from otlmow_converter.Exceptions.FailedToImportFileError import FailedToImportFileError


class NoTypeUriInTableError(FailedToImportFileError):
    def __init__(self, message: str = '', file_path: Path = None, tab: str = None):
        super().__init__(message, file_path)
        self.tab = tab
