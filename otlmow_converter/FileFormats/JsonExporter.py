from json import JSONEncoder
from pathlib import Path
from typing import Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, create_dict_from_asset

from otlmow_converter.AbstractExporter import AbstractExporter
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

load_settings()

json_settings = GlobalVariables.settings['formats']['JSON']
WAARDE_SHORTCUT = json_settings['waarde_shortcut']
ALLOW_NON_OTL_CONFORM_ATTRIBUTES = json_settings['allow_non_otl_conform_attributes']
WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES = json_settings['warn_for_non_otl_conform_attributes']

class JsonExporter(AbstractExporter):
    @classmethod
    def from_objects(cls, sequence_of_objects: Iterable[OTLObject], filepath: Path, **kwargs) -> None:
        waarde_shortcut = kwargs.get('waarde_shortcut', WAARDE_SHORTCUT)
        allow_non_otl_conform_attributes = kwargs.get('allow_non_otl_conform_attributes',
                                                      ALLOW_NON_OTL_CONFORM_ATTRIBUTES)
        warn_for_non_otl_conform_attributes = kwargs.get('warn_for_non_otl_conform_attributes',
                                                         WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES)

        list_of_objects = []
        for asset in sequence_of_objects:
            d = create_dict_from_asset(asset, cast_datetime=True, waarde_shortcut=waarde_shortcut,
                                       allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                       warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
            d['typeURI'] = asset.typeURI
            list_of_objects.append(d)

        encoded_json = JSONEncoder(indent=4).encode(list_of_objects)

        with open(filepath, "w") as file:
            file.write(encoded_json)
