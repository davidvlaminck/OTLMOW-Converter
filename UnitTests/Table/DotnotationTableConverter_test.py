from datetime import date
from pathlib import Path

import pytest
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from UnitTests.SettingManagerForUnit_test import get_settings_path_for_unittests
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.Exceptions.BadTypeWarning import BadTypeWarning
from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter
from otlmow_converter.FileFormats.DotnotationTableImporter import DotnotationTableImporter
from otlmow_converter.SettingsManager import load_settings

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def set_up_converter(class_dir_test_class=True):
    settings_file_location = get_settings_path_for_unittests()
    settings = load_settings(settings_file_location)
    csv_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'csv'), None)
    if class_dir_test_class:
        model_directory = model_directory_path
    else:
        model_directory = None
    converter = DotnotationTableConverter(model_directory=model_directory)
    converter.load_settings(dotnotation_settings=csv_settings['dotnotation'])
    return converter


def test_init_exporter_only_load_with_settings(subtests):
    with subtests.test(msg='load with correct settings'):
        exporter = set_up_converter()
        assert exporter is not None

    with subtests.test(msg='_import_otl_object otlmow_model'):
        exporter = set_up_converter(class_dir_test_class=False)
        assert exporter.otl_object_ref.typeURI is None

    with subtests.test(msg='_import_otl_object unittestclass'):
        exporter = set_up_converter()
        assert exporter.otl_object_ref.typeURI is None
        assert issubclass(exporter.otl_object_ref, OTLObject) == True


def test_get_data_from_table():
    importer = set_up_converter()

    list_of_dicts_data = [
        {'typeURI': 0, 'assetId.identificator': 1, 'assetId.toegekendDoor': 2, 'testStringField': 3},
        {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
         'assetId.identificator': '0', 'testStringField': 'string1'},
        {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
         'assetId.identificator': '1'}]

    objects = importer.get_data_from_table(list_of_dicts_data)
    assert len(objects) == 2

    assert objects[0].assetId.identificator == '0'
    assert objects[0].testStringField == 'string1'
    assert objects[0].assetId.toegekendDoor is None
    assert objects[0].typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'

    assert objects[1].assetId.identificator == '1'
    assert objects[1].assetId.toegekendDoor is None
    assert objects[1].typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'


def test_transform_list_of_dicts_to_2d_sequence():
    importer = set_up_converter()

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

    sequence_2d = importer.transform_list_of_dicts_to_2d_sequence(list_of_dicts_data)

    assert sequence_2d == expected_2d_sequence


def test_transform_2d_sequence_to_list_of_dicts():
    importer = set_up_converter()

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

    list_of_dicts = importer.transform_2d_sequence_to_list_of_dicts(sequence_2d)

    assert list_of_dicts == expected_list_of_dicts


