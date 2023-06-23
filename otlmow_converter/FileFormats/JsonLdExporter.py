from pathlib import Path

from otlmow_converter.FileFormats.JsonLdContext import JsonLdContext
from otlmow_converter.FileFormats.OtlAssetJSONLDEncoder import OtlAssetJSONLDEncoder


class JsonLdExporter:
    def __init__(self, settings=None):
        self.encoder = OtlAssetJSONLDEncoder(indent=4, settings=settings)

    def export_to_file(self, filepath: Path, list_of_objects: list = None):
        graph_dict = {}
        if isinstance(list_of_objects, list):
            graph_dict['@graph'] = list_of_objects
        else:
            graph_dict['@graph'] = [list_of_objects]
        encoded_json = self.encoder.encode(graph_dict)
        encoded_json = self.modify_jsonld_for_context(encoded_json)
        self.encoder.write_json_to_file(encoded_json, filepath)

    @staticmethod
    def modify_jsonld_for_context(encoded_json: str):
        context_dict = JsonLdContext.context_dict
        context_str = '{'
        for short, long in context_dict.items():
            if long in encoded_json:
                context_str += f'"{short}": "{long}", '
                encoded_json = encoded_json.replace(long, f'{short}:')
        context_str = context_str[:-2] + '}'

        encoded_json = encoded_json.replace('"@graph"', f'"@context": {context_str},"@graph"')
        return encoded_json
