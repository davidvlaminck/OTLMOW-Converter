class DotnotationListOfListError(ValueError):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

