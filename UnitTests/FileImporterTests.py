import os
from pathlib import Path
from unittest import TestCase

from otlmow_converter.Exceptions.InvalidExtensionError import InvalidExtensionError
from otlmow_converter.FileFormats.CsvImporter import CsvImporter
from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
from otlmow_converter.FileFormats.JsonImporter import JsonImporter
from otlmow_converter.FileImporter import FileImporter


class FileImporterTests(TestCase):
    def test_get_file_extension_empty_path(self):
        with self.assertRaises(ValueError):
            FileImporter.get_file_extension('')
        with self.assertRaises(ValueError):
            FileImporter.get_file_extension(None)

    def test_get_file_extension_nonexistant_filepath(self):
        with self.assertRaises(FileNotFoundError):
            FileImporter.get_file_extension(Path('this_file_does_not_exist.csv'))

    def test_get_file_extension_filepath_without_extension(self):
        with self.assertRaises(ValueError):
            FileImporter.get_file_extension(Path('this_file_has_no_extension'))

    def test_get_file_extension_valid_filepath(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        filepath = Path(base_dir) / 'CSV' / 'Testfiles' / 'import_then_export_input.csv'
        extension = FileImporter.get_file_extension(filepath)
        self.assertEqual('csv', extension)

    def test_get_importer_from_extension_invalid_extension(self):
        with self.assertRaises(InvalidExtensionError):
            FileImporter.get_importer_from_extension(extension='jpg', settings={})

    def test_get_importer_from_extension_valid_extensions(self):
        empty_settings = {'file_formats': [{'name': 'csv'}, {'name': 'json'},  {'name': 'xls'}]}
        importer = FileImporter.get_importer_from_extension(extension='csv', settings=empty_settings)
        self.assertIsInstance(importer, CsvImporter)

        importer = FileImporter.get_importer_from_extension(extension='json', settings=empty_settings)
        self.assertIsInstance(importer, JsonImporter)

        importer = FileImporter.get_importer_from_extension(extension='xlsx', settings=empty_settings)
        self.assertIsInstance(importer, ExcelImporter)

