from pathlib import Path

from otlmow_converter.Exceptions.InvalidExtensionError import InvalidExtensionError
from otlmow_converter.FileImporter import FileImporter


class FileExporter:
    def __init__(self, settings: dict):
        self.settings = settings

    def create_file_from_assets(self, filepath: Path, list_of_objects: list, **kwargs):
        extension = FileImporter.get_file_extension(filepath, file_must_exist=False)
        exporter = self.get_exporter_from_extension(extension=extension, settings=self.settings, **kwargs)
        return exporter.export_to_file(filepath=filepath, list_of_objects=list_of_objects, **kwargs)

    @classmethod
    def get_exporter_from_extension(cls, extension: str, settings: dict, **kwargs):
        if extension == 'csv':
            model_directory = None
            if kwargs is not None and 'model_directory' in kwargs:
                model_directory = kwargs['model_directory']
            from otlmow_converter.FileFormats.CsvExporter import CsvExporter
            return CsvExporter(settings=settings, model_directory=model_directory)
        elif extension == 'json':
            from otlmow_converter.FileFormats.JsonExporter import JsonExporter
            return JsonExporter(settings=settings)
        elif extension in ['xls', 'xlsx']:
            from otlmow_converter.FileFormats.ExcelExporter import ExcelExporter
            return ExcelExporter(settings=settings)
        elif extension == 'ttl':
            from otlmow_converter.FileFormats.TtlExporter import TtlExporter
            return TtlExporter(settings=settings)
        elif extension == 'jsonld':
            from otlmow_converter.FileFormats.JsonLdExporter import JsonLdExporter
            return JsonLdExporter(settings=settings)
        elif extension == 'geojson':
            from otlmow_converter.FileFormats.GeoJSONExporter import GeoJSONExporter
            return GeoJSONExporter(settings=settings)
        else:
            raise InvalidExtensionError('This file has an invalid extension. Supported file formats are: csv, json, xlsx, xls, ttl, jsonld')

