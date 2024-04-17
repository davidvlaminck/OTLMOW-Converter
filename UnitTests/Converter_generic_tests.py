import json
import os
from datetime import date
from pathlib import Path

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.OtlmowConverter import OtlmowConverter, to_objects
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

    dicts = OtlmowConverter.from_objects_to_dicts(sequence_of_objects, cast_datetime=False)
    assert list(dicts) == [{'testDateField': date(2020, 1, 1),
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'}]

    update_settings_by_dict(settings)
    dicts = OtlmowConverter.from_objects_to_dicts(sequence_of_objects, cast_datetime=True)
    assert list(dicts) == [{'testDateField': "2020-01-01",
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'}]

    orig_settings = {
        "formats": {
            "OTLMOW": {
                "cast_datetime": False
            }
        }
    }
    update_settings_by_dict(orig_settings)


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


def test_generic_uses():
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
    excel_file_path = Path(__file__).parent / 'test_generic_use.xlsx'
    json_file_path = Path(__file__).parent / 'test_generic_use.json'

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

    if excel_file_path.exists():
        os.unlink(excel_file_path)
    if json_file_path.exists():
        os.unlink(json_file_path)


def test_generic_to_objects(subtests):
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
    json_file_path = Path(__file__).parent / 'test_generic_to_objects.json'

    orig_list_of_objects = list(OtlmowConverter.from_dicts_to_objects(orig_list_of_dicts,
                                                                      model_directory=model_directory_path))

    with subtests.test(msg="list of dicts to_objects"):
        generic_objects_1 = list(OtlmowConverter.to_objects(orig_list_of_dicts, model_directory=model_directory_path))
        assert generic_objects_1 == orig_list_of_objects

    with subtests.test(msg="file to_objects"):
        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=json_file_path)
        generic_objects_2 = list(OtlmowConverter.to_objects(json_file_path, model_directory=model_directory_path))
        assert generic_objects_2 == orig_list_of_objects

        if json_file_path.exists():
            os.unlink(json_file_path)

    with subtests.test(msg="dataframe to_objects"):
        df = OtlmowConverter.from_objects_to_dataframe(sequence_of_objects=orig_list_of_objects)
        generic_objects_3 = list(OtlmowConverter.to_objects(df, model_directory=model_directory_path))
        assert generic_objects_3 == orig_list_of_objects

    with subtests.test(msg="dotnotation_dicts to_objects"):
        d_dicts = OtlmowConverter.from_objects_to_dotnotation_dicts(sequence_of_objects=orig_list_of_objects)
        generic_objects_4 = list(to_objects(d_dicts, model_directory=model_directory_path))
        assert generic_objects_4 == orig_list_of_objects

    with subtests.test(msg="objects to_objects"):
        generic_objects_5 = list(to_objects(orig_list_of_objects, model_directory=model_directory_path))
        assert generic_objects_5 == orig_list_of_objects


def test_generic_to_file(subtests):
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
    expected_file_path = Path(__file__).parent / 'test_generic_input_to_file.json'
    output_file_path = Path(__file__).parent / 'test_generic_to_file.json'

    orig_list_of_objects = list(OtlmowConverter.from_dicts_to_objects(orig_list_of_dicts,
                                                                      model_directory=model_directory_path))
    OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=expected_file_path)

    with subtests.test(msg="file to_file"):
        OtlmowConverter.to_file(subject=expected_file_path, file_path=output_file_path)
        assert json.load(output_file_path.open()) == json.load(expected_file_path.open())

    with subtests.test(msg="objects to_file"):
        OtlmowConverter.to_file(subject=orig_list_of_objects, file_path=output_file_path)
        assert json.load(output_file_path.open()) == json.load(expected_file_path.open())

    with subtests.test(msg="dicts to_file"):
        OtlmowConverter.to_file(subject=orig_list_of_dicts, file_path=output_file_path)
        assert json.load(output_file_path.open()) == json.load(expected_file_path.open())

    with subtests.test(msg="dotnotation_dicts to_file"):
        dd_list = OtlmowConverter.from_objects_to_dotnotation_dicts(sequence_of_objects=orig_list_of_objects)
        OtlmowConverter.to_file(subject=dd_list, file_path=output_file_path)
        assert json.load(output_file_path.open()) == json.load(expected_file_path.open())

    with subtests.test(msg="dataframe to_file"):
        df = OtlmowConverter.from_objects_to_dataframe(sequence_of_objects=orig_list_of_objects)
        OtlmowConverter.to_file(subject=df, file_path=output_file_path)
        assert json.load(output_file_path.open()) == json.load(expected_file_path.open())

    if expected_file_path.exists():
        os.unlink(expected_file_path)
    if output_file_path.exists():
        os.unlink(output_file_path)


