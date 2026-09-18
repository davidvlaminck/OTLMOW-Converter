from typing import Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from rdflib.paths import Path

from otlmow_converter.AbstractExporter import AbstractExporter
from otlmow_converter.FileFormats.RDFExporter import RDFExporter
from otlmow_converter.SettingsManager import GlobalVariables, load_settings

load_settings()

ttl_settings = GlobalVariables.settings['formats']['ttl']
WAARDE_SHORTCUT = ttl_settings['waarde_shortcut']
ALLOW_NON_OTL_CONFORM_ATTRIBUTES = ttl_settings['allow_non_otl_conform_attributes']
WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES = ttl_settings['warn_for_non_otl_conform_attributes']
RDF_EXPORTER = RDFExporter(settings=ttl_settings)

class TtlExporter(AbstractExporter):


    @classmethod
    def from_objects(cls, sequence_of_objects: Iterable[OTLObject], filepath: Path, **kwargs) -> tuple[Path]:
        if filepath is None:
            raise ValueError(f'Can not write a file to: {filepath}')

        graph = RDF_EXPORTER.create_graph(sequence_of_objects)

        graph.serialize(destination=str(filepath))

    @classmethod
    async def from_objects_async(cls, sequence_of_objects: Iterable[OTLObject], filepath: Path, **kwargs) -> tuple[
        Path]:
        pass


