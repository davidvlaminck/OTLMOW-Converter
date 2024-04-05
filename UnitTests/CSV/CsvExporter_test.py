import csv
import os
import shutil
from datetime import date, datetime, time
from pathlib import Path

import pytest

from UnitTests.SettingManagerForUnit_test import get_settings_path_for_unittests
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError
from otlmow_converter.FileFormats.CsvExporter import CsvExporter
from otlmow_converter.FileFormats.CsvImporter import CsvImporter
from otlmow_converter.OtlmowConverter import OtlmowConverter

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_export_unnested_attributes():
    temp_dir_path = Path(__file__).parent / 'remove_after_test'
    os.mkdir(temp_dir_path)
    file_location = temp_dir_path / 'unnested.csv'

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testBooleanField = False
    instance.testDateField = date(2019, 9, 20)
    instance.testDateTimeField = datetime(2001, 12, 15, 22, 22, 15)
    instance.testDecimalField = 79.07
    instance.testDecimalFieldMetKard = [10.0, 20.0]
    instance.testEenvoudigType.waarde = 'string1'
    instance._testEenvoudigTypeMetKard.add_empty_value()
    instance._testEenvoudigTypeMetKard.add_empty_value()
    instance.testEenvoudigTypeMetKard[0].waarde = 'string1'
    instance.testEenvoudigTypeMetKard[1].waarde = 'string2'
    instance.testIntegerField = -55
    instance.testIntegerFieldMetKard = [76, 2]
    instance.testKeuzelijst = 'waarde-4'
    instance.testKeuzelijstMetKard = ['waarde-4', 'waarde-3']
    instance.testKwantWrd.waarde = 98.21
    instance._testKwantWrdMetKard.add_empty_value()
    instance._testKwantWrdMetKard.add_empty_value()
    instance.testKwantWrdMetKard[0].waarde = 10.0
    instance.testKwantWrdMetKard[1].waarde = 20.0
    instance.testStringField = 'oFfeDLp'
    instance.testStringFieldMetKard = ['string1', 'string2']
    instance.testTimeField = time(11, 5, 26)

    CsvExporter.from_objects(sequence_of_objects=[instance], filepath=file_location, split_per_type=False,
                             model_directory=model_directory_path)

    with open(file_location, newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=';')
        lines = list(csv_reader)
    assert len(lines) == 2

    line_0 = lines[0]
    assert line_0 == ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testBooleanField',
                      'testDateField', 'testDateTimeField', 'testDecimalField', 'testDecimalFieldMetKard[]',
                      'testEenvoudigType', 'testEenvoudigTypeMetKard[]', 'testIntegerField',
                      'testIntegerFieldMetKard[]', 'testKeuzelijst', 'testKeuzelijstMetKard[]',
                      'testKwantWrd', 'testKwantWrdMetKard[]', 'testStringField', 'testStringFieldMetKard[]',
                      'testTimeField']

    line_1 = lines[1]
    assert line_1 == ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000', '', 'False',
                      '2019-09-20', '2001-12-15 22:22:15', '79.07', '10.0|20.0', 'string1', 'string1|string2', '-55',
                      '76|2', 'waarde-4', 'waarde-4|waarde-3', '98.21', '10.0|20.0', 'oFfeDLp', 'string1|string2',
                      '11:05:26']

    shutil.rmtree(temp_dir_path)


def test_export_unnested_attributes_split_per_type():
    temp_dir_path = Path(__file__).parent / 'remove_after_test'
    os.mkdir(temp_dir_path)
    file_location = temp_dir_path / 'unnested.csv'

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testStringField = 'oFfeDLp'

    instance2 = AnotherTestClass()
    instance2.assetId.identificator = '0001'
    instance2.notitie = 'notitie'

    CsvExporter.from_objects(sequence_of_objects=[instance, instance2], filepath=file_location, split_per_type=True,
                             model_directory=model_directory_path)

    with open(temp_dir_path / 'unnested_onderdeel_AllCasesTestClass.csv', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=';')
        lines = list(csv_reader)
    assert len(lines) == 2

    line_0 = lines[0]
    assert line_0 == ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testStringField']

    line_1 = lines[1]
    assert line_1 == ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000', '', 'oFfeDLp']

    with open(temp_dir_path / 'unnested_onderdeel_AnotherTestClass.csv', 'r') as file:
        lines = list(file)
    assert len(lines) == 2

    line_0 = lines[0].split(';')
    assert line_0 == ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'notitie\n']

    line_1 = lines[1].split(';')
    assert line_1 == ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass', '0001', '',
                      'notitie\n']

    shutil.rmtree(temp_dir_path)


def test_export_and_then_import_nested_attributes_level_1():
    temp_dir_path = Path(__file__).parent / 'remove_after_test'
    os.mkdir(temp_dir_path)
    file_location = temp_dir_path / 'nested_level_1.csv'

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'

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

    CsvExporter.from_objects(sequence_of_objects=[instance], filepath=file_location, split_per_type=False,
                             model_directory=model_directory_path)

    with open(file_location, newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=';', quotechar='"')
        lines = list(csv_reader)

    assert len(lines) == 2

    line_0 = lines[0]
    assert line_0 == ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testComplexType.testBooleanField',
                      'testComplexType.testKwantWrd', 'testComplexType.testKwantWrdMetKard[]',
                      'testComplexType.testStringField', 'testComplexType.testStringFieldMetKard[]',
                      'testComplexTypeMetKard[].testBooleanField', 'testComplexTypeMetKard[].testKwantWrd',
                      'testComplexTypeMetKard[].testStringField', 'testUnionType.unionString',
                      'testUnionTypeMetKard[].unionKwantWrd']
    line_1 = lines[1]
    assert line_1 == ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000', '',
                      'True', '65.14', '10.0|20.0', 'KmCtMXM', 'string1|string2', 'True|False', '10.0|20.0',
                      'string1|string2', 'RWKofW', '10.0|20.0']

    shutil.rmtree(temp_dir_path)


def test_export_and_then_import_nested_attributes_level_2():
    temp_dir_path = Path(__file__).parent / 'remove_after_test'
    os.mkdir(temp_dir_path)
    file_location = temp_dir_path / 'nested_level_2.csv'

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

    CsvExporter.from_objects(sequence_of_objects=[instance], filepath=file_location, split_per_type=False,
                             model_directory=model_directory_path)

    with open(file_location, newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=';', quotechar='"')
        lines = list(csv_reader)

    assert len(lines) == 2

    line_0 = lines[0]
    assert line_0 == ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor',
                      'testComplexType.testComplexType2.testKwantWrd',
                      'testComplexType.testComplexType2.testStringField',
                      'testComplexType.testComplexType2MetKard[].testKwantWrd',
                      'testComplexType.testComplexType2MetKard[].testStringField',
                      'testComplexTypeMetKard[].testComplexType2.testKwantWrd',
                      'testComplexTypeMetKard[].testComplexType2.testStringField']

    line_1 = lines[1]
    assert line_1 == ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000', '',
                      '76.8', 'GZBzgRhOrQvfZaN', '10.0|20.0', 'string1|string2', '10.0|20.0', 'string1|string2']

    shutil.rmtree(temp_dir_path)


def test_export_list_of_lists():
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_lists.csv'

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde = 10.0

    with pytest.raises(DotnotationListOfListError):
        CsvExporter.from_objects(sequence_of_objects=[instance], filepath=file_location, split_per_type=False)
