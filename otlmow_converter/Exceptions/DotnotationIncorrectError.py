from pathlib import Path
from typing import Optional

from otlmow_converter.Exceptions.FailedToImportFileError import FailedToImportFileError


class DotnotationIncorrectError(FailedToImportFileError):
    def __init__(self, message: str, file_path: Path, tab: Optional[str] = None,
                 header: Optional[str] = None, expected_header: Optional[str] = None):
        super().__init__(message, file_path)
        self.file_path = file_path
        self.tab = tab
        self.header = header
        self.expected_header = expected_header