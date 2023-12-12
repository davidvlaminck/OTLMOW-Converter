import os
from datetime import date, datetime, time
from pathlib import Path
from unittest.mock import Mock

import pytest

from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.Exceptions.InvalidColumnNamesInExcelTabError import InvalidColumnNamesInExcelTabError
from otlmow_converter.Exceptions.NoTypeUriInExcelTabError import NoTypeUriInExcelTabError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError
from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
from otlmow_converter.OtlmowConverter import OtlmowConverter

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_init_importer_only_load_with_settings(subtests):
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)

    with subtests.test(msg='load with correct settings'):
        importer = ExcelImporter(settings=converter.settings)
        assert importer is not None

    with subtests.test(msg='load without settings'):
        with pytest.raises(ValueError):
            ExcelImporter()

    with subtests.test(msg='load with incorrect settings (no file_formats)'):
        with pytest.raises(ValueError):
            ExcelImporter(settings={"auth_options": [{}]})

    with subtests.test(msg='load with incorrect settings (file_formats but no xls)'):
        with pytest.raises(ValueError):
            ExcelImporter(settings={"file_formats": [{}]})


def test_load_test_unnested_attributes(caplog):
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    importer = ExcelImporter(settings=converter.settings)
    file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes.xlsx'

    caplog.records.clear()
    objects = importer.import_file(filepath=file_location, model_directory=model_directory_path)
    assert len(caplog.records) == 0

    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert not instance.testBooleanField
    assert instance.testDateField == date(2019, 9, 20)
    assert instance.testDateTimeField == datetime(2001, 12, 15, 22, 22, 15)
    assert instance.testDecimalField == 79.07
    assert instance.testDecimalFieldMetKard == [10.0, 20.0]
    assert instance.testEenvoudigType.waarde == 'string1'
    assert instance.testEenvoudigTypeMetKard[0].waarde == 'string1'
    assert instance.testEenvoudigTypeMetKard[1].waarde == 'string2'
    assert instance.testIntegerField == -55
    assert instance.testIntegerFieldMetKard == [76, 2]
    assert instance.testKeuzelijst == 'waarde-4'
    assert instance.testKeuzelijstMetKard == ['waarde-4', 'waarde-3']
    assert instance.testKwantWrd.waarde == 98.21
    assert instance.testKwantWrdMetKard[0].waarde == 10.0
    assert instance.testKwantWrdMetKard[1].waarde == 20.0
    assert instance.testStringField == 'oFfeDLp'
    assert instance.testStringFieldMetKard[0] == 'string1'
    assert instance.testStringFieldMetKard[1] == 'string2'
    assert instance.testTimeField == time(11, 5, 26)


def test_load_test_nested_attributes_1_level(caplog):
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    importer = ExcelImporter(settings=converter.settings)
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_1.xlsx'

    caplog.records.clear()
    objects = importer.import_file(filepath=file_location, model_directory=model_directory_path)
    assert len(caplog.records) == 0

    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == 'YKAzZDhhdTXqkD'
    assert instance.assetId.toegekendDoor == 'DGcQxwCGiBlR'
    assert instance.testComplexType.testBooleanField
    assert instance.testComplexType.testKwantWrd.waarde == 65.14
    assert instance.testComplexType.testKwantWrdMetKard[0].waarde == 10.0
    assert instance.testComplexType.testKwantWrdMetKard[1].waarde == 20.0
    assert instance.testComplexType.testStringField == 'KmCtMXM'
    assert instance.testComplexType.testStringFieldMetKard[0] == 'string1'
    assert instance.testComplexType.testStringFieldMetKard[1] == 'string2'
    assert instance.testComplexTypeMetKard[0].testBooleanField
    assert not instance.testComplexTypeMetKard[1].testBooleanField
    assert instance.testComplexTypeMetKard[0].testKwantWrd.waarde == 10.0
    assert instance.testComplexTypeMetKard[1].testKwantWrd.waarde == 20.0
    assert instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde is None
    assert instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde is None
    assert instance.testComplexTypeMetKard[0].testStringField == 'string1'
    assert instance.testComplexTypeMetKard[1].testStringField == 'string2'
    assert instance.testUnionType.unionString == 'RWKofW'
    assert instance.testUnionType.unionKwantWrd.waarde is None
    assert instance.testUnionTypeMetKard[0].unionKwantWrd.waarde == 10.0
    assert instance.testUnionTypeMetKard[1].unionKwantWrd.waarde == 20.0


