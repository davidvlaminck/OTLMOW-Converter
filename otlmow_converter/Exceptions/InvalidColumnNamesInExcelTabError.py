from pathlib import Path
from typing import List

from otlmow_converter.Exceptions.FailedToImportFileError import FailedToImportFileError


class InvalidColumnNamesInExcelTabError(FailedToImportFileError):
    def __init__(self, message, file_path: Path, tab: str = None, bad_columns: List[str] = None):
        super().__init__(message, file_path)
        self.file_path = file_path
        self.tab = tab
        if bad_columns is None:
            bad_columns = []
        self.bad_columns = bad_columns