#
# def test_master_dict_basic_functionality(subtests):
#     with subtests.test(msg='empty list'):
#         exporter = set_up_importer()
#         exporter.fill_master_dict([])
#         expected_master_dict = {}
#         assert expected_master_dict == exporter.master
#
#     with subtests.test(msg='list with bad object'):
#         with pytest.warns(BadTypeWarning):
#             exporter = set_up_importer()
#             exporter.fill_master_dict([BadTypeWarning])
#             expected_master_dict = {}
#             assert expected_master_dict == exporter.master
#
#     with subtests.test(msg='single AllCasesTestClass'):
#         exporter = set_up_importer()
#         exporter.ignore_empty_asset_id = True
#         exporter.fill_master_dict([AllCasesTestClass()])
#         expected_master_dict = {'onderdeel#AllCasesTestClass': {
#             'headers': ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'],
#             'data': [{
#                 'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
#                 'assetId.identificator': None, 'assetId.toegekendDoor': None
#             }]
#         }}
#         assert expected_master_dict == exporter.master
#
#     with subtests.test(msg='double AllCasesTestClass'):
#         exporter = set_up_importer()
#         exporter.ignore_empty_asset_id = True
#         exporter.fill_master_dict([AllCasesTestClass(), AllCasesTestClass()])
#         expected_master_dict = {'onderdeel#AllCasesTestClass': {
#             'headers': ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'],
#             'data': [{
#                 'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
#                 'assetId.identificator': None, 'assetId.toegekendDoor': None
#             }, {
#                 'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
#                 'assetId.identificator': None, 'assetId.toegekendDoor': None
#             }]
#         }}
#
#         assert expected_master_dict == exporter.master
#
#     with subtests.test(msg='two different classes'):
#         exporter = set_up_importer()
#         exporter.ignore_empty_asset_id = True
#         exporter.fill_master_dict([AllCasesTestClass(), AnotherTestClass()])
#         expected_master_dict = {'onderdeel#AllCasesTestClass': {
#             'headers': ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'],
#             'data': [{
#                 'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
#                 'assetId.identificator': None, 'assetId.toegekendDoor': None
#             }]
#         }, 'onderdeel#AnotherTestClass': {
#             'headers': ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'],
#             'data': [{
#                 'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
#                 'assetId.identificator': None, 'assetId.toegekendDoor': None
#             }]
#         }}
#         assert expected_master_dict == exporter.master
#
#     with subtests.test(msg='two different classes, split_per_type=False'):
#         exporter = set_up_importer()
#         exporter.ignore_empty_asset_id = True
#         list_of_objects = [AllCasesTestClass(), AnotherTestClass()]
#         list_of_objects[0].assetId.identificator = '0'
#         list_of_objects[1].assetId.identificator = '1'
#         list_of_objects[0].testStringField = 'string1'
#         list_of_objects[1].notitie = 'notitie2'
#
#         exporter.fill_master_dict(list_of_objects, split_per_type=False)
#         expected_master_dict = {'single': {
#             'headers': ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testStringField', 'notitie'],
#             'data': [{
#                 'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
#                 'assetId.identificator': '0', 'assetId.toegekendDoor': None, 'testStringField': 'string1'
#             }, {
#                 'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
#                 'assetId.identificator': '1', 'assetId.toegekendDoor': None, 'notitie': 'notitie2'
#             }]
#         }}
#         assert expected_master_dict == exporter.master
#
#
# def test_sort_headers(subtests):
#     with subtests.test(msg='no headers'):
#         result = DotnotationTableExporter._sort_headers(['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'])
#         expected = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor']
#         assert expected == result
#
#     with subtests.test(msg='2 headers'):
#         result = DotnotationTableExporter._sort_headers(['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'b', 'a'])
#         expected = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'a', 'b']
#         assert expected == result
#
#     with subtests.test(msg='complex headers'):
#         result = DotnotationTableExporter._sort_headers(
#             ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'a.2', 'a.1'])
#         expected = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'a.1', 'a.2']
#         assert expected == result
#
#
# def test_fill_master_dict_edge_cases(subtests):
#     with subtests.test(msg='empty list of objects'):
#         exporter = set_up_importer()
#         list_of_objects = []
#         exporter.fill_master_dict(list_of_objects)
#         assert len(exporter.master.items()) == 0
#
#     with subtests.test(msg='object in list without valid assetId'):
#         exporter = set_up_importer()
#         with pytest.raises(ValueError):
#             list_of_objects = [AllCasesTestClass()]
#             exporter.fill_master_dict(list_of_objects)
#
#     with subtests.test(msg='object in list without valid assetId and ignore True'):
#         exporter = set_up_importer()
#         exporter.ignore_empty_asset_id = True
#         list_of_objects = [AllCasesTestClass()]
#         exporter.fill_master_dict(list_of_objects)
#         tabular_data = exporter.master['onderdeel#AllCasesTestClass']
#         assert None == tabular_data['data'][0]['assetId.identificator']
#
#     with subtests.test(msg='object in list without valid assetId -> empty string'):
#         exporter = set_up_importer()
#         with pytest.raises(ValueError):
#             list_of_objects = [AllCasesTestClass()]
#             list_of_objects[0].assetId.identificator = ''
#             exporter.fill_master_dict(list_of_objects)
#
#     with (subtests.test(msg='object in list with valid assetId -> string')):
#         exporter = set_up_importer()
#         list_of_objects = [AllCasesTestClass()]
#         list_of_objects[0].assetId.identificator = '0'
#         exporter.fill_master_dict(list_of_objects)
#         tabular_data = exporter.master['onderdeel#AllCasesTestClass']
#
#         assert 'typeURI' == tabular_data['headers'][0]
#         assert 'assetId.identificator' == tabular_data['headers'][1]
#         assert 'assetId.toegekendDoor' == tabular_data['headers'][2]
#         assert 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass' == tabular_data['data'][0]['typeURI']
#         assert '0' == tabular_data['data'][0]['assetId.identificator']
#         assert None == tabular_data['data'][0]['assetId.toegekendDoor']
#
#
# def test_get_data_as_table_basic_functionality(subtests):
#     with subtests.test(msg='no data'):
#         exporter = set_up_importer()
#         exporter.ignore_empty_asset_id = True
#         exporter.fill_master_dict([])
#         with pytest.raises(ValueError):
#             exporter.get_data_as_table()
#
#     with subtests.test(msg='one object, no attributes'):
#         exporter = set_up_importer()
#         list_of_objects = [AllCasesTestClass()]
#         list_of_objects[0].assetId.identificator = '0'
#         exporter.fill_master_dict(list_of_objects)
#         table_data = exporter.get_data_as_table('onderdeel#AllCasesTestClass')
#         assert [['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'],
#                 ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0',
#                  '']] == table_data
#
#     with subtests.test(msg='one object, primitive attributes in reverse order'):
#         exporter = set_up_importer()
#         list_of_objects = [AllCasesTestClass()]
#         list_of_objects[0].assetId.identificator = '0'
#         list_of_objects[0].testStringField = 'test'
#         list_of_objects[0].testIntegerField = 1
#         exporter.fill_master_dict(list_of_objects)
#         table_data = exporter.get_data_as_table('onderdeel#AllCasesTestClass')
#         expected_data = [
#             ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testIntegerField', 'testStringField'],
#             ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0', '', '1', 'test']]
#         assert expected_data == table_data
#
#
# def test_get_data_as_table_two_different_types_split_false():
#     exporter = set_up_importer()
#     exporter.ignore_empty_asset_id = True
#     list_of_objects = [AllCasesTestClass(), AnotherTestClass()]
#     list_of_objects[0].assetId.identificator = '0'
#     list_of_objects[1].assetId.identificator = '1'
#     list_of_objects[0].testStringField = 'string1'
#     list_of_objects[1].notitie = 'notitie2'
#
#     exporter.fill_master_dict(list_of_objects, split_per_type=False)
#     table_data = exporter.get_data_as_table()
#     expected_data = [
#         ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'notitie', 'testStringField'],
#         ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0', '', '', 'string1'],
#         ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass', '1', '', 'notitie2', '']]
#     assert expected_data == table_data
#
#
# def test_get_data_as_table_basic_nonempty_objects_same_type():
#     exporter = set_up_importer()
#     list_of_objects = [AllCasesTestClass(), AllCasesTestClass()]
#     list_of_objects[0].assetId.identificator = '0'
#     list_of_objects[0].testDecimalField = 1.0
#     list_of_objects[0].testBooleanField = True
#     list_of_objects[0].testKeuzelijst = 'waarde-1'
#     list_of_objects[0].testComplexType.testStringField = 'string in complex veld'
#     list_of_objects[0].testComplexType.testKwantWrd.waarde = 2.0
#
#     list_of_objects[1].assetId.identificator = '1'
#     list_of_objects[1].testBooleanField = False
#     list_of_objects[1].testKeuzelijstMetKard = ['waarde-2']
#     list_of_objects[1].testDateField = date(2022, 2, 2)
#     list_of_objects[1].testDecimalField = 2.5
#
#     exporter.fill_master_dict(list_of_objects)
#     table_data = exporter.get_data_as_table('onderdeel#AllCasesTestClass')
#     expected_data = [
#         ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testBooleanField',
#          'testComplexType.testKwantWrd', 'testComplexType.testStringField', 'testDateField', 'testDecimalField',
#          'testKeuzelijst', 'testKeuzelijstMetKard[]'],
#         ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0', '', 'True', '2.0',
#          'string in complex veld', '', '1.0', 'waarde-1', ''],
#         ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '1', '', 'False', '', '',
#          '2022-02-02', '2.5', '', 'waarde-2']]
#     assert expected_data == table_data
#
#
# def test_fill_master_dict_cardinality(subtests):
#     with subtests.test(msg='empty list'):
#         exporter = set_up_importer()
#         list_of_objects = [AllCasesTestClass()]
#         list_of_objects[0].assetId.identificator = '0'
#         list_of_objects[0].testStringFieldMetKard = []
#         exporter.fill_master_dict(list_of_objects)
#         assert [] == exporter.master['onderdeel#AllCasesTestClass']['data'][0]['testStringFieldMetKard[]']
#
#     with subtests.test(msg='list one element'):
#         exporter = set_up_importer()
#         list_of_objects = [AllCasesTestClass()]
#         list_of_objects[0].assetId.identificator = '0'
#         list_of_objects[0].testStringFieldMetKard = ['test']
#         exporter.fill_master_dict(list_of_objects)
#         assert ['test'] == exporter.master['onderdeel#AllCasesTestClass']['data'][0]['testStringFieldMetKard[]']
#
#     with subtests.test(msg='list multiple elements'):
#         exporter = set_up_importer()
#         list_of_objects = [AllCasesTestClass()]
#         list_of_objects[0].assetId.identificator = '0'
#         list_of_objects[0].testStringFieldMetKard = ['string1', 'string2']
#         exporter.fill_master_dict(list_of_objects)
#         assert ['string1', 'string2'] == exporter.master['onderdeel#AllCasesTestClass']['data'][0][
#             'testStringFieldMetKard[]']
#
#
# def test_stringify_value(subtests):
#     exporter = set_up_importer()
#     with subtests.test(msg='None, values_as_strings = True'):
#         assert '' == exporter._stringify_value(None)
#     with subtests.test(msg='None, values_as_strings = False'):
#         assert None == exporter._stringify_value(None, values_as_strings=False)
#     with subtests.test(msg='str, values_as_strings = True'):
#         assert 'test1' == exporter._stringify_value('test1')
#     with subtests.test(msg='str, values_as_strings = False'):
#         assert 'test2' == exporter._stringify_value('test2', values_as_strings=False)
#     with subtests.test(msg='date, values_as_strings = True'):
#         assert '2022-02-01' == exporter._stringify_value(date(2022, 2, 1))
#     with subtests.test(msg='date, values_as_strings = False'):
#         assert date(2022, 2, 2) == exporter._stringify_value(date(2022, 2, 2), values_as_strings=False)
#     with subtests.test(msg='float, values_as_strings = True'):
#         assert '1.0' == exporter._stringify_value(1.00)
#     with subtests.test(msg='float, values_as_strings = False'):
#         assert 2.0 == exporter._stringify_value(2.00, values_as_strings=False)
#     with subtests.test(msg='empty list'):
#         assert '' == exporter._stringify_value([])
#     with subtests.test(msg='list of 1 strings, values_as_strings = True'):
#         assert '1' == exporter._stringify_value(['1'])
#     with subtests.test(msg='list of 2 strings, values_as_strings = True'):
#         assert '1|2' == exporter._stringify_value(['1', '2'])
#     with subtests.test(msg='list of 1 strings, values_as_strings = False'):
#         assert '1' == exporter._stringify_value(['1'], values_as_strings=False)
#     with subtests.test(msg='list of 2 strings, values_as_strings = False'):
#         assert '1|2' == exporter._stringify_value(['1', '2'], values_as_strings=False)
#     with subtests.test(msg='list of 1 floats, values_as_strings = True'):
#         assert '1.0' == exporter._stringify_value([1.00])
#     with subtests.test(msg='list of 2 floats, values_as_strings = True'):
#         assert '1.0|2.0' == exporter._stringify_value([1.00, 2.00])
#     with subtests.test(msg='list of 1 floats, values_as_strings = False'):
#         assert '1.0' == exporter._stringify_value([1.00], values_as_strings=False)
#     with subtests.test(msg='list of 2 floats, values_as_strings = False'):
#         assert '1.0|2.0' == exporter._stringify_value([1.00, 2.00], values_as_strings=False)
#     with subtests.test(msg='list of 1 float and None, values_as_strings = False'):
#         assert '1.0|' == exporter._stringify_value([1.00, None], values_as_strings=False)
#     with subtests.test(msg='list of None and 1 float, values_as_strings = False'):
#         assert '|2.0' == exporter._stringify_value([None, 2.00], values_as_strings=False)
#     with subtests.test(msg='list of list'):
#         with pytest.raises(ValueError):
#             exporter._stringify_value([[]])
#
#
# def test_get_data_as_table_different_cardinality_among_subattributes(subtests):
#     with subtests.test(msg='empty list'):
#         exporter = set_up_importer()
#         instance = AllCasesTestClass()
#         instance.assetId.identificator = '0000-0000'
#
#         instance._testComplexTypeMetKard.add_empty_value()
#         instance.testComplexTypeMetKard[0].testBooleanField = False
#         instance.testComplexTypeMetKard[0].testStringField = '1.1'
#         instance._testComplexTypeMetKard.add_empty_value()
#         instance.testComplexTypeMetKard[1].testBooleanField = True
#         instance.testComplexTypeMetKard[1].testKwantWrd.waarde = 2.0
#         instance.testComplexTypeMetKard[1].testStringField = '1.2'
#         instance._testComplexTypeMetKard.add_empty_value()
#         instance.testComplexTypeMetKard[2].testStringField = '1.3'
#
#         exporter.fill_master_dict([instance])
#         table_data = exporter.get_data_as_table('onderdeel#AllCasesTestClass')
#
#         expected_data = [
#             ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor',
#              'testComplexTypeMetKard[].testBooleanField', 'testComplexTypeMetKard[].testKwantWrd',
#              'testComplexTypeMetKard[].testStringField'],
#             ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000-0000', '',
#              'False|True|', '|2.0|', '1.1|1.2|1.3']]
#         assert expected_data == table_data
#
#
# def test_get_data_as_table_different_dotnotation_settings():
#     settings = {
#         "separator": "+",
#         "cardinality_separator": "*",
#         "cardinality_indicator": "()",
#         "waarde_shortcut": False
#     }
#     exporter = DotnotationTableExporter(dotnotation_settings=settings, model_directory=model_directory_path)
#
#     instance = AllCasesTestClass()
#     instance.assetId.identificator = '0000-0000'
#
#     instance._testComplexTypeMetKard.add_empty_value()
#     instance.testComplexTypeMetKard[0].testBooleanField = False
#     instance.testComplexTypeMetKard[0].testStringField = '1.1'
#     instance._testComplexTypeMetKard.add_empty_value()
#     instance.testComplexTypeMetKard[1].testBooleanField = True
#     instance.testComplexTypeMetKard[1].testKwantWrd.waarde = 2.0
#     instance.testComplexTypeMetKard[1].testStringField = '1.2'
#     instance._testComplexTypeMetKard.add_empty_value()
#     instance.testComplexTypeMetKard[2].testStringField = '1.3'
#
#     exporter.fill_master_dict([instance])
#     table_data = exporter.get_data_as_table('onderdeel#AllCasesTestClass')
#
#     expected_data = [
#         ['typeURI', 'assetId+identificator', 'assetId+toegekendDoor',
#          'testComplexTypeMetKard()+testBooleanField', 'testComplexTypeMetKard()+testKwantWrd+waarde',
#          'testComplexTypeMetKard()+testStringField'],
#         ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000-0000', '',
#          'False*True*', '*2.0*', '1.1*1.2*1.3']]
#     assert expected_data == table_data
