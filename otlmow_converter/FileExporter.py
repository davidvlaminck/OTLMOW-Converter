from pathlib import Path

from otlmow_converter.Exceptions.InvalidExtensionError import InvalidExtensionError
from otlmow_converter.FileFormats.CsvExporter import CsvExporter
from otlmow_converter.FileFormats.JsonExporter import JsonExporter
from otlmow_converter.FileImporter import FileImporter


class FileExporter:
    def __init__(self, settings: dict):
        self.settings = settings

    def create_file_from_assets(self, filepath: Path, list_of_objects: list, **kwargs):
        extension = FileImporter.get_file_extension(filepath, file_must_exist=False)
        exporter = self.get_exporter_from_extension(extension=extension, settings=self.settings)
        return exporter.export_to_file(filepath=filepath, list_of_objects=list_of_objects, **kwargs)

    @staticmethod
    def get_exporter_from_extension(extension: str, settings: dict):
        if extension == 'csv':
            return CsvExporter(settings=settings)
        if extension == 'json':
            return JsonExporter(settings=settings)
        else:
            raise InvalidExtensionError('This file has an invalid extension. Supported file formats are: csv, json')

