import json

from otlmow_model.Helpers.AssetCreator import dynamic_create_instance_from_uri

from otlmow_converter.FileFormats.DictDecoder import DictDecoder


class JsonLdDecoder:
    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        json_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'jsonld'), None)
        if json_settings is None:
            raise ValueError("Unable to find json in file formats settings")

        self.settings = json_settings

    def decode_json_string(self, json_string, ignore_failed_objects=False, classes_directory: str = None):
        dict_list = json.loads(json_string)
        lijst = []
        for obj in dict_list['@graph']:
            try:
                typeURI = obj['@type']

                if 'https://wegenenverkeer.data.vlaanderen.be/ns' not in typeURI:
                    raise ValueError('typeURI should start with "https://wegenenverkeer.data.vlaanderen.be/ns" to use this decoder')

                instance = dynamic_create_instance_from_uri(typeURI, directory=classes_directory)
                lijst.append(instance)

                for key, value in obj.items():
                    if key == '@type':
                        continue
                    if key == '@id':
                        instance.assetId.identificator = value
                        continue
                    if 'typeURI' in key or value == '' or value == [] or key == 'bron' or key == 'doel':
                        continue

                    DictDecoder.set_value_by_dictitem(instance, key, value, self.settings['dotnotation']['waarde_shortcut_applicable'], ld=True)
            except Exception as ex:
                if not ignore_failed_objects:
                    raise ex
        return lijst


