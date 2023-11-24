import json

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from otlmow_converter.FileFormats.JsonLdContext import JsonLdContext


class JsonLdDecoder:
    def __init__(self, settings=None, model_directory: str = None):
        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        json_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'jsonld'), None)
        if json_settings is None:
            raise ValueError("Unable to find json in file formats settings")

        self.settings = json_settings
        self.model_directory = model_directory

    def decode_json_string(self, json_string: str, ignore_failed_objects=False) -> [OTLObject]:
        dict_list = json.loads(json_string)
        if '@context' in dict_list:
            context_dict = dict_list['@context']
        else:
            context_dict = {}

        lijst = []

        for obj in dict_list['@graph']:
            try:
                rdf_dict = self.transform_dict_to_rdf(d=obj, context_dict=context_dict)
                del rdf_dict['@id']
                del rdf_dict['@type']
                instance = OTLObject.from_dict(rdf_dict, rdf=True, model_directory=self.model_directory,
                                               waarde_shortcut=self.settings['dotnotation']['waarde_shortcut'])
                lijst.append(instance)
            except Exception as ex:
                if not ignore_failed_objects:
                    raise ex
        return lijst

    def transform_dict_to_rdf(self, d: dict, context_dict: dict):
        new_dict = {}
        for k, v in d.items():
            if ':' in k:
                k = JsonLdContext.replace_context(k, context_dict=context_dict)

            if isinstance(v, dict):
                v = self.transform_dict_to_rdf(v, context_dict=context_dict)
            elif isinstance(v, str) and v and ':' in v:
                v = JsonLdContext.replace_context(v, context_dict=context_dict)
            elif isinstance(v, list):
                value_list = []
                for list_item in v:
                    if isinstance(list_item, dict):
                        value_list.append(self.transform_dict_to_rdf(list_item, context_dict=context_dict))
                    elif isinstance(list_item, str) and list_item and ':' in list_item:
                        value_list.append(JsonLdContext.replace_context(list_item, context_dict=context_dict))
                    else:
                        value_list.append(list_item)
                v = value_list
            new_dict[k] = v
        return new_dict



