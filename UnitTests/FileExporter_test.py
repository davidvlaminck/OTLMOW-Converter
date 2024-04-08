import pytest

from otlmow_converter.Exceptions.InvalidExtensionError import InvalidExtensionError
from otlmow_converter.FileExporter import FileExporter
from otlmow_converter.FileFormats.CsvExporter import CsvExporter
from otlmow_converter.FileFormats.ExcelExporter import ExcelExporter
from otlmow_converter.FileFormats.GeoJSONExporter import GeoJSONExporter
from otlmow_converter.FileFormats.JsonExporter import JsonExporter
from otlmow_converter.FileFormats.JsonLdExporter import JsonLdExporter
from otlmow_converter.FileFormats.TtlExporter import TtlExporter


def test_return_Exporter_correct_type(subtests):
    with subtests.test(msg='returning GeoJsonExporter'):
        exporter = FileExporter.get_exporter_from_extension('geojson')
        assert isinstance(exporter, GeoJSONExporter)

    with subtests.test(msg='returning JsonExporter'):
        exporter = FileExporter.get_exporter_from_extension('json')
        assert isinstance(exporter, JsonExporter)

    with subtests.test(msg='returning JsonLdExporter'):
        exporter = FileExporter.get_exporter_from_extension('jsonld')
        assert isinstance(exporter, JsonLdExporter)

    with subtests.test(msg='returning ExcelExporter'):
        for extension in ['xls', 'xlsx']:
            exporter = FileExporter.get_exporter_from_extension(extension)
            assert isinstance(exporter, ExcelExporter)

    with subtests.test(msg='returning CsvExporter'):
        exporter = FileExporter.get_exporter_from_extension('csv')
        assert isinstance(exporter, CsvExporter)

    with subtests.test(msg='returning TtlExporter'):
        exporter = FileExporter.get_exporter_from_extension('ttl')
        assert isinstance(exporter, TtlExporter)

    with subtests.test(msg='invalid extension'):
        with pytest.raises(InvalidExtensionError):
            FileExporter.get_exporter_from_extension('dwg')
