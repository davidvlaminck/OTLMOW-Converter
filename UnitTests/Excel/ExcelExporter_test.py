import os
from datetime import date, datetime, time
from pathlib import Path

import pytest

from UnitTests.SettingManagerForUnit_test import get_settings_path_for_unittests
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.ExcelExporter import ExcelExporter
from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
from otlmow_converter.OtlmowConverter import OtlmowConverter


def set_up_converter():
    settings_file_location = get_settings_path_for_unittests()
    otl_converter = OtlmowConverter(settings_path=settings_file_location)
    return otl_converter


def test_init_importer_only_load_with_settings(subtests):
    otl_converter = set_up_converter()

    with subtests.test(msg='load with correct settings'):
        exporter = ExcelExporter(settings=otl_converter.settings)
        assert exporter is not None

    with subtests.test(msg='load without settings'):
        with pytest.raises(ValueError):
            ExcelExporter(settings=None)

    with subtests.test(msg='load with incorrect settings (no file_formats)'):
        with pytest.raises(ValueError):
            ExcelExporter(settings={"auth_options": [{}]})

    with subtests.test(msg='load with incorrect settings (file_formats but no xls)'):
        with pytest.raises(ValueError):
            ExcelExporter(settings={"file_formats": [{}]})


def test_export_and_then_import_unnested_attributes():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    importer = ExcelImporter(settings=converter.settings)
    exporter = ExcelExporter(settings=converter.settings, model_directory='UnitTests.TestClasses')
    file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.xlsx'
    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000-0000'
    instance.testBooleanField = False
    instance.testDateField = date(2019, 9, 20)
    instance.testDateTimeField = datetime(2001, 12, 15, 22, 22, 15)
    instance.testDecimalField = 79.07
    instance.testDecimalFieldMetKard = [10.0, 20.0]
    instance.testEenvoudigType.waarde = 'string1'
    instance.testIntegerField = -55
    instance.testIntegerFieldMetKard = [76, 2]
    instance.testKeuzelijst = 'waarde-4'
    instance.testKeuzelijstMetKard = ['waarde-4', 'waarde-3']
    instance.testKwantWrd.waarde = 98.21
    instance.testStringField = 'oFfeDLp'
    instance.testStringFieldMetKard = ['string1', 'string2']
    instance.testTimeField = time(11, 5, 26)
    exporter.export_to_file(list_of_objects=[instance], filepath=file_location,
                            split_per_type=False)

    objects = importer.import_file(filepath=file_location, model_directory='UnitTests.TestClasses')
    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == '0000-0000'

    assert not instance.testBooleanField 
    assert instance.testDateField == date(2019, 9, 20)
    assert instance.testDateTimeField == datetime(2001, 12, 15, 22, 22, 15)
    assert instance.testDecimalField == 79.07
    assert instance.testDecimalFieldMetKard == [10.0, 20.0]
    assert instance.testEenvoudigType.waarde == 'string1'
    assert instance.testIntegerField == -55
    assert instance.testIntegerFieldMetKard == [76, 2]
    assert instance.testKeuzelijst == 'waarde-4'
    assert instance.testKeuzelijstMetKard == ['waarde-4', 'waarde-3']
    assert instance.testKwantWrd.waarde == 98.21
    assert instance.testStringField == 'oFfeDLp'
    assert instance.testStringFieldMetKard[0] == 'string1'
    assert instance.testStringFieldMetKard[1] == 'string2'
    assert instance.testTimeField == time(11, 5, 26)

    os.unlink(file_location)


