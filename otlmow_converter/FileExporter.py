from otlmow_converter.AbstractExporter import AbstractExporter
from otlmow_converter.Exceptions.InvalidExtensionError import InvalidExtensionError


class FileExporter:
    @classmethod
    def get_exporter_from_extension(cls, extension: str) -> AbstractExporter:
        if extension == 'csv':
            from otlmow_converter.FileFormats.CsvExporter import CsvExporter
            return CsvExporter()
        elif extension == 'json':
            from otlmow_converter.FileFormats.JsonExporter import JsonExporter
            return JsonExporter()
        elif extension in {'xls', 'xlsx'}:
            from otlmow_converter.FileFormats.ExcelExporter import ExcelExporter
            return ExcelExporter()
        # elif extension == 'ttl':
        #     from otlmow_converter.FileFormats.TtlExporter import TtlExporter
        #     return TtlExporter()
        elif extension == 'jsonld':
            from otlmow_converter.FileFormats.JsonLdExporter import JsonLdExporter
            return JsonLdExporter()
        elif extension == 'geojson':
            from otlmow_converter.FileFormats.GeoJSONExporter import GeoJSONExporter
            return GeoJSONExporter()
        else:
            raise InvalidExtensionError('This file has an invalid extension. '
                                        'Supported file formats are: csv, json, xlsx, xls, geojson, jsonld')

