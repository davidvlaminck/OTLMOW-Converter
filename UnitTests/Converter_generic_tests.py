import os
from datetime import date
from pathlib import Path

import pytest

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_converter.SettingsManager import update_settings_by_dict

model_directory_path = Path(__file__).parent / 'TestModel'


def test_generic_use_of_to_dicts():
    instance1 = AllCasesTestClass()
    instance1.notitie = 'notitie'
    instance2 = AnotherTestClass()
    instance2.notitie = 'notitie2'
    sequence_of_objects = [instance1, instance2]

    dicts = OtlmowConverter.from_objects_to_dicts(sequence_of_objects)
    assert list(dicts) == [{'notitie': 'notitie',
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'},
                           {'notitie': 'notitie2',
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'}]

    dicts = OtlmowConverter.from_objects_to_dicts(sequence_of_objects, rdf=True)
    assert list(dicts) == [
        {'@type': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
         'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.notitie': 'notitie'},
        {'@type': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
         'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.notitie': 'notitie2'}]


def test_using_to_dicts_with_altered_settings():
    instance1 = AllCasesTestClass()
    instance1.testDateField = date(2020, 1, 1)
    sequence_of_objects = [instance1]

    settings = {
        "formats": {
            "OTLMOW": {
                "cast_datetime": True
            }
        }
    }

    dicts = OtlmowConverter.from_objects_to_dicts(sequence_of_objects)
    assert list(dicts) == [{'testDateField': date(2020, 1, 1),
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'}]

    update_settings_by_dict(settings)
    dicts = OtlmowConverter.from_objects_to_dicts(sequence_of_objects)
    assert list(dicts) == [{'testDateField': "2020-01-01",
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'}]


def test_generic_use_of_from_dicts():
    dicts = [{'notitie': 'notitie',
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'},
                           {'notitie': 'notitie2',
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'}]
    objects = OtlmowConverter.from_dicts_to_objects(dicts, model_directory=model_directory_path)
    instance1 = AllCasesTestClass()
    instance1.notitie = 'notitie'
    instance2 = AnotherTestClass()
    instance2.notitie = 'notitie2'
    sequence_of_objects = [instance1, instance2]
    assert list(objects) == sequence_of_objects


def test_generic_file_uses():
    orig_list_of_dicts = [{
        'typeURI': AllCasesTestClass.typeURI,
        'assetId': {'identificator': 'id1'},
        'testBooleanField': True,
        'testDateField': date(2020, 1, 1),
        'testStringFieldMetKard': ['test1', 'test2']
    }, {
        'typeURI': AnotherTestClass.typeURI,
        'assetId': {'identificator': 'id2'},
        'notitie': 'note',
        'non_conform_attribute': 'non conform value'
    }]
    excel_file_path = Path(__file__).parent / 'test_excel.xlsx'
    json_file_path = Path(__file__).parent / 'test_excel.json'

    list_of_objects_1 = OtlmowConverter.from_dicts_to_objects(orig_list_of_dicts,
                                                              model_directory=model_directory_path)
    OtlmowConverter.from_objects_to_file(sequence_of_objects=list_of_objects_1, file_path=excel_file_path)
    list_of_objects_2 = OtlmowConverter.from_file_to_objects(file_path=excel_file_path,
                                                             model_directory=model_directory_path)
    new_list_of_dicts = list(OtlmowConverter.from_objects_to_dicts(list_of_objects_2))
    assert orig_list_of_dicts == new_list_of_dicts

    OtlmowConverter.from_objects_to_file(sequence_of_objects=list_of_objects_2, file_path=json_file_path)
    list_of_objects_3 = OtlmowConverter.from_file_to_objects(file_path=json_file_path,
                                                             model_directory=model_directory_path)
    new_list_of_dicts = list(OtlmowConverter.from_objects_to_dicts(list_of_objects_3))
    assert orig_list_of_dicts == new_list_of_dicts

    os.unlink(excel_file_path)
    os.unlink(json_file_path)


@pytest.mark.skip(reason="Not implemented yet")
def test_generic_dataframe_uses():
    orig_list_of_dicts = [{
        'typeURI': AllCasesTestClass.typeURI,
        'assetId': {'identificator': 'id1'},
        'testBooleanField': True,
        'testDateField': date(2020, 1, 1),
        'testStringFieldMetKard': ['test1', 'test2']
    }, {
        'typeURI': AnotherTestClass.typeURI,
        'assetId': {'identificator': 'id2'},
        'notitie': 'note',
        #'non_conform_attribute': 'non conform value'
    }]
    excel_file_path = Path(__file__).parent / 'test_excel.xlsx'
    json_file_path = Path(__file__).parent / 'test_excel.json'

    list_of_objects_1 = OtlmowConverter.from_dicts_to_objects(orig_list_of_dicts,
                                                              model_directory=model_directory_path)
    OtlmowConverter.from_objects_to_file(sequence_of_objects=list_of_objects_1, file_path=excel_file_path)
    list_of_objects_2 = OtlmowConverter.from_file_to_objects(file_path=excel_file_path,
                                                             model_directory=model_directory_path)
    new_list_of_dicts = list(OtlmowConverter.from_objects_to_dicts(list_of_objects_2))
    assert orig_list_of_dicts == new_list_of_dicts

    OtlmowConverter.from_objects_to_file(sequence_of_objects=list_of_objects_2, file_path=json_file_path)
    list_of_objects_3 = OtlmowConverter.from_file_to_objects(file_path=json_file_path,
                                                             model_directory=model_directory_path)
    new_list_of_dicts = list(OtlmowConverter.from_objects_to_dicts(list_of_objects_3))
    assert orig_list_of_dicts == new_list_of_dicts

    dataframe = OtlmowConverter.from_objects_to_dataframe(sequence_of_objects=list_of_objects_3)
    list_of_objects_4 = OtlmowConverter.from_dataframe_to_objects(dataframe, model_directory=model_directory_path)
    new_list_of_dicts = list(OtlmowConverter.from_objects_to_dicts(list_of_objects_4))

    assert orig_list_of_dicts == new_list_of_dicts
