from otlmow_converter.FileFormats.OtlAssetJSONLDEncoder import OtlAssetJSONLDEncoder


class JsonLdExporter:
    def __init__(self, settings=None):
        self.encoder = OtlAssetJSONLDEncoder(indent=4, settings=settings)

    def export_to_file(self, filepath: str = '', list_of_objects: list = None):
        encoded_json = self.encoder.encode(list_of_objects)
        self.encoder.write_json_to_file(encoded_json, filepath)
