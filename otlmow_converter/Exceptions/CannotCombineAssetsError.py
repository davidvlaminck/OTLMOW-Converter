from pathlib import Path


class CannotCombineAssetsError(ValueError):
    def __init__(self, message):
        super().__init__(message)
        self.object_id: str = None
        self.attribute_errors: [tuple] = None
        self.files: list[Path] = None
        self.type_uri: str = None
        self.message: str = None
