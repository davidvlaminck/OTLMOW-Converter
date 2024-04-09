import pytest

from otlmow_converter.Exceptions.InvalidExtensionError import InvalidExtensionError
from otlmow_converter.FileExporter import FileExporter
from otlmow_converter.FileFormats.CsvExporter import CsvExporter
from otlmow_converter.FileFormats.ExcelExporter import ExcelExporter
from otlmow_converter.FileFormats.GeoJSONExporter import GeoJSONExporter
from otlmow_converter.FileFormats.JsonExporter import JsonExporter
from otlmow_converter.FileFormats.JsonLdExporter import JsonLdExporter
from otlmow_converter.FileFormats.TtlExporter import TtlExporter


@pytest.mark.parametrize("extension, expected_exporter",
                         [('geojson', GeoJSONExporter),
                          ('json', JsonExporter),
                          ('jsonld', JsonLdExporter),
                          ('xls', ExcelExporter),
                          ('xlsx', ExcelExporter),
                          ('csv', CsvExporter),
                          ('ttl', TtlExporter),
                          ('dwg', None)])  # None represents the expected result when an InvalidExtensionError is raised
def test_return_Exporter_correct_type(subtests, extension, expected_exporter):
    with subtests.test(msg=f'returning {expected_exporter.__name__}'):
        if expected_exporter is not None:
            exporter = FileExporter.get_exporter_from_extension(extension)
            assert isinstance(exporter, expected_exporter)
        else:
            with pytest.raises(InvalidExtensionError):
                FileExporter.get_exporter_from_extension(extension)
