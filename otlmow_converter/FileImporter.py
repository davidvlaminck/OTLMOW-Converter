import os
from pathlib import Path

from otlmow_converter.Exceptions.InvalidExtensionError import InvalidExtensionError


class FileImporter:
    def __init__(self, settings: dict):
        self.settings = settings

    def create_assets_from_file(self, filepath: Path = None, **kwargs):
        extension = self.get_file_extension(filepath)
        importer = self.get_importer_from_extension(extension=extension, settings=self.settings)
        return importer.import_file(filepath=filepath, **kwargs)

    @staticmethod
    def get_file_extension(filepath: Path, file_must_exist: bool = True):
        if filepath is None:
            raise ValueError('filepath is empty, specify a file path')
        filepath_str = str(filepath)
        if '.' not in filepath_str:
            raise ValueError(
                'This file does not have an extension. An extension is required to determine the type of importer '
                'that is needed to import this file')

        if file_must_exist and not os.path.isfile(filepath):
            raise FileNotFoundError(filepath_str + " is not a valid path. File does not exist.")

        return filepath.suffix[1:]

    @staticmethod
    def get_importer_from_extension(extension: str, settings: dict):
        if extension == 'csv':
            from otlmow_converter.FileFormats.CsvImporter import CsvImporter
            return CsvImporter(settings=settings)
        elif extension == 'json':
            from otlmow_converter.FileFormats.JsonImporter import JsonImporter
            return JsonImporter(settings=settings)
        elif extension == 'geojson':
            from otlmow_converter.FileFormats.GeoJSONImporter import GeoJSONImporter
            return GeoJSONImporter(settings=settings)
        elif extension == 'jsonld':
            from otlmow_converter.FileFormats.JsonLdImporter import JsonLdImporter
            return JsonLdImporter(settings=settings)
        elif extension in ['xls', 'xlsx']:
            from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
            return ExcelImporter(settings=settings)
        else:
            raise InvalidExtensionError('This file has an invalid extension. Supported file formats are: csv, json, xlsx')
