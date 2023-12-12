from pathlib import Path


class FailedToImportFileError(BaseException):
    def __init__(self, message, file_path: Path = None):
        super().__init__(message)
        self.file_path = file_path
