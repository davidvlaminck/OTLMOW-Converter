import abc
from pathlib import Path
from typing import Iterable, AsyncIterable
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject


class AbstractImporter(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def to_objects(cls, filepath: Path, **kwargs) -> Iterable[OTLObject]:
        pass

    @classmethod
    @abc.abstractmethod
    async def to_objects_async(cls, filepath: Path, **kwargs) -> AsyncIterable[OTLObject]:
        pass

