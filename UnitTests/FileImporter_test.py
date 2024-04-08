import os
from pathlib import Path
from unittest import TestCase

from otlmow_converter.Exceptions.InvalidExtensionError import InvalidExtensionError
from otlmow_converter.FileFormats.CsvImporter import CsvImporter
from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
from otlmow_converter.FileFormats.GeoJSONImporter import GeoJSONImporter
from otlmow_converter.FileFormats.JsonImporter import JsonImporter
from otlmow_converter.FileFormats.JsonLdImporter import JsonLdImporter
from otlmow_converter.FileImporter import FileImporter


class FileImporterTests(TestCase):


    def test_get_importer_from_extension_valid_extensions(self):
        importer = FileImporter.get_importer_from_extension(extension='csv')
        self.assertIsInstance(importer, CsvImporter)

        importer = FileImporter.get_importer_from_extension(extension='json')
        self.assertIsInstance(importer, JsonImporter)

        for ext in {'xls', 'xlsx'}:
            importer = FileImporter.get_importer_from_extension(extension=ext)
            self.assertIsInstance(importer, ExcelImporter)

        importer = FileImporter.get_importer_from_extension('jsonld')
        assert isinstance(importer, JsonLdImporter)

        importer = FileImporter.get_importer_from_extension('geojson')
        assert isinstance(importer, GeoJSONImporter)

