import json
from pathlib import Path

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import set_value_by_dictitem, dynamic_create_instance_from_uri


class JsonDecoder:
    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        json_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'json'), None)
        if json_settings is None:
            raise ValueError("Unable to find json in file formats settings")

        self.settings = json_settings

    def decode_json_string(self, jsonString, ignore_failed_objects=False, model_directory: Path = None):
        dict_list = json.loads(jsonString)
        lijst = []
        for obj in dict_list:
            try:
                typeURI = next(value for key, value in obj.items() if 'typeURI' in key)

                instance = dynamic_create_instance_from_uri(typeURI, model_directory=model_directory)
                lijst.append(instance)

                for key, value in obj.items():
                    if 'typeURI' in key or value == '' or value == []:
                        continue

                    set_value_by_dictitem(instance_or_attribute=instance, key=key, value=value,
                                          waarde_shortcut=self.settings['dotnotation']['waarde_shortcut'],
                                          datetime_as_string=True)
            except Exception as ex:
                if not ignore_failed_objects:
                    raise ex
        return lijst


