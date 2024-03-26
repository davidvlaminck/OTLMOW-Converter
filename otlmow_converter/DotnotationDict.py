class DotnotationDict(dict[str, object]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        if key.startswith('_') :
            raise ValueError(f'{key} is a non standardized attribute of {self.__class__.__name__}. '
                             f'While this is supported, the key can not start with "_".')
        self[key] = value

    def __delattr__(self, item):
        try:
            del self[item]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)