from pathlib import Path


class CannotCombineAssetsError(ValueError):
    def __init__(self, message):
        super().__init__(message)
        self.object_id: str
        self.attribute_errors: [tuple] = None
        self.files: list[Path]
        self.type_uri: str
        self.message: str
