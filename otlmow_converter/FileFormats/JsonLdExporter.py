from typing import Iterable

from rdflib.paths import Path

from otlmow_converter.FileFormats.RDFExporter import RDFExporter


class JsonLdExporter:
    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        ttl_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'ttl'), None)
        if ttl_settings is None:
            raise ValueError("Unable to find ttl in file formats settings")

        self.settings = ttl_settings

        self.rdf_exporter = RDFExporter(dotnotation_settings=ttl_settings['dotnotation'])

    def export_to_file(self, filepath: Path = None, list_of_objects: Iterable = None) -> None:
        if filepath is None:
            raise ValueError(f'Can not write a file to: {filepath}')

        graph = self.rdf_exporter.create_graph(list_of_objects)

        graph.serialize(destination=str(filepath), format='json-ld', indent=4)
