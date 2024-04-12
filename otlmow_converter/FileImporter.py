from otlmow_converter.AbstractImporter import AbstractImporter
from otlmow_converter.Exceptions.InvalidExtensionError import InvalidExtensionError


class FileImporter:
    @classmethod
    def get_importer_from_extension(cls, extension: str) -> AbstractImporter:
        if extension == 'csv':
            from otlmow_converter.FileFormats.CsvImporter import CsvImporter
            return CsvImporter()
        elif extension == 'json':
            from otlmow_converter.FileFormats.JsonImporter import JsonImporter
            return JsonImporter()
        elif extension == 'geojson':
            from otlmow_converter.FileFormats.GeoJSONImporter import GeoJSONImporter
            return GeoJSONImporter()
        elif extension == 'jsonld':
            from otlmow_converter.FileFormats.JsonLdImporter import JsonLdImporter
            return JsonLdImporter()
        elif extension in {'xls', 'xlsx'}:
            from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
            return ExcelImporter()
        else:
            raise InvalidExtensionError('This file has an invalid extension. '
                                        'Supported file formats are: csv, json, xlsx, xls, geojson, jsonld')
