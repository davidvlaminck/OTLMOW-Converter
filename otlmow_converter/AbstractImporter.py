import abc
from pathlib import Path
from typing import Iterable
from universalasync import async_to_sync_wraps
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject


class AbstractImporter(abc.ABC):
    @classmethod
    @abc.abstractmethod
    @async_to_sync_wraps
    async def to_objects(cls, filepath: Path, **kwargs) -> Iterable[OTLObject]:
        pass
