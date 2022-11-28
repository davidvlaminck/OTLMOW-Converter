from pathlib import Path

from otlmow_converter.Exceptions.InvalidExtensionError import InvalidExtensionError
from otlmow_converter.FileFormats.CsvExporter import CsvExporter
from otlmow_converter.FileFormats.ExcelExporter import ExcelExporter
from otlmow_converter.FileFormats.JsonExporter import JsonExporter
from otlmow_converter.FileFormats.JsonLdExporter import JsonLdExporter
from otlmow_converter.FileFormats.TtlExporter import TtlExporter
from otlmow_converter.FileImporter import FileImporter


class FileExporter:
    def __init__(self, settings: dict):
        self.settings = settings

    def create_file_from_assets(self, filepath: Path, list_of_objects: list, **kwargs):
        extension = FileImporter.get_file_extension(filepath, file_must_exist=False)
        exporter = self.get_exporter_from_extension(extension=extension, settings=self.settings, **kwargs)
        return exporter.export_to_file(filepath=filepath, list_of_objects=list_of_objects, **kwargs)

    @staticmethod
    def get_exporter_from_extension(extension: str, settings: dict, **kwargs):
        if extension == 'csv':
            class_directory = None
            if kwargs is not None and 'class_directory' in kwargs:
                class_directory = kwargs['class_directory']
            return CsvExporter(settings=settings, class_directory=class_directory)
        elif extension == 'json':
            return JsonExporter(settings=settings)
        elif extension in ['xls', 'xlsx']:
            return ExcelExporter(settings=settings)
        elif extension == 'ttl':
            return TtlExporter(settings=settings)
        elif extension == 'jsonld':
            return JsonLdExporter(settings=settings)
        else:
            raise InvalidExtensionError('This file has an invalid extension. Supported file formats are: csv, json, xlsx, xls, ttl, jsonld')