def test_load_test_nested_attributes_2_levels(caplog):
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    importer = ExcelImporter(settings=converter.settings)
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_2.xlsx'

    caplog.records.clear()
    objects = importer.import_file(filepath=file_location, model_directory=model_directory_path)
    assert len(caplog.records) == 0

    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.testComplexType.testComplexType2.testKwantWrd.waarde == 76.8
    assert instance.testComplexType.testComplexType2.testStringField == 'GZBzgRhOrQvfZaN'
    assert instance.testComplexType.testComplexType2MetKard[0].testKwantWrd.waarde == 10.0
    assert instance.testComplexType.testComplexType2MetKard[1].testKwantWrd.waarde == 20.0
    assert instance.testComplexType.testComplexType2MetKard[0].testStringField == 'string1'
    assert instance.testComplexType.testComplexType2MetKard[1].testStringField == 'string2'
    assert instance.testComplexTypeMetKard[0].testComplexType2.testKwantWrd.waarde == 10.0
    assert instance.testComplexTypeMetKard[1].testComplexType2.testKwantWrd.waarde == 20.0
    assert instance.testComplexTypeMetKard[0].testComplexType2.testStringField == 'string1'
    assert instance.testComplexTypeMetKard[1].testComplexType2.testStringField == 'string2'
    assert instance.testComplexTypeMetKard[0].testComplexType2MetKard[0].testKwantWrd.waarde is None
    assert instance.testComplexTypeMetKard[0].testComplexType2MetKard[0].testStringField is None


def test_get_index_of_typeURI_column_in_sheet():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    importer = ExcelImporter(settings=converter.settings)
    file_location = Path(__file__).parent / 'Testfiles' / 'typeURITestFile.xlsx'
    orig_create_objects_from_data = importer.create_objects_from_data
    importer.create_objects_from_data = Mock()
    importer.import_file(filepath=file_location, model_directory=model_directory_path)

    for sheet, data in importer.data.items():
        sheet_name = str(sheet)
        if sheet_name == '<Worksheet "correct_sheet">':
            headers = data[0]
            type_uri_index = importer.get_index_of_typeURI_column_in_sheet(
                filepath=file_location, sheet='correct_sheet', headers=headers, data=data)
            assert type_uri_index == 0
            break

    importer = ExcelImporter(settings=converter.settings)
    importer.create_objects_from_data = orig_create_objects_from_data

    try:
        importer.import_file(filepath=file_location, model_directory=model_directory_path)
        assert False
    except Exception as ex:
        assert isinstance(ex, ExceptionsGroup)
        assert len(ex.exceptions) == 3

        exception_1 = ex.exceptions[0]
        assert isinstance(exception_1, TypeUriNotInFirstRowError)
        assert exception_1.file_path == file_location
        assert exception_1.tab == 'type_uri_third_row'

        exception_2 = ex.exceptions[1]
        assert isinstance(exception_2, NoTypeUriInExcelTabError)
        assert exception_2.file_path == file_location
        assert exception_2.tab == 'no_type_uri_in_sheet'

        exception_3 = ex.exceptions[2]
        assert isinstance(exception_3, NoTypeUriInExcelTabError)
        assert exception_3.file_path == file_location
        assert exception_3.tab == 'empty_sheet'


def test_check_headers():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    importer = ExcelImporter(settings=converter.settings)
    file_location = Path(__file__).parent / 'Testfiles' / 'typeURITestFile.xlsx'

    try:
        importer.check_headers(
            filepath=file_location, model_directory=model_directory_path, sheet='<Worksheet "correct_sheet">',
            headers=['typeURI', 'testStringField', 'bad_name_field', '[DEPRECATED] d_a', 'list[].list[]'],
            type_uri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass')
        assert False
    except InvalidColumnNamesInExcelTabError as ex:
        assert ex.bad_columns == ['bad_name_field', '[DEPRECATED] d_a', 'list[].list[]']


