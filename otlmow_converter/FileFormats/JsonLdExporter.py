import json
import pyld
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
        jsonld_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'jsonld'), None)
        if jsonld_settings is None:
            raise ValueError("Unable to find jsonld in file formats settings")

        self.settings = jsonld_settings

        self.rdf_exporter = RDFExporter(dotnotation_settings=jsonld_settings['dotnotation'])

    def export_to_file(self, filepath: Path = None, list_of_objects: Iterable = None) -> None:
        if filepath is None:
            raise ValueError(f'Can not write a file to: {filepath}')

        graph = self.rdf_exporter.create_graph(list_of_objects)
        namespace_dict = {}
        for ns_prefix, namespace in graph.namespaces():
            namespace_dict[ns_prefix] = namespace

        # create a typelist to frame the json-ld
        q_res = graph.query("SELECT ?o WHERE { ?s a ?o }")
        type_lijst = []
        for row in q_res:
            type_lijst.append(str(row.o))

        json_ld = graph.serialize(format='json-ld', indent=4)
        json_ld = json.loads(json_ld)
        compacted = pyld.jsonld.compact(json_ld, {}, options={'graph': False})
        compacted = pyld.jsonld.frame(compacted, {
            '@context': namespace_dict,
            '@type': type_lijst})

        with open(str(filepath), "w") as out_file:
            json.dump(obj=compacted, fp=out_file, indent=4)

        # graph.serialize(destination=str(filepath), format='json-ld', indent=4)
