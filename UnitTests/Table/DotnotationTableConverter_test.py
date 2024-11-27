from pathlib import Path

import pytest

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_get_data_from_table():
    list_of_dicts_data = [
        {'typeURI': 0, 'assetId.identificator': 1, 'assetId.toegekendDoor': 2, 'testStringField': 3},
        {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
         'assetId.identificator': '0', 'testStringField': 'string1'},
        {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
         'assetId.identificator': '1'}]

    objects = DotnotationTableConverter.get_data_from_table(list_of_dicts_data, model_directory=model_directory_path)
    assert len(objects) == 2

    assert objects[0].assetId.identificator == '0'
    assert objects[0].testStringField == 'string1'
    assert objects[0].assetId.toegekendDoor is None
    assert objects[0].typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'

    assert objects[1].assetId.identificator == '1'
    assert objects[1].assetId.toegekendDoor is None
    assert objects[1].typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'


def test_get_single_table_from_data():
    instance_1 = AllCasesTestClass()
    instance_1.assetId.identificator = '0'
    instance_1.testStringField = 'string1'

    instance_2 = AnotherTestClass()
    instance_2.assetId.identificator = '1'
    instance_2.notitie = 'notitie'

    expected_list_of_dicts_data = [
        {'typeURI': 0, 'assetId.identificator': 1, 'assetId.toegekendDoor': 2, 'testStringField': 3, 'notitie': 4},
        {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
         'assetId.identificator': '0', 'testStringField': 'string1'},
        {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
         'assetId.identificator': '1', 'notitie': 'notitie'}]

    list_of_dicts = DotnotationTableConverter.get_single_table_from_data([instance_1, instance_2])
    assert list_of_dicts == expected_list_of_dicts_data


def test_get_single_table_from_data_errors():
    with pytest.raises(ValueError):
        instance_1 = AllCasesTestClass()
        instance_1.testStringField = 'string1'
        DotnotationTableConverter.get_single_table_from_data([instance_1], allow_empty_asset_id=False)

    with pytest.raises(ValueError):
        instance_1 = AllCasesTestClass()
        instance_1.testStringField = 'string1'
        instance_1.assetId.identificator = ''
        DotnotationTableConverter.get_single_table_from_data([instance_1], allow_empty_asset_id=False)

def test_get_single_table_from_data_empty():
    objects = DotnotationTableConverter.get_single_table_from_data([])
    assert objects == [{'assetId.identificator': 1, 'assetId.toegekendDoor': 2, 'typeURI': 0}]


def test_get_tables_per_type_from_data():
    instance_1 = AllCasesTestClass()
    instance_1.assetId.identificator = '0'
    instance_1.testStringField = 'string1'

    instance_2 = AnotherTestClass()
    instance_2.assetId.identificator = '1'
    instance_2.notitie = 'notitie'

    expected_list_of_dicts_data = {
        'onderdeel#AllCasesTestClass': [
            {'typeURI': 0, 'assetId.identificator': 1, 'assetId.toegekendDoor': 2, 'testStringField': 3},
            {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
             'assetId.identificator': '0', 'testStringField': 'string1'}
        ],
        'onderdeel#AnotherTestClass': [
            {'typeURI': 0, 'assetId.identificator': 1, 'assetId.toegekendDoor': 2, 'notitie': 3},
            {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
             'assetId.identificator': '1', 'notitie': 'notitie'}
        ]
    }

    list_of_dicts = DotnotationTableConverter.get_tables_per_type_from_data([instance_1, instance_2])
    assert list_of_dicts == expected_list_of_dicts_data


def test_transform_list_of_dicts_to_2d_sequence():
    list_of_dicts_data = [
        {'typeURI': 0, 'assetId.identificator': 1, 'assetId.toegekendDoor': 2, 'testStringField': 3},
        {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
         'assetId.identificator': '0', 'testStringField': 'string1'},
        {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
         'assetId.identificator': '1'}]
    expected_2d_sequence = [
        ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testStringField'],
        ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0', None, 'string1'],
        ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass', '1', None, None]]

    sequence_2d = DotnotationTableConverter.transform_list_of_dicts_to_2d_sequence(list_of_dicts_data)

    assert sequence_2d == expected_2d_sequence


def test_transform_2d_sequence_to_list_of_dicts():
    expected_list_of_dicts = [
        {'typeURI': 0, 'assetId.identificator': 1, 'assetId.toegekendDoor': 2, 'testStringField': 3},
        {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
         'assetId.identificator': '0', 'testStringField': 'string1'},
        {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
         'assetId.identificator': '1'}]
    sequence_2d = [
        ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testStringField'],
        ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0', None, 'string1'],
        ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass', '1', None, None]]

    list_of_dicts = DotnotationTableConverter.transform_2d_sequence_to_list_of_dicts(sequence_2d)

    assert list_of_dicts == expected_list_of_dicts
