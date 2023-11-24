import json
from collections import OrderedDict
from typing import Dict

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, create_dict_from_asset


class OtlAssetJSONLDEncoder(json.JSONEncoder):
    def __init__(self, indent=None, settings=None):
        super().__init__(indent=indent)
        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        json_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'jsonld'), None)
        if json_settings is None:
            raise ValueError("Unable to find json in file formats settings")

        self.settings = json_settings

    @staticmethod
    def create_ld_dict_from_asset(otl_object: OTLObject, waarde_shortcut=False) -> Dict:
        """Creates a dictionary from an OTLObject"""
        if otl_object.assetId is None or otl_object.assetId.identificator is None:
            raise ValueError('JSON-LD requires the assetId.identificator to not be None.')

        d = create_dict_from_asset(otl_object, waarde_shortcut=waarde_shortcut, rdf=True)
        if d is None:
            return {}
        # ns, name = get_ns_and_name_from_uri(otl_object.typeURI)
        # encoded_uri = encode_short_uri(f'{ns}#{name}')
        aim_id = f'https://data.awvvlaanderen.be/id/asset/{otl_object.assetId.identificator}'
        d['@id'] = aim_id
        return d

    def default(self, otl_object):
        if isinstance(otl_object, OTLObject):
            d = self.create_ld_dict_from_asset(
                otl_object, waarde_shortcut=self.settings['dotnotation']['waarde_shortcut'])
            # TODO should no longer be required
            if hasattr(otl_object, 'typeURI'):
                d['https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.typeURI'] = otl_object.typeURI
            od = OrderedDict(sorted(d.items()))
            return od
        return super().default(otl_object)

    # no usage?
    @classmethod
    def isEmptyDict(cls, value: dict):
        for v in value.values():
            if isinstance(v, dict):
                if cls.isEmptyDict(v):
                    continue
            if v is not None and v != []:
                return False
        return True

    @staticmethod
    def write_json_to_file(encoded_json, file_path):
        with open(file_path, "w") as file:
            file.write(encoded_json)
