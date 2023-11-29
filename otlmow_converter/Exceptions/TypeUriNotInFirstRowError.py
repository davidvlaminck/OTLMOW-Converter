from pathlib import Path

from otlmow_converter.Exceptions.FailedToImportFileError import FailedToImportFileError


class TypeUriNotInFirstRowError(FailedToImportFileError):
    def __init__(self, message, file_path: Path, tab: str = None):
        super().__init__(message, file_path)
        self.file_path = file_path
        self.tab = tab
