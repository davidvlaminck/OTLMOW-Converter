import pytest

from otlmow_converter.FileFormats.CsvImporter import CsvImporter
from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
from otlmow_converter.FileFormats.GeoJSONImporter import GeoJSONImporter
from otlmow_converter.FileFormats.JsonImporter import JsonImporter
from otlmow_converter.FileFormats.JsonLdImporter import JsonLdImporter
from otlmow_converter.FileImporter import FileImporter


@pytest.mark.parametrize("extension, expected_importer",
                         [('csv', CsvImporter),
                          ('json', JsonImporter),
                          ('xls', ExcelImporter),
                          ('xlsx', ExcelImporter),
                          ('jsonld', JsonLdImporter),
                          ('geojson', GeoJSONImporter)])
def test_get_importer_from_extension_valid_extensions(extension, expected_importer):
    importer = FileImporter.get_importer_from_extension(extension)
    assert isinstance(importer, expected_importer)
