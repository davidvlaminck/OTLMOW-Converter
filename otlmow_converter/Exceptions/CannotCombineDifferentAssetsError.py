from pathlib import Path


class CannotCombineDifferentAssetsError(ValueError):
    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)
        self.object_id: str = None
        self.attribute_errors: [tuple] = None
        self.files: list[Path] = None
        self.type_uri: str = None
        self.message: str = None


class CannotCombineAssetsWithDifferentIdError(CannotCombineDifferentAssetsError):
    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)


class CannotCombineAssetsWithDifferentTypeError(CannotCombineDifferentAssetsError):
    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)
