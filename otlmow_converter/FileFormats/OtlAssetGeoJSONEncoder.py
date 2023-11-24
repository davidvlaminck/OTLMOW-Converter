import json
from collections import OrderedDict
from pathlib import Path

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject


class OtlAssetGeoJSONEncoder(json.JSONEncoder):
    def __init__(self, indent=None, settings=None):
        super().__init__(indent=indent)
        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        json_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'geojson'), None)
        if json_settings is None:
            raise ValueError("Unable to find json in file formats settings")

        self.settings = json_settings

    def default(self, otl_object):
        if isinstance(otl_object, OTLObject):
            d = otl_object.create_dict_from_asset(
                waarde_shortcut=self.settings['dotnotation']['waarde_shortcut'])
            if hasattr(otl_object, 'typeURI'):
                d['typeURI'] = otl_object.typeURI
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
    def write_json_to_file(encoded_json, file_path: Path):
        with open(file_path, "w") as file:
            file.write(encoded_json)
