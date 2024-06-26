import json
from pathlib import Path
from typing import Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject


class JsonDecoder:
    @classmethod
    def decode_json_string(cls, json_string: str, ignore_failed_objects: bool=False, model_directory: Path=None,
                           allow_non_otl_conform_attributes: bool=True, warn_for_non_otl_conform_attributes: bool=True,
                           waarde_shortcut: bool=True) -> Iterable[OTLObject]:
        dict_list = json.loads(json_string)
        object_list = []
        for index, obj in enumerate(dict_list):
            try:
                type_uri = obj.get('typeURI', None)
                if type_uri is None:
                    raise ValueError(f"No typeURI found in json object {index}. Unable to create object.")

                instance = OTLObject.from_dict(obj, model_directory=model_directory, waarde_shortcut=waarde_shortcut,
                                               cast_datetime=True,
                                               allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                               warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
                object_list.append(instance)

            except Exception as ex:
                if not ignore_failed_objects:
                    raise ex from ex
        return object_list


