import os
import shutil
from datetime import date, datetime, time
from pathlib import Path

import pytest

from UnitTests.SettingManagerForUnit_test import get_settings_path_for_unittests
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.FileFormats.CsvExporter import CsvExporter
from otlmow_converter.FileFormats.CsvImporter import CsvImporter
from otlmow_converter.OtlmowConverter import OtlmowConverter

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def set_up_converter():
    settings_file_location = get_settings_path_for_unittests()
    return OtlmowConverter(settings_path=settings_file_location)


def test_init_importer_only_load_with_settings(subtests):
    converter = set_up_converter()

    with subtests.test(msg='load with correct settings'):
        exporter = CsvExporter(settings=converter.settings)
        assert exporter is not None

    with subtests.test(msg='load without settings'):
        with pytest.raises(ValueError):
            CsvExporter(settings=None)

    with subtests.test(msg='load with incorrect settings (no file_formats)'):
        with pytest.raises(ValueError):
            CsvExporter(settings={"auth_options": [{}]})

    with subtests.test(msg='load with incorrect settings (file_formats but no csv)'):
        with pytest.raises(ValueError):
            CsvExporter(settings={"file_formats": [{}]})


def test_import_then_export_file():
    converter = set_up_converter()
    importer = CsvImporter(settings=converter.settings)
    file_location = Path(__file__).parent / 'Testfiles' / 'import_then_export_input.csv'
    objects = importer.import_file(filepath=file_location, model_directory=model_directory_path)
    exporter = CsvExporter(settings=converter.settings, model_directory=model_directory_path)
    new_file_location = Path(__file__).parent / 'import_then_export_output.csv'
    if os.path.isfile(new_file_location):
        os.remove(new_file_location)
    exporter.export_to_file(list_of_objects=objects, filepath=new_file_location, split_per_type=False)
    assert os.path.isfile(new_file_location)

    with open(file_location, 'r') as input_file:
        input_file_lines = list(input_file)
    with open(new_file_location, 'r') as output_file:
        output_file_lines = list(output_file)
    assert input_file_lines == output_file_lines

    os.unlink(new_file_location)


def test_export_unnested_attributes():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    exporter = CsvExporter(settings=converter.settings, model_directory=model_directory_path)
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

    exporter.export_to_file(list_of_objects=[instance], filepath=file_location, split_per_type=False)

    with open(file_location, 'r') as file:
        lines = list(file)
    assert len(lines) == 2

    line_0 = lines[0].split(';')
    assert len(line_0) == 19
    assert line_0 == ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testBooleanField',
                      'testDateField', 'testDateTimeField', 'testDecimalField', 'testDecimalFieldMetKard[]',
                      'testEenvoudigType', 'testEenvoudigTypeMetKard[]', 'testIntegerField',
                      'testIntegerFieldMetKard[]', 'testKeuzelijst', 'testKeuzelijstMetKard[]',
                      'testKwantWrd', 'testKwantWrdMetKard[]', 'testStringField', 'testStringFieldMetKard[]',
                      'testTimeField\n']

    line_1 = lines[1].split(';')
    assert len(line_1) == 19
    assert line_1 == ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000', '', 'False',
                      '2019-09-20', '2001-12-15 22:22:15', '79.07', '10.0|20.0', 'string1', 'string1|string2', '-55',
                      '76|2', 'waarde-4', 'waarde-4|waarde-3', '98.21', '10.0|20.0', 'oFfeDLp', 'string1|string2',
                      '11:05:26\n']

    shutil.rmtree(temp_dir_path)


def test_export_unnested_attributes_split_per_type():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    exporter = CsvExporter(settings=converter.settings, model_directory=model_directory_path)
    temp_dir_path = Path(__file__).parent / 'remove_after_test'
    os.mkdir(temp_dir_path)
    file_location = temp_dir_path / 'unnested.csv'

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testStringField = 'oFfeDLp'

    instance2 = AnotherTestClass()
    instance2.assetId.identificator = '0001'
    instance2.notitie = 'notitie'

    exporter.export_to_file(list_of_objects=[instance, instance2], filepath=file_location, split_per_type=True)
    with open(temp_dir_path / 'unnested_onderdeel_AllCasesTestClass.csv', 'r') as file:
        lines = list(file)
    assert len(lines) == 2

    line_0 = lines[0].split(';')
    assert len(line_0) == 4
    assert line_0 == ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testStringField\n']

    line_1 = lines[1].split(';')
    assert len(line_1) == 4
    assert line_1 == ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000', '',
                      'oFfeDLp\n']

    with open(temp_dir_path / 'unnested_onderdeel_AnotherTestClass.csv', 'r') as file:
        lines = list(file)
    assert len(lines) == 2

    line_0 = lines[0].split(';')
    assert len(line_0) == 4
    assert line_0 == ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'notitie\n']

    line_1 = lines[1].split(';')
    assert len(line_1) == 4
    assert line_1 == ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass', '0001', '',
                      'notitie\n']

    shutil.rmtree(temp_dir_path)


def test_export_and_then_import_nested_attributes_level_1():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    importer = CsvImporter(settings=converter.settings)
    exporter = CsvExporter(settings=converter.settings, model_directory=model_directory_path)
    file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.csv'
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

    exporter.export_to_file(list_of_objects=[instance], filepath=file_location,
                            split_per_type=False)

    objects = importer.import_file(filepath=file_location, model_directory=model_directory_path)
    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == '0000'
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

    os.unlink(file_location)


def test_export_and_then_import_nested_attributes_level_2():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    importer = CsvImporter(settings=converter.settings)
    exporter = CsvExporter(settings=converter.settings, model_directory=model_directory_path)
    file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.csv'
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

    objects = importer.import_file(filepath=file_location, model_directory=model_directory_path)
    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == '0000'
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

    os.unlink(file_location)


def test_export_list_of_lists():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    exporter = CsvExporter(settings=converter.settings, model_directory=model_directory_path)
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_lists.csv'
    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde = 10.0
    with pytest.raises(ValueError):
        exporter.export_to_file(list_of_objects=[instance], filepath=file_location, split_per_type=False)
