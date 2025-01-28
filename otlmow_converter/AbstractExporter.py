import abc
from pathlib import Path
from typing import Iterable
from universalasync import async_to_sync_wraps
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject


class AbstractExporter(abc.ABC):
    @classmethod
    @abc.abstractmethod
    @async_to_sync_wraps
    def from_objects(cls, sequence_of_objects: Iterable[OTLObject], filepath: Path, **kwargs) -> None:
        pass


