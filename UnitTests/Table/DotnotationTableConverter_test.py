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


# TODO check for additional tests in these comments

#     with subtests.test(msg='list with bad object'):
#         with pytest.warns(BadTypeWarning):
#             exporter = set_up_importer()
#             exporter.fill_master_dict([BadTypeWarning])
#             expected_master_dict = {}
#             assert expected_master_dict == exporter.master    #
#
#
# def test_fill_master_dict_edge_cases(subtests):

#     with subtests.test(msg='object in list without valid assetId and ignore True'):
#         exporter = set_up_importer()
#         exporter.ignore_empty_asset_id = True
#         list_of_objects = [AllCasesTestClass()]
#         exporter.fill_master_dict(list_of_objects)
#         tabular_data = exporter.master['onderdeel#AllCasesTestClass']
#         assert None == tabular_data['data'][0]['assetId.identificator']
#
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
##
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
