from otlmow_model.BaseClasses.KeuzelijstField import KeuzelijstField
from otlmow_model.Classes.ImplementatieElement.AIMObject import AIMObject
from rdflib import Graph, FOAF, URIRef, BNode, Literal, RDF
from rdflib.paths import Path


class TtlExporter:
    def __init__(self, settings=None, class_directory: str = None, ignore_empty_asset_id: bool = False):
        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        csv_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'csv'), None)
        if csv_settings is None:
            raise ValueError("Unable to find csv in file formats settings")

        self.settings = csv_settings

    def export_to_file(self, filepath: Path = None, list_of_objects: list[AIMObject] = None, **kwargs) -> None:
        if filepath is None:
            raise ValueError(f'Can not write a file to: {filepath}')

        g = Graph()
        g.bind("foaf", FOAF)

        for instance in list_of_objects:
            asset = URIRef('https://data.awvvlaanderen.be/id/asset/' + instance.assetId.identificator)
            type_node = URIRef(instance.typeURI)

            g.add((asset, RDF.type, type_node))
            
            self.add_attributes_to_graph(graph=g, asset_or_attribute=instance, asset_attribute_ref=asset)

            bob = URIRef("http://example.org/people/Bob")
            linda = BNode()  # a GUID is generated

            name = Literal("Bob")
            age = Literal(24)

            # g.add((bob, RDF.type, FOAF.Person))
            # g.add((bob, FOAF.name, name))
            # g.add((bob, FOAF.age, age))
            # g.add((bob, FOAF.knows, linda))
            # g.add((linda, RDF.type, FOAF.Person))
            # g.add((linda, FOAF.name, Literal("Linda")))

        print(g.serialize())

    def add_attributes_to_graph(self, graph, asset_or_attribute, asset_attribute_ref):
        keys = list(filter(lambda k:k[0] == '_', vars(asset_or_attribute).keys()))
        print(keys)

        for key in keys:
            if key == '_valid_relations':
                continue

            attribute = getattr(asset_or_attribute, key)
            if attribute.waarde is None:
                continue

            if attribute.field.waardeObject is not None:
                continue

            if attribute.kardinaliteit_max != '1':
                for waarde_item in attribute.waarde:
                    if issubclass(attribute.field, KeuzelijstField):
                        graph.add((asset_attribute_ref, URIRef(attribute.objectUri),
                                   URIRef(attribute.field.options[waarde_item].objectUri)))                
                    else:
                        graph.add((asset_attribute_ref, URIRef(attribute.objectUri), Literal(waarde_item)))
            else:
                if issubclass(attribute.field, KeuzelijstField):
                    graph.add((asset_attribute_ref, URIRef(attribute.objectUri),
                               URIRef(attribute.field.options[attribute.waarde].objectUri)))
                else:
                    graph.add((asset_attribute_ref, URIRef(attribute.objectUri), Literal(attribute.waarde)))

            print(attribute)
