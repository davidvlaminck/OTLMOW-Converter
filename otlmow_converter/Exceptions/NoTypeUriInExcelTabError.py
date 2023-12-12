from pathlib import Path

from otlmow_converter.Exceptions.NoTypeUriInTableError import NoTypeUriInTableError


class NoTypeUriInExcelTabError(NoTypeUriInTableError):
    def __init__(self, message, file_path: Path, tab: str = None):
        super().__init__(message, file_path, tab=tab)
