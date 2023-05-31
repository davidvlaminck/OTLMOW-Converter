from pathlib import Path

from otlmow_converter.FileFormats.OtlAssetJSONEncoder import OtlAssetJSONEncoder


class JsonExporter:
    def __init__(self, settings=None):
        self.encoder = OtlAssetJSONEncoder(indent=4, settings=settings)

    def export_to_file(self, filepath: Path, list_of_objects: list = None):
        encoded_json = self.encoder.encode(list_of_objects)
        self.encoder.write_json_to_file(encoded_json, filepath)