def test_export_and_then_import_nested_attributes_level_1():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    importer = ExcelImporter(settings=converter.settings)
    exporter = ExcelExporter(settings=converter.settings, model_directory='UnitTests.TestClasses')
    file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.xlsx'
    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'

    instance._testEenvoudigTypeMetKard.add_empty_value()
    instance._testEenvoudigTypeMetKard.add_empty_value()
    instance.testEenvoudigTypeMetKard[0].waarde = 'string1'
    instance.testEenvoudigTypeMetKard[1].waarde = 'string2'
    instance._testKwantWrdMetKard.add_empty_value()
    instance._testKwantWrdMetKard.add_empty_value()
    instance.testKwantWrdMetKard[0].waarde = 10.0
    instance.testKwantWrdMetKard[1].waarde = 20.0

    instance.testComplexType.testBooleanField = True
    instance.testComplexType.testKwantWrd.waarde = 65.14
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType.testKwantWrdMetKard[0].waarde = 10.0
    instance.testComplexType.testKwantWrdMetKard[1].waarde = 20.0
    instance.testComplexType.testStringField = 'KmCtMXM'
    instance.testComplexType.testStringFieldMetKard = ['string1', 'string2']

    instance._testComplexTypeMetKard.add_empty_value()
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[0].testBooleanField = True
    instance.testComplexTypeMetKard[1].testBooleanField = False
    instance.testComplexTypeMetKard[0].testKwantWrd.waarde = 10.0
    instance.testComplexTypeMetKard[1].testKwantWrd.waarde = 20.0
    instance.testComplexTypeMetKard[0].testStringField = 'string1'
    instance.testComplexTypeMetKard[1].testStringField = 'string2'
    instance.testUnionType.unionString = 'RWKofW'

    instance._testUnionTypeMetKard.add_empty_value()
    instance._testUnionTypeMetKard.add_empty_value()
    instance.testUnionTypeMetKard[0].unionKwantWrd.waarde = 10.0
    instance.testUnionTypeMetKard[1].unionKwantWrd.waarde = 20.0

    exporter.export_to_file(list_of_objects=[instance], filepath=file_location,
                            split_per_type=False)

    objects = importer.import_file(filepath=file_location, model_directory='UnitTests.TestClasses')
    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'

    assert instance.testEenvoudigTypeMetKard[0].waarde == 'string1'
    assert instance.testEenvoudigTypeMetKard[1].waarde == 'string2'
    assert instance.testKwantWrdMetKard[0].waarde == 10.0
    assert instance.testKwantWrdMetKard[1].waarde == 20.0
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
    assert instance.testComplexTypeMetKard[0].testStringField == 'string1'
    assert instance.testComplexTypeMetKard[1].testStringField == 'string2'
    assert instance.testUnionType.unionString == 'RWKofW'
    assert instance.testUnionType.unionKwantWrd.waarde is None
    assert instance.testUnionTypeMetKard[0].unionKwantWrd.waarde == 10.0
    assert instance.testUnionTypeMetKard[1].unionKwantWrd.waarde == 20.0
    assert instance.assetId.identificator == '0000'

    os.unlink(file_location)


def test_export_and_then_import_nested_attributes_level_2():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    importer = ExcelImporter(settings=converter.settings)
    exporter = ExcelExporter(settings=converter.settings, model_directory='UnitTests.TestClasses')
    file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.xlsx'
    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'

    instance.testComplexType.testComplexType2.testKwantWrd.waarde = 76.8
    instance.testComplexType.testComplexType2.testStringField = 'GZBzgRhOrQvfZaN'
    instance.testComplexType._testComplexType2MetKard.add_empty_value()
    instance.testComplexType._testComplexType2MetKard.add_empty_value()
    instance.testComplexType.testComplexType2MetKard[0].testKwantWrd.waarde = 10.0
    instance.testComplexType.testComplexType2MetKard[1].testKwantWrd.waarde = 20.0
    instance.testComplexType.testComplexType2MetKard[0].testStringField = 'string1'
    instance.testComplexType.testComplexType2MetKard[1].testStringField = 'string2'

    instance._testComplexTypeMetKard.add_empty_value()
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[0].testComplexType2.testKwantWrd.waarde = 10.0
    instance.testComplexTypeMetKard[1].testComplexType2.testKwantWrd.waarde = 20.0
    instance.testComplexTypeMetKard[0].testComplexType2.testStringField = 'string1'
    instance.testComplexTypeMetKard[1].testComplexType2.testStringField = 'string2'

    exporter.export_to_file(list_of_objects=[instance], filepath=file_location,
                            split_per_type=False)

    objects = importer.import_file(filepath=file_location, model_directory='UnitTests.TestClasses')
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
    assert instance.assetId.identificator == '0000'

    os.unlink(file_location)
