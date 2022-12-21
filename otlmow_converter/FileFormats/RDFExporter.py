from typing import Dict, Iterable

from otlmow_model.BaseClasses.FloatOrDecimalField import FloatOrDecimalField
from otlmow_model.BaseClasses.KeuzelijstField import KeuzelijstField
from rdflib import Graph, FOAF, URIRef, BNode, Literal, RDF, XSD


class RDFExporter:
    def __init__(self, dotnotation_settings: Dict = None):

        if dotnotation_settings is None:
            dotnotation_settings = {}
        self.settings = dotnotation_settings

        for required_attribute in ['waarde_shortcut_applicable']:
            if required_attribute not in self.settings:
                raise ValueError("The settings are not loaded or don't contain the full dotnotation settings")

    def create_graph(self, list_of_objects: Iterable = None) -> Graph:
        g = Graph()
        for ns, namespace in {'foaf': FOAF,
                              'imel': 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#',
                              'asset': 'https://data.awvvlaanderen.be/id/asset/',
                              'assetrelatie': 'https://data.awvvlaanderen.be/id/assetrelatie/',
                              'onderdeel': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#',
                              'installatie': 'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#',
                              'keuzelijst': 'https://wegenenverkeer.data.vlaanderen.be/id/concept/',
                              'loc': 'https://loc.data.wegenenverkeer.be/ns/implementatieelement#'}.items():
            g.bind(ns, namespace)

        for instance in list_of_objects:
            if instance.assetId is None or instance.assetId.identificator is None or \
                    instance.assetId.identificator == '':
                raise ValueError('Can not export assets without a valid assetId')

            if not hasattr(instance, 'typeURI') or instance.typeURI is None or instance.typeURI == '':
                raise ValueError(f'Can not export invalid objects: {instance}')

            asset = URIRef('https://data.awvvlaanderen.be/id/asset/' + instance.assetId.identificator)
            type_node = URIRef(instance.typeURI)
            g.add((asset, RDF.type, type_node))

            # if isinstance(instance, RelatieObject):
            #     g.add((asset, URIRef('https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#bron'),
            #            URIRef('https://data.awvvlaanderen.be/id/asset/' + instance.bronAssetId.identificator)))
            #     g.add((asset, URIRef('https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#doel'),
            #            URIRef('https://data.awvvlaanderen.be/id/asset/' + instance.doelAssetId.identificator)))

            self._add_attributes_to_graph(graph=g, asset_or_attribute=instance, asset_attribute_ref=asset)

        return g

    def _add_attributes_to_graph(self, graph, asset_or_attribute, asset_attribute_ref):
        keys = list(filter(lambda k: k[0] == '_', vars(asset_or_attribute).keys()))

        for key in keys:
            if key in ['_valid_relations', '_parent', '_geometry_types']:  # TODO fix geometry
                continue

            attribute = getattr(asset_or_attribute, key)
            if attribute.waarde is None:
                continue

            if attribute.field.waardeObject is not None:
                if attribute.kardinaliteit_max != '1':
                    for waarde_item in attribute.waarde:
                        waarde_object = BNode()
                        graph.add((asset_attribute_ref, URIRef(attribute.objectUri), waarde_object))
                        self._add_attributes_to_graph(graph=graph, asset_or_attribute=waarde_item,
                                                      asset_attribute_ref=waarde_object)
                else:
                    waarde_object = BNode()
                    graph.add((asset_attribute_ref, URIRef(attribute.objectUri), waarde_object))
                    self._add_attributes_to_graph(graph=graph, asset_or_attribute=attribute.waarde,
                                                  asset_attribute_ref=waarde_object)
                continue

            if attribute.kardinaliteit_max != '1':
                for waarde_item in attribute.waarde:
                    if issubclass(attribute.field, KeuzelijstField):
                        graph.add((asset_attribute_ref, URIRef(attribute.objectUri),
                                   URIRef(attribute.field.options[waarde_item].objectUri)))
                    elif issubclass(attribute.field, FloatOrDecimalField):
                        graph.add((asset_attribute_ref, URIRef(attribute.objectUri), Literal(waarde_item, datatype=XSD.decimal)))
                    else:
                        graph.add((asset_attribute_ref, URIRef(attribute.objectUri), Literal(waarde_item)))
            else:
                if issubclass(attribute.field, KeuzelijstField):
                    graph.add((asset_attribute_ref, URIRef(attribute.objectUri),
                               URIRef(attribute.field.options[attribute.waarde].objectUri)))
                elif issubclass(attribute.field, FloatOrDecimalField):
                    graph.add((asset_attribute_ref, URIRef(attribute.objectUri), Literal(attribute.waarde, datatype=XSD.decimal)))
                else:
                    graph.add((asset_attribute_ref, URIRef(attribute.objectUri), Literal(attribute.waarde)))
