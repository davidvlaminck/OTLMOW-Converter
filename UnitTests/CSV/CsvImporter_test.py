from datetime import date, datetime, time
from pathlib import Path

import pytest

from otlmow_converter.FileFormats.CsvImporter import CsvImporter
from otlmow_converter.OtlmowConverter import OtlmowConverter


def test_init_importer_only_load_with_settings(subtests):
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    otl_facility = OtlmowConverter(settings_path=settings_file_location)

    with subtests.test(msg='load with correct settings'):
        importer = CsvImporter(settings=otl_facility.settings)
        assert importer is not None

    with subtests.test(msg='load without settings'):
        with pytest.raises(ValueError):
            CsvImporter(settings=None)

    with subtests.test(msg='load with incorrect settings (no file_formats)'):
        with pytest.raises(ValueError):
            CsvImporter(settings={"auth_options": [{}]})

    with subtests.test(msg='load with incorrect settings (file_formats but no csv)'):
        with pytest.raises(ValueError):
            CsvImporter(settings={"file_formats": [{}]})


def test_load_test_file_multiple_types():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    file_location = Path(__file__).parent / 'export_multiple_types.csv'
    otl_facility = OtlmowConverter(settings_path=settings_file_location)
    objects = otl_facility.create_assets_from_file(file_location)

    assert len(objects) == 15


def test_load_test_file():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    otl_facility = OtlmowConverter(settings_path=settings_file_location)
    importer = CsvImporter(settings=otl_facility.settings)
    file_location = Path(__file__).parent / 'Testfiles' / 'import_then_export_input.csv'
    importer.import_file(file_location, class_directory='UnitTests.TestClasses.Classes')
    assert len(importer.data) == 1
    assert len(importer.headers) == 35


def test_load_test_unnested_attributes():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    importer = CsvImporter(settings=converter.settings)
    file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes.csv'
    objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
    assert len(objects) == 1
    assert len(importer.headers) == 17

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
    importer = CsvImporter(settings=converter.settings)
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_1.csv'

    caplog.records.clear()
    objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
    assert len(caplog.records) == 2

    assert len(objects) == 1
    assert len(importer.headers) == 15

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
    importer = CsvImporter(settings=converter.settings)
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_2.csv'

    caplog.records.clear()
    objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
    assert len(caplog.records) == 2

    assert len(objects) == 1
    assert len(importer.headers) == 9

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


def test_load_test_subset_file(caplog):
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    otl_facility = OtlmowConverter(settings_path=settings_file_location)
    importer = CsvImporter(settings=otl_facility.settings)
    file_location = Path(__file__).parent / 'template_file_text_onderdeel_AllCasesTestClass.csv'

    caplog.records.clear()
    objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
    assert len(caplog.records) == 4

    assert len(objects) == 1
    assert len(importer.headers) == 39
