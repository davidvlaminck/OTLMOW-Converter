from pathlib import Path
from typing import Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from otlmow_converter.AbstractImporter import AbstractImporter
from otlmow_converter.FileFormats.JsonLdDecoder import JsonLdDecoder
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

load_settings()

jsonld_settings = GlobalVariables.settings['formats']['JSON-LD']
WAARDE_SHORTCUT = jsonld_settings['waarde_shortcut']
ALLOW_NON_OTL_CONFORM_ATTRIBUTES = jsonld_settings['allow_non_otl_conform_attributes']
WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES = jsonld_settings['warn_for_non_otl_conform_attributes']


class JsonLdImporter(AbstractImporter):
    @classmethod
    def to_objects(cls, filepath: Path, **kwargs) -> Iterable[OTLObject]:
        """Imports a json file created with Davie and decodes it to OTL objects

        :param filepath: location of the file to import
        :type: Path
        :rtype: list
        :return: returns a list of OTL objects
        """

        waarde_shortcut = kwargs.get('waarde_shortcut', WAARDE_SHORTCUT)
        allow_non_otl_conform_attributes = kwargs.get('allow_non_otl_conform_attributes',
                                                      ALLOW_NON_OTL_CONFORM_ATTRIBUTES)
        warn_for_non_otl_conform_attributes = kwargs.get('warn_for_non_otl_conform_attributes',
                                                         WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES)

        if filepath is None:
            raise ValueError(f'Can not write a file to: {filepath}')

        model_directory = None
        if kwargs is not None and 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']

        ignore_failed_objects = False

        if kwargs is not None and 'ignore_failed_objects' in kwargs:
            ignore_failed_objects = kwargs['ignore_failed_objects']

        data = Path(filepath).read_text()
        return JsonLdDecoder.decode_json_string(
            json_string=data, ignore_failed_objects=ignore_failed_objects,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
            model_directory=model_directory, waarde_shortcut=waarde_shortcut)
