import json
from pathlib import Path
from typing import Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from otlmow_converter.FileFormats.JsonLdContext import JsonLdContext


class JsonLdDecoder:
    @classmethod
    def decode_json_string(cls, json_string: str, ignore_failed_objects: bool = False, model_directory: Path = None,
                           allow_non_otl_conform_attributes: bool = True,
                           warn_for_non_otl_conform_attributes: bool = True,
                           waarde_shortcut: bool = True) -> Iterable[OTLObject]:
        dict_list = json.loads(json_string)
        context_dict = dict_list['@context'] if '@context' in dict_list else {}
        lijst = []

        for obj in dict_list['@graph']:
            try:
                rdf_dict = cls.transform_dict_to_rdf_dict(input_dict=obj, context_dict=context_dict)
                del rdf_dict['@id']
                del rdf_dict['@type']
                instance = OTLObject.from_dict(rdf_dict, model_directory=model_directory,
                                               waarde_shortcut=waarde_shortcut,
                                               cast_datetime=True, rdf=True,
                                               allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                               warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
                lijst.append(instance)
            except Exception as ex:
                if not ignore_failed_objects:
                    raise ex from ex
        return lijst

    @classmethod
    def transform_dict_to_rdf_dict(cls, input_dict: dict, context_dict: dict):
        new_dict = {}
        for k, v in input_dict.items():
            if ':' in k:
                k = JsonLdContext.replace_context(k, context_dict=context_dict)

            if isinstance(v, dict):
                v = cls.transform_dict_to_rdf_dict(v, context_dict=context_dict)
            elif isinstance(v, str) and v and ':' in v:
                v = JsonLdContext.replace_context(v, context_dict=context_dict)
            elif isinstance(v, list):
                value_list = []
                for list_item in v:
                    if isinstance(list_item, dict):
                        value_list.append(cls.transform_dict_to_rdf_dict(list_item, context_dict=context_dict))
                    elif isinstance(list_item, str) and list_item and ':' in list_item:
                        value_list.append(JsonLdContext.replace_context(list_item, context_dict=context_dict))
                    else:
                        value_list.append(list_item)
                v = value_list
            new_dict[k] = v
        return new_dict
