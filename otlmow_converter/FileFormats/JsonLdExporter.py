import json
from json import JSONEncoder
from pathlib import Path
from typing import Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, create_dict_from_asset
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import is_relation

from otlmow_converter.AbstractExporter import AbstractExporter
from otlmow_converter.FileFormats.JsonLdContext import JsonLdContext
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

load_settings()

jsonld_settings = GlobalVariables.settings['formats']['JSON-LD']
WAARDE_SHORTCUT = jsonld_settings['waarde_shortcut']
ALLOW_NON_OTL_CONFORM_ATTRIBUTES = jsonld_settings['allow_non_otl_conform_attributes']
WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES = jsonld_settings['warn_for_non_otl_conform_attributes']


class JsonLdExporter(AbstractExporter):
    @classmethod
    def from_objects(cls, sequence_of_objects: Iterable[OTLObject], filepath: Path, **kwargs) -> None:
        waarde_shortcut = kwargs.get('waarde_shortcut', WAARDE_SHORTCUT)
        allow_non_otl_conform_attributes = kwargs.get('allow_non_otl_conform_attributes',
                                                      ALLOW_NON_OTL_CONFORM_ATTRIBUTES)
        warn_for_non_otl_conform_attributes = kwargs.get('warn_for_non_otl_conform_attributes',
                                                         WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES)

        model_directory = None
        if 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']

        list_of_objects = []
        for asset in sequence_of_objects:
            d = create_dict_from_asset(asset, rdf=True, cast_datetime=True, waarde_shortcut=waarde_shortcut,
                                       allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                       warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
            d['@type'] = asset.typeURI
            d['https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.typeURI'] = asset.typeURI
            if asset.assetId.identificator is None:
                raise ValueError(f'No identificator found for asset: {d}')
            else:
                if is_relation(asset, model_directory):
                    d['@id'] = 'https://data.awvvlaanderen.be/id/assetrelatie/' + asset.assetId.identificator
                else:
                    d['@id'] = 'https://data.awvvlaanderen.be/id/asset/' + asset.assetId.identificator
            list_of_objects.append(d)

        graph_dict = {'@graph': (list_of_objects if isinstance(list_of_objects, list) else [list_of_objects])}

        encoded_json = JSONEncoder(indent=4).encode(graph_dict)
        encoded_json = cls.modify_jsonld_for_context(encoded_json)

        with open(filepath, "w") as file:
            file.write(encoded_json)

    @classmethod
    def modify_jsonld_for_context(cls, encoded_json: str):
        orig_context_dict = JsonLdContext.context_dict
        new_context_dict = {}
        for short, long in orig_context_dict.items():
            if long in encoded_json:
                new_context_dict[short] = long
                encoded_json = encoded_json.replace(long, f'{short}:')

        encoded_json = encoded_json.replace('"@graph"',
                                            f'"@context": {json.dumps(new_context_dict, indent=4)},\n"@graph"')
        return encoded_json
