from abc import abstractmethod
from typing import Generator


class WaardenObject:
    @abstractmethod
    def __init__(self):
        self._parent = None

    def __iter__(self) -> Generator:
        for k, v in vars(self).items():
            if k in ['_parent', '_geometry_types', '_valid_relations']:
                continue
            yield v
