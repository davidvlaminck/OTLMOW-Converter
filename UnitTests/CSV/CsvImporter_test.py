from datetime import date, datetime, time
from pathlib import Path

import pytest

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.Exceptions.NoTypeUriInTableError import NoTypeUriInTableError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError
from otlmow_converter.FileFormats.CsvImporter import CsvImporter

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_load_test_file_multiple_types():
    file_location = Path(__file__).parent / 'Testfiles' / 'export_multiple_types.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location))
    assert len(assets) == 15


def test_load_test_file(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'import_then_export_input.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path))
    assert len(assets) == 1
    assert assets[0].assetId.identificator == 'UgVLnoH'
    assert recwarn.list == []


def test_load_test_unnested_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path))
    assert len(recwarn.list) == 0

    assert len(assets) == 1
    instance = assets[0]
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


def test_load_test_unnested_attributes_clear_values(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes_clear_values.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path))

    assert len(assets) == 1

    instance = AllCasesTestClass()
    instance._testBooleanField.clear_value()
    instance._testDateField.clear_value()
    instance._testDateTimeField.clear_value()
    instance._testDecimalField.clear_value()
    instance._testDecimalFieldMetKard.clear_value()
    instance.testEenvoudigType._waarde.clear_value()
    instance.testEenvoudigTypeMetKard[0]._waarde.clear_value()
    instance._testEenvoudigTypeMetKard.add_empty_value()
    instance.testEenvoudigTypeMetKard[1]._waarde.clear_value()
    instance._testIntegerField.clear_value()
    instance._testIntegerFieldMetKard.clear_value()
    instance._testKeuzelijst.clear_value()
    instance._testKeuzelijstMetKard.clear_value()
    instance.testKwantWrd._waarde.clear_value()
    instance.testKwantWrdMetKard[0]._waarde.clear_value()
    instance._testKwantWrdMetKard.add_empty_value()
    instance.testKwantWrdMetKard[1]._waarde.clear_value()
    instance._testStringField.clear_value()
    instance._testStringFieldMetKard.clear_value()
    instance._testTimeField.clear_value()
    instance.assetId.identificator = '0000-0000'
    assert instance == assets[0]

    assert len(recwarn.list) == 0


def test_load_test_nested_attributes_1_level(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_1.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path))
    assert len(recwarn.list) == 0

    assert len(assets) == 1
    instance = assets[0]
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


def test_load_test_nested_attributes_2_levels(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_2.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path))
    assert len(recwarn.list) == 0

    assert len(assets) == 1
    instance = assets[0]
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


def test_load_test_subset_file(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'template_file_text_onderdeel_AllCasesTestClass.csv'

    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path))
    assert len(recwarn.list) == 0
    assert len(assets) == 1


def test_raise_errors():
    file_location = Path(__file__).parent / 'Testfiles' / 'type_uri_not_in_first_row.csv'
    with pytest.raises(TypeUriNotInFirstRowError) as exc:
        CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
        assert exc.value.message == 'The typeURI is not in the first row in file type_uri_not_in_first_row.csv'
        assert exc.value.file_path == file_location

    file_location = Path(__file__).parent / 'Testfiles' / 'type_uri_not_in_file.csv'
    with pytest.raises(NoTypeUriInTableError) as exc:
        CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
        assert exc.value.message == 'Could not find typeURI within 5 rows in the csv file type_uri_not_in_file.csv'
        assert exc.value.file_path == file_location
