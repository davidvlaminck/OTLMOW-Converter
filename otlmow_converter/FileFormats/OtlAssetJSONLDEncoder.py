import json
from collections import OrderedDict
from datetime import date, datetime, time
from typing import Dict, Union, List

from otlmow_model.BaseClasses.DateField import DateField
from otlmow_model.BaseClasses.DateTimeField import DateTimeField
from otlmow_model.BaseClasses.KeuzelijstField import KeuzelijstField
from otlmow_model.BaseClasses.OTLAttribuut import OTLAttribuut
from otlmow_model.BaseClasses.OTLObject import OTLObject
from otlmow_model.BaseClasses.TimeField import TimeField


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

    def create_ld_dict_from_asset(self, otl_object: OTLObject, waarde_shortcut=False) -> Dict:
        """Creates a dictionary from an OTLObject"""
        if otl_object.assetId is None or otl_object.assetId.identificator is None:
            raise ValueError('JSON-LD requires the assetId.identificator to not be None.')

        d = self._recursive_create_ld_dict_from_asset(otl_object, waarde_shortcut=waarde_shortcut)
        if d is None:
            return {}
        # ns, name = get_ns_and_name_from_uri(otl_object.typeURI)
        # encoded_uri = encode_short_uri(f'{ns}#{name}')
        aim_id = f'https://data.awvvlaanderen.be/id/asset/{otl_object.assetId.identificator}'
        d['@id'] = aim_id
        d['@type'] = otl_object.typeURI
        return d

    def _recursive_create_ld_dict_from_asset(self, asset: Union[OTLObject, OTLAttribuut, list, dict],
                                             waarde_shortcut: bool = False) -> Union[Dict, List[Dict]]:
        if isinstance(asset, list) and not isinstance(asset, dict):
            l = []
            for item in asset:
                dict_item = self._recursive_create_ld_dict_from_asset(asset=item, waarde_shortcut=waarde_shortcut)
                if dict_item is not None:
                    l.append(dict_item)
            if len(l) > 0:
                return l
        else:
            d = {}
            for k, v in vars(asset).items():
                if k in ['_parent', '_geometry_types', '_valid_relations']:
                    continue
                if v.waarde is None or v.waarde == []:
                    continue

                if v.field.waardeObject is not None:  # complex
                    if waarde_shortcut and v.field.waarde_shortcut_applicable:
                        if isinstance(v.waarde, list):
                            dict_item_list = [item.waarde for item in v.waarde]
                            if len(dict_item_list) > 0:
                                d[v.objectUri] = dict_item_list
                        else:
                            dict_item = v.waarde.waarde
                            if dict_item is not None:
                                d[v.objectUri] = dict_item
                    else:
                        dict_item = self._recursive_create_ld_dict_from_asset(asset=v.waarde,
                                                                              waarde_shortcut=waarde_shortcut)
                        if dict_item is not None:
                            d[v.objectUri] = dict_item
                else:
                    if isinstance(v.waarde, list):
                        dict_item_list = []
                        for item in v.waarde:
                            if v.field == TimeField:
                                dict_item_list.append(time.strftime(item, "%H:%M:%S"))
                            elif v.field == DateField:
                                dict_item_list.append(date.strftime(item, "%Y-%m-%d"))
                            elif v.field == DateTimeField:
                                dict_item_list.append(datetime.strftime(item, "%Y-%m-%d %H:%M:%S"))
                            elif issubclass(v.field, KeuzelijstField):
                                dict_item_list.append(v.field.options[item].objectUri)
                            else:
                                dict_item_list.append(item)
                        if len(dict_item_list) > 0:
                            d[v.objectUri] = dict_item_list
                    else:
                        if v.field == TimeField:
                            d[v.objectUri] = time.strftime(v.waarde, format="%H:%M:%S")
                        elif v.field == DateField:
                            d[v.objectUri] = date.strftime(v.waarde, "%Y-%m-%d")
                        elif v.field == DateTimeField:
                            d[v.objectUri] = datetime.strftime(v.waarde, "%Y-%m-%d %H:%M:%S")
                        elif issubclass(v.field, KeuzelijstField):
                            d[v.objectUri] = v.field.options[v.waarde].objectUri
                        else:
                            d[v.objectUri] = v.waarde

            if len(d.items()) > 0:
                return d

    def default(self, otl_object):
        if isinstance(otl_object, OTLObject):
            d = self.create_ld_dict_from_asset(
                otl_object, waarde_shortcut=self.settings['dotnotation']['waarde_shortcut_applicable'])
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