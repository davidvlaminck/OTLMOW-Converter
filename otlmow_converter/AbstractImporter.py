import abc
from pathlib import Path
from typing import Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject


class AbstractImporter(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def to_objects(cls, filepath: Path, **kwargs) -> Iterable[OTLObject]:
        pass
