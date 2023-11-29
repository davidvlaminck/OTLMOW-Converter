import logging
from pathlib import Path


class FailedToImportFileError(BaseException):
    def __init__(self, message, file_path: Path):
        super().__init__(message)
        self.file_path = file_path
        logging.error(f'Failed to import file: {file_path} with error: {message}')
