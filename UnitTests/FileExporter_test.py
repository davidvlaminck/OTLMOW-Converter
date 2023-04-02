import pytest

from UnitTests.SettingManagerForUnit_test import get_settings_path_for_unittests
from otlmow_converter import SettingsManager
from otlmow_converter.Exceptions.InvalidExtensionError import InvalidExtensionError
from otlmow_converter.FileExporter import FileExporter
from otlmow_converter.FileFormats.CsvExporter import CsvExporter
from otlmow_converter.FileFormats.ExcelExporter import ExcelExporter
from otlmow_converter.FileFormats.JsonExporter import JsonExporter
from otlmow_converter.FileFormats.JsonLdExporter import JsonLdExporter
from otlmow_converter.FileFormats.TtlExporter import TtlExporter


def test_init_and_save_settings():
    settings = {'csv': {}}
    expected_settings = {'csv': {}}
    exporter = FileExporter(settings=settings)
    assert exporter is not None
    assert exporter.settings == expected_settings


def test_return_Exporter_correct_type(subtests):
    settings_path = get_settings_path_for_unittests()
    unittest_settings = SettingsManager.load_settings(settings_path=settings_path)

    with subtests.test(msg='returning JsonExporter'):
        exporter = FileExporter.get_exporter_from_extension('json', settings=unittest_settings)
        assert isinstance(exporter, JsonExporter)

    with subtests.test(msg='returning JsonLdExporter'):
        exporter = FileExporter.get_exporter_from_extension('jsonld', settings=unittest_settings)
        assert isinstance(exporter, JsonLdExporter)

    with subtests.test(msg='returning ExcelExporter'):
        for extension in ['xls', 'xlsx']:
            exporter = FileExporter.get_exporter_from_extension(extension, settings=unittest_settings)
            assert isinstance(exporter, ExcelExporter)

    with subtests.test(msg='returning CsvExporter'):
        exporter = FileExporter.get_exporter_from_extension('csv', settings=unittest_settings)
        assert isinstance(exporter, CsvExporter)

    with subtests.test(msg='returning TtlExporter'):
        exporter = FileExporter.get_exporter_from_extension('ttl', settings=unittest_settings)
        assert isinstance(exporter, TtlExporter)

    with subtests.test(msg='invalid extension'):
        with pytest.raises(InvalidExtensionError):
            FileExporter.get_exporter_from_extension('dwg', settings=unittest_settings)