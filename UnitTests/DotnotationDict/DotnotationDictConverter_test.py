from datetime import date, time, datetime
from pathlib import Path

import pytest
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import create_dict_from_asset
from otlmow_model.OtlmowModel.Exceptions.CouldNotCreateInstanceError import CouldNotCreateInstanceError
from otlmow_model.OtlmowModel.Exceptions.NonStandardAttributeWarning import NonStandardAttributeWarning

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.DotnotationDict import DotnotationDict
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_from_dict_simple_attributes():
    expected = AllCasesTestClass()
    expected.testKeuzelijst = 'waarde-2'
    expected.testBooleanField = True

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testBooleanField': True, 'testKeuzelijst': 'waarde-2'}),
        model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_simple_attributes_clear_values():
    expected = AllCasesTestClass()
    expected._testKeuzelijst.clear_value()
    expected._testBooleanField.clear_value()
    expected._testDecimalField.clear_value()
    expected._testDateTimeField.clear_value()
    expected._testIntegerField.clear_value()

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testBooleanField': '88888888', 'testKeuzelijst': '88888888',
            'testDecimalField': 88888888.0, 'testDateTimeField': '88888888', 'testIntegerField': 88888888}),
        model_directory=model_directory_path)

    assert created_instance == expected


def test_to_dict_simple_attributes():
    instance = AllCasesTestClass()
    instance.testKeuzelijst = 'waarde-2'
    instance.testBooleanField = True

    assert DotnotationDictConverter.to_dict(instance) == {'testBooleanField': True, 'testKeuzelijst': 'waarde-2',
                                                          'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_simple_attributes_clear_values():
    instance = AllCasesTestClass()
    instance._testKeuzelijst.clear_value()
    instance._testBooleanField.clear_value()
    instance._testDecimalField.clear_value()
    instance._testDateTimeField.clear_value()
    instance._testIntegerField.clear_value()

    assert DotnotationDictConverter.to_dict(instance) == {
        'typeURI': AllCasesTestClass.typeURI, 'testBooleanField': '88888888', 'testKeuzelijst': '88888888',
        'testDecimalField': 88888888.0, 'testDateTimeField': '88888888', 'testIntegerField': 88888888}


def test_from_dict_convert_types_without_warnings(recwarn):
    expected = AllCasesTestClass()
    expected._testComplexTypeMetKard.add_empty_value()
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[0].testBooleanField = True
    expected.testComplexTypeMetKard[1].testBooleanField = False
    expected.testComplexType._testKwantWrdMetKard.add_empty_value()
    expected.testComplexType._testKwantWrdMetKard.add_empty_value()
    expected.testComplexType.testKwantWrdMetKard[0].waarde = 3.0
    expected.testComplexType.testKwantWrdMetKard[1].waarde = 4.0
    expected.testDecimalFieldMetKard = [1.0, 2.0]

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI,
         'testComplexTypeMetKard[].testBooleanField': 'True|False',
         'testComplexType.testKwantWrdMetKard[]': '3.0|4.0',
         'testDecimalFieldMetKard[]': '1.0|2.0'
         }),
        model_directory=model_directory_path, cast_list=True, waarde_shortcut=True)

    assert created_instance == expected
    assert len(recwarn) == 0


def test_from_dict_datetime_convert_true(recwarn):
    expected = AllCasesTestClass()
    expected.testDateField = date(2022, 12, 12)
    expected.testTimeField = time(10, 11, 12)
    expected.testDateTimeField = datetime(2022, 12, 12, 10, 11, 12, 123456)

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testDateField': '2022-12-12', 'testTimeField': '10:11:12',
         'testDateTimeField': '2022-12-12 10:11:12.123456'}),
        model_directory=model_directory_path, cast_datetime=True)

    assert created_instance == expected
    assert len(recwarn) == 0


def test_from_dict_datetime_convert_false(recwarn):
    expected = AllCasesTestClass()
    expected.testDateField = date(2022, 12, 12)
    expected.testTimeField = time(10, 11, 12)
    expected.testDateTimeField = datetime(2022, 12, 12, 10, 11, 12, 123456)

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI,
         'testDateField': date(2022, 12, 12),
         'testTimeField': time(10, 11, 12),
         'testDateTimeField': datetime(2022, 12, 12, 10, 11, 12, 123456)}),
        model_directory=model_directory_path)

    assert created_instance == expected
    assert len(recwarn) == 0


def test_to_dict_datetime():
    instance = AllCasesTestClass()
    instance.testDateField = date(2022, 12, 12)
    instance.testTimeField = time(10, 11, 12)
    instance.testDateTimeField = datetime(2022, 12, 12, 10, 11, 12, 123456)

    assert DotnotationDictConverter.to_dict(instance, collect_native_types=True) == {
        'testDateField': date(2022, 12, 12),
        'testTimeField': time(10, 11, 12),
        'testDateTimeField': datetime(2022, 12, 12, 10, 11, 12, 123456),
        'typeURI': AllCasesTestClass.typeURI,
        '_native_type_dict': {
            'testDateField': date,
            'testTimeField': time,
            'testDateTimeField': datetime
        }
    }

    assert DotnotationDictConverter.to_dict(instance, cast_datetime=True) == {
        'testDateField': '2022-12-12',
        'testTimeField': '10:11:12',
        'testDateTimeField': '2022-12-12T10:11:12.123456',
        'typeURI': AllCasesTestClass.typeURI
    }


def test_from_dict_with_non_conform_otl_attributes(subtests, recwarn):
    expected = AllCasesTestClass()
    expected.non_conform_attribute = 'non-conform'
    expected.testBooleanField = True

    input_dict = DotnotationDict({'typeURI': AllCasesTestClass.typeURI, 'testBooleanField': True,
                                  'non_conform_attribute': 'non-conform'})

    with (subtests.test('Test with warn_for_non_otl_conform_attributes set to False')):
        created_instance = DotnotationDictConverter.from_dict(input_dict, model_directory=model_directory_path,
                                                              warn_for_non_otl_conform_attributes=False)

        assert create_dict_from_asset(created_instance, warn_for_non_otl_conform_attributes=False
                                      ) == create_dict_from_asset(expected, warn_for_non_otl_conform_attributes=False)
        assert len(recwarn) == 0

    with subtests.test('Test with allow_non_otl_conform_attributes set to True'):
        with pytest.warns(NonStandardAttributeWarning):
            created_instance = DotnotationDictConverter.from_dict(input_dict, model_directory=model_directory_path)

            assert created_instance == expected

    with subtests.test('Test with allow_non_otl_conform_attributes set to False'):
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(input_dict,
                                               model_directory=model_directory_path,
                                               allow_non_otl_conform_attributes=False)

    with subtests.test('Test with allow_non_otl_conform_attributes with bad key'):
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(
                DotnotationDict({'typeURI': AllCasesTestClass.typeURI, 'testBooleanField': True,
                                 '_non_conform_attribute': 'not a valid key name'}),
                model_directory=model_directory_path)


def test_to_dict_with_non_conform_otl_attributes(subtests, recwarn):
    with subtests.test('Test with warn_for_non_otl_conform_attributes set to False'):
        instance = AllCasesTestClass()
        instance.testBooleanField = True
        instance.non_conform_attribute = 'non-conform'

        assert DotnotationDictConverter.to_dict(instance, warn_for_non_otl_conform_attributes=False) == {
            'testBooleanField': True, 'non_conform_attribute': 'non-conform', 'typeURI': AllCasesTestClass.typeURI}
        assert len(recwarn) == 0

    with subtests.test('Test with allow_non_otl_conform_attributes set to True'):
        with pytest.warns(NonStandardAttributeWarning):
            instance = AllCasesTestClass()
            instance.testBooleanField = True
            instance.non_conform_attribute = 'non-conform'

            assert DotnotationDictConverter.to_dict(instance) == {
                'testBooleanField': True, 'non_conform_attribute': 'non-conform', 'typeURI': AllCasesTestClass.typeURI}

    with subtests.test('Test with allow_non_otl_conform_attributes set to False'):
        with pytest.raises(ValueError):
            instance = AllCasesTestClass()
            instance.non_conform_attribute = 'non-conform'

            DotnotationDictConverter.to_dict(instance, allow_non_otl_conform_attributes=False)

    with subtests.test('Test with allow_non_otl_conform_attributes with bad key'):
        with pytest.raises(ValueError):
            instance = AllCasesTestClass()
            instance._non_conform_attribute = 'not a valid key name'

            DotnotationDictConverter.to_dict(instance)


def test_from_dict_simple_attribute_with_cardinality():
    expected = AllCasesTestClass()
    expected.testIntegerFieldMetKard = [1, 2, 3]
    expected.testStringFieldMetKard = ['a', 'b', 'c']
    expected.testKeuzelijstMetKard = ['waarde-1', 'waarde-2', 'waarde-3']

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict({
        'typeURI': AllCasesTestClass.typeURI, 'testIntegerFieldMetKard[]': [1, 2, 3],
        'testStringFieldMetKard[]': ['a', 'b', 'c'],
        'testKeuzelijstMetKard[]': ['waarde-1', 'waarde-2', 'waarde-3']
    }), model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_simple_attribute_with_cardinality_clear_values():
    expected = AllCasesTestClass()
    expected.testIntegerFieldMetKard = '88888888'
    expected.testStringFieldMetKard = '88888888'
    expected.testKeuzelijstMetKard = '88888888'

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict({
        'typeURI': AllCasesTestClass.typeURI, 'testIntegerFieldMetKard[]': '88888888',
        'testStringFieldMetKard[]': '88888888',
        'testKeuzelijstMetKard[]': '88888888'
    }), model_directory=model_directory_path)

    assert created_instance == expected


def test_to_dict_native_types_dict_for_cardinality_and_nested():
    instance = AllCasesTestClass()
    instance.testIntegerFieldMetKard = [1, 2, 3]
    instance.testDateField = date(2022, 1, 1)
    instance.testComplexType.testBooleanField = True
    instance.testComplexTypeMetKard[0].testComplexType2.testKwantWrd.waarde = 20.0

    result = DotnotationDictConverter.to_dict(instance, collect_native_types=True)
    assert result['_native_type_dict']['testDateField'] == date
    assert result['_native_type_dict']['testComplexType.testBooleanField'] == bool
    assert result['_native_type_dict']['testComplexTypeMetKard[].testComplexType2.testKwantWrd'] == float
    assert result['_native_type_dict']['testIntegerFieldMetKard[]'] == int


def test_to_dict_native_types_dict_for_clear_values_and_lists():
    instance = AllCasesTestClass()
    instance._testDateField.clear_value()
    instance._testIntegerFieldMetKard.clear_value()
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[0]._testStringField.clear_value()

    result = DotnotationDictConverter.to_dict(instance, collect_native_types=True)
    assert result['_native_type_dict']['testDateField'] == date
    assert result['_native_type_dict']['testIntegerFieldMetKard[]'] == int
    assert result['_native_type_dict']['testComplexTypeMetKard[].testStringField'] == str


def test_to_dict_simple_attribute_with_cardinality():
    instance = AllCasesTestClass()
    instance.testIntegerFieldMetKard = [1, 2, 3]
    instance.testStringFieldMetKard = ['a', 'b', 'c']
    instance.testKeuzelijstMetKard = ['waarde-1', 'waarde-2', 'waarde-3']

    assert DotnotationDictConverter.to_dict(instance) == {
        'testIntegerFieldMetKard[]': [1, 2, 3],
        'testStringFieldMetKard[]': ['a', 'b', 'c'],
        'testKeuzelijstMetKard[]': ['waarde-1', 'waarde-2', 'waarde-3'],
        'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_simple_attribute_with_cardinality_clear_values():
    instance = AllCasesTestClass()
    instance.testIntegerFieldMetKard = '88888888'
    instance.testStringFieldMetKard = '88888888'
    instance.testKeuzelijstMetKard = '88888888'

    assert DotnotationDictConverter.to_dict(instance) == {
        'typeURI': AllCasesTestClass.typeURI,
        'testIntegerFieldMetKard[]': '88888888',
        'testStringFieldMetKard[]': '88888888',
        'testKeuzelijstMetKard[]': '88888888'
    }


def test_from_dict_simple_attribute_with_cardinality_convert_lists(recwarn):
    expected = AllCasesTestClass()
    expected.testIntegerFieldMetKard = [1, 2]
    expected._testKwantWrdMetKard.add_empty_value()
    expected.testKwantWrdMetKard[0].waarde = 1.0
    expected._testKwantWrdMetKard.add_empty_value()
    expected.testKwantWrdMetKard[1].waarde = 2.0
    expected.testStringFieldMetKard = ['a', 'b']
    expected.testKeuzelijstMetKard = ['waarde-1', 'waarde-2']

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict({
        'typeURI': AllCasesTestClass.typeURI, 'testIntegerFieldMetKard[]': '1|2',
        'testStringFieldMetKard[]': 'a|b', 'testKeuzelijstMetKard[]': 'waarde-1|waarde-2',
        'testKwantWrdMetKard[]': '1.0|2.0'}), cast_list=True, model_directory=model_directory_path)

    assert created_instance == expected
    assert len(recwarn) == 0


def test_from_dict_simple_attribute_with_cardinality_convert_lists_clear_values(recwarn):
    expected = AllCasesTestClass()
    expected.testIntegerFieldMetKard = '88888888'
    expected.testKwantWrdMetKard[0].waarde = 88888888.0
    expected.testStringFieldMetKard = '88888888'
    expected.testKeuzelijstMetKard = '88888888'

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict({
        'typeURI': AllCasesTestClass.typeURI, 'testIntegerFieldMetKard[]': '88888888',
        'testStringFieldMetKard[]': '88888888', 'testKeuzelijstMetKard[]': '88888888',
        'testKwantWrdMetKard[]': '88888888'}), cast_list=True, model_directory=model_directory_path)

    assert created_instance == expected
    assert len(recwarn) == 0


def test_to_dict_simple_attribute_with_cardinality_convert_lists():
    instance = AllCasesTestClass()
    instance.testIntegerFieldMetKard = [1, 2]
    instance._testKwantWrdMetKard.add_empty_value()
    instance.testKwantWrdMetKard[0].waarde = 1.0
    instance._testKwantWrdMetKard.add_empty_value()
    instance.testKwantWrdMetKard[1].waarde = 2.0
    instance.testKeuzelijstMetKard = ['waarde-1', 'waarde-2']

    assert DotnotationDictConverter.to_dict(instance, cast_list=True, waarde_shortcut=True) == {
        'testIntegerFieldMetKard[]': '1|2',
        'testKwantWrdMetKard[]': '1.0|2.0',
        'testKeuzelijstMetKard[]': 'waarde-1|waarde-2',
        'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_simple_attribute_with_cardinality_convert_lists_clear_values():
    instance = AllCasesTestClass()
    instance._testIntegerFieldMetKard.clear_value()
    instance._testKwantWrdMetKard.add_empty_value()
    instance.testKwantWrdMetKard[0]._waarde.clear_value()
    instance._testKeuzelijstMetKard.clear_value()

    assert DotnotationDictConverter.to_dict(instance, cast_list=True, waarde_shortcut=False) == {
        'testIntegerFieldMetKard[]': '88888888',
        'testKwantWrdMetKard[].waarde': '88888888.0',
        'testKeuzelijstMetKard[]': '88888888',
        'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_simple_attribute_with_cardinality_convert_lists_waarde_shortcut_clear_values():
    instance = AllCasesTestClass()
    instance._testIntegerFieldMetKard.clear_value()
    instance._testKwantWrdMetKard.add_empty_value()
    instance.testKwantWrdMetKard[0]._waarde.clear_value()
    instance._testKeuzelijstMetKard.clear_value()

    assert DotnotationDictConverter.to_dict(instance, cast_list=True, waarde_shortcut=True) == {
        'testIntegerFieldMetKard[]': '88888888',
        'testKwantWrdMetKard[]': '88888888.0',
        'testKeuzelijstMetKard[]': '88888888',
        'typeURI': AllCasesTestClass.typeURI}


def test_from_dict_simple_attributes_waarde_shortcut():
    expected = AllCasesTestClass()
    expected.testEenvoudigType.waarde = 'A.B.C.D'
    expected.testKwantWrd.waarde = 2.0

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testEenvoudigType': 'A.B.C.D', 'testKwantWrd': 2.0}),
        waarde_shortcut=True, model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_simple_attributes_waarde_shortcut_clear_values():
    expected = AllCasesTestClass()
    expected._testEenvoudigType.clear_value()
    expected._testKwantWrd.clear_value()

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testEenvoudigType': '88888888', 'testKwantWrd': 88888888}),
        waarde_shortcut=True, model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_simple_attributes_waarde_shortcut_set_to_false():
    expected = AllCasesTestClass()
    expected.testEenvoudigType.waarde = 'A.B.C.D'
    expected.testKwantWrd.waarde = 2.0

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testEenvoudigType.waarde': 'A.B.C.D', 'testKwantWrd.waarde': 2.0}),
        model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_simple_attributes_waarde_shortcut_set_to_false_clear_values():
    expected = AllCasesTestClass()
    expected._testEenvoudigType.clear_value()
    expected._testKwantWrd.clear_value()

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testEenvoudigType.waarde': '88888888',
         'testKwantWrd.waarde': 88888888}),
        model_directory=model_directory_path)

    assert created_instance == expected


def test_to_dict_simple_attributes_waarde_shortcut():
    instance = AllCasesTestClass()
    instance.testEenvoudigType.waarde = 'A.B.C.D'
    instance.testKwantWrd.waarde = 2.0

    assert DotnotationDictConverter.to_dict(instance) == {'testEenvoudigType': 'A.B.C.D', 'testKwantWrd': 2.0,
                                                          'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_simple_attributes_waarde_shortcut_clear_values():
    instance = AllCasesTestClass()
    instance._testEenvoudigType.clear_value()
    instance._testKwantWrd.clear_value()

    assert DotnotationDictConverter.to_dict(instance) == {'testEenvoudigType': '88888888', 'testKwantWrd': 88888888.0,
                                                          'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_simple_attributes_waarde_shortcut_set_to_false():
    instance = AllCasesTestClass()
    instance.testEenvoudigType.waarde = 'A.B.C.D'
    instance.testKwantWrd.waarde = 2.0

    assert DotnotationDictConverter.to_dict(instance, waarde_shortcut=False) == {
        'testEenvoudigType.waarde': 'A.B.C.D', 'testKwantWrd.waarde': 2.0, 'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_simple_attributes_waarde_shortcut_set_to_false_clear_values():
    instance = AllCasesTestClass()
    instance._testEenvoudigType.clear_value()
    instance._testKwantWrd.clear_value()

    assert DotnotationDictConverter.to_dict(instance, waarde_shortcut=False) == {
        'testEenvoudigType.waarde': '88888888', 'testKwantWrd.waarde': 88888888.0, 'typeURI': AllCasesTestClass.typeURI}


def test_from_dict_complex_attributes():
    expected = AllCasesTestClass()
    expected.testComplexType.testStringField = 'string 1'
    expected.testComplexType.testComplexType2.testStringField = 'string 2'

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testComplexType.testStringField': 'string 1',
         'testComplexType.testComplexType2.testStringField': 'string 2'}),
        model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_complex_attributes_clear_values():
    expected = AllCasesTestClass()
    expected.testComplexType._testStringField.clear_value()
    expected.testComplexType.testComplexType2._testStringField.clear_value()

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testComplexType.testStringField': '88888888',
         'testComplexType.testComplexType2.testStringField': '88888888'}),
        model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_complex_attributes_with_kwant_wrd():
    expected = AllCasesTestClass()
    expected.testUnionType.unionKwantWrd.waarde = 2.0

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testUnionType.unionKwantWrd': 2.0}),
        waarde_shortcut=True, model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_complex_attributes_with_kwant_wrd_clear_values():
    expected = AllCasesTestClass()
    expected.testUnionType.unionKwantWrd.waarde = 88888888.0

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testUnionType.unionKwantWrd': 88888888.0}),
        waarde_shortcut=True, model_directory=model_directory_path)

    assert created_instance == expected


def test_to_dict_complex_attributes():
    instance = AllCasesTestClass()
    instance.testComplexType.testStringField = 'string 1'
    instance.testComplexType.testComplexType2.testStringField = 'string 2'
    instance.testUnionType.unionKwantWrd.waarde = 2.0

    assert DotnotationDictConverter.to_dict(instance) == {
        'testComplexType.testComplexType2.testStringField': 'string 2',
        'testComplexType.testStringField': 'string 1',
        'testUnionType.unionKwantWrd': 2.0,
        'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_complex_attributes_clear_values():
    instance = AllCasesTestClass()
    instance.testComplexType._testStringField.clear_value()
    instance.testComplexType.testComplexType2._testStringField.clear_value()
    instance.testUnionType.unionKwantWrd._waarde.clear_value()

    assert DotnotationDictConverter.to_dict(instance) == {
        'testComplexType.testComplexType2.testStringField': '88888888',
        'testComplexType.testStringField': '88888888',
        'testUnionType.unionKwantWrd': 88888888.0,
        'typeURI': AllCasesTestClass.typeURI}


def test_from_dict_complex_attributes_with_cardinality():
    expected = AllCasesTestClass()
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[0].testStringField = 'e'
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[1].testStringField = 'f'
    expected.testComplexType.testStringFieldMetKard = ['c', 'd']

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testComplexTypeMetKard[].testStringField': 'e|f',
         'testComplexType.testStringFieldMetKard[]': 'c|d'}), cast_list=True,
        model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_complex_attributes_with_cardinality_clear_values():
    expected = AllCasesTestClass()
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[0]._testStringField.clear_value()
    expected.testComplexType._testStringFieldMetKard.clear_value()

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI,
         'testComplexTypeMetKard[].testStringField': '88888888',
         'testComplexType.testStringFieldMetKard[]': '88888888'}),
        cast_list=True, model_directory=model_directory_path)

    assert created_instance == expected


def test_to_dict_with_cardinality():
    instance = AllCasesTestClass()
    instance.testStringFieldMetKard = ['a', 'b']
    instance.testComplexType.testStringFieldMetKard = ['c', 'd']
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[0].testStringField = 'e'
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[1].testStringField = 'f'

    assert DotnotationDictConverter.to_dict(instance) == {
        'testComplexTypeMetKard[].testStringField': ['e', 'f'],
        'testComplexType.testStringFieldMetKard[]': ['c', 'd'],
        'testStringFieldMetKard[]': ['a', 'b'],
        'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_with_cardinality_clear_values():
    instance = AllCasesTestClass()
    instance._testStringFieldMetKard.clear_value()
    instance.testComplexType._testStringFieldMetKard.clear_value()
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[0]._testStringField.clear_value()
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[1]._testStringField.clear_value()

    assert DotnotationDictConverter.to_dict(instance, cast_list=True) == {
        'testComplexTypeMetKard[].testStringField': '88888888|88888888',
        'testComplexType.testStringFieldMetKard[]': '88888888',
        'testStringFieldMetKard[]': '88888888',
        'typeURI': AllCasesTestClass.typeURI}


def test_from_dict_with_different_cardinality():
    expected = AllCasesTestClass()
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[0].testBooleanField = False
    expected.testComplexTypeMetKard[0].testStringField = '1.1'
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[1].testBooleanField = True
    expected.testComplexTypeMetKard[1].testKwantWrd.waarde = 2.0
    expected.testComplexTypeMetKard[1].testStringField = '1.2'
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[2].testStringField = '1.3'

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict({
        'typeURI': AllCasesTestClass.typeURI,
        'testComplexTypeMetKard[].testBooleanField': [False, True, None],
        'testComplexTypeMetKard[].testStringField': ['1.1', '1.2', '1.3'],
        'testComplexTypeMetKard[].testKwantWrd': [None, 2.0, None]}), model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_with_different_cardinality_clear_values():
    expected = AllCasesTestClass()
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[0]._testBooleanField.clear_value()
    expected.testComplexTypeMetKard[0].testStringField = '1.1'
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[1].testBooleanField = True
    expected.testComplexTypeMetKard[1].testKwantWrd._waarde.clear_value()
    expected.testComplexTypeMetKard[1].testStringField = '1.2'
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[2]._testStringField.clear_value()

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict({
        'typeURI': AllCasesTestClass.typeURI,
        'testComplexTypeMetKard[].testBooleanField': ['88888888', True, None],
        'testComplexTypeMetKard[].testStringField': ['1.1', '1.2', '88888888'],
        'testComplexTypeMetKard[].testKwantWrd': [None, 88888888.0, None]}), model_directory=model_directory_path)

    assert created_instance == expected


def test_to_dict_with_different_cardinality():
    instance = AllCasesTestClass()

    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[0].testBooleanField = False
    instance.testComplexTypeMetKard[0].testStringField = '1.1'
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[1].testBooleanField = True
    instance.testComplexTypeMetKard[1].testKwantWrd.waarde = 2.0
    instance.testComplexTypeMetKard[1].testStringField = '1.2'
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[2].testStringField = '1.3'

    assert DotnotationDictConverter.to_dict(instance) == {
        'testComplexTypeMetKard[].testBooleanField': [False, True, None],
        'testComplexTypeMetKard[].testStringField': ['1.1', '1.2', '1.3'],
        'testComplexTypeMetKard[].testKwantWrd': [None, 2.0, None],
        'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_with_different_cardinality_clear_values():
    instance = AllCasesTestClass()

    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[0]._testBooleanField.clear_value()
    instance.testComplexTypeMetKard[0].testStringField = '1.1'
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[1].testBooleanField = True
    instance.testComplexTypeMetKard[1].testKwantWrd._waarde.clear_value()
    instance.testComplexTypeMetKard[1].testStringField = '1.2'
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[2]._testStringField.clear_value()

    assert DotnotationDictConverter.to_dict(instance) == {
        'typeURI': AllCasesTestClass.typeURI,
        'testComplexTypeMetKard[].testBooleanField': ['88888888', True, None],
        'testComplexTypeMetKard[].testStringField': ['1.1', '1.2', '88888888'],
        'testComplexTypeMetKard[].testKwantWrd': [None, 88888888.0, None]}


def test_from_dict_complex_attributes_with_cardinality_and_kwant_wrd():
    expected = AllCasesTestClass()
    expected.testComplexType._testKwantWrdMetKard.add_empty_value()
    expected.testComplexType._testKwantWrdMetKard.add_empty_value()
    expected.testComplexType.testKwantWrdMetKard[0].waarde = 3.0
    expected.testComplexType.testKwantWrdMetKard[1].waarde = 4.0
    expected.testComplexType.testComplexType2.testKwantWrd.waarde = 5.0
    expected.testUnionType.unionKwantWrd.waarde = 2.0

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testComplexType.testKwantWrdMetKard[]': [3.0, 4.0],
         'testComplexType.testComplexType2.testKwantWrd': 5.0, 'testUnionType.unionKwantWrd': 2.0}),
        model_directory=model_directory_path, waarde_shortcut=True)

    assert created_instance == expected


def test_from_dict_complex_attributes_with_cardinality_and_kwant_wrd_clear_values():
    expected = AllCasesTestClass()
    expected.testComplexType._testKwantWrdMetKard.add_empty_value()
    expected.testComplexType._testKwantWrdMetKard.add_empty_value()
    expected.testComplexType.testKwantWrdMetKard[0]._waarde.clear_value()
    expected.testComplexType.testKwantWrdMetKard[1]._waarde.clear_value()
    expected.testComplexType.testComplexType2.testKwantWrd._waarde.clear_value()
    expected.testUnionType.unionKwantWrd._waarde.clear_value()

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testComplexType.testKwantWrdMetKard[]': [88888888.0, 88888888.0],
         'testComplexType.testComplexType2.testKwantWrd': 88888888.0, 'testUnionType.unionKwantWrd': 88888888.0}),
        model_directory=model_directory_path, waarde_shortcut=True)

    assert created_instance == expected


def test_to_dict_complex_attributes_with_cardinality_and_kwant_wrd_cast_list_False():
    instance = AllCasesTestClass()
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType.testKwantWrdMetKard[0]._waarde.clear_value()
    instance.testComplexType.testKwantWrdMetKard[1]._waarde.clear_value()
    instance.testComplexType.testComplexType2.testKwantWrd._waarde.clear_value()
    instance.testUnionType.unionKwantWrd._waarde.clear_value()

    assert DotnotationDictConverter.to_dict(instance, waarde_shortcut=True) == {
        'testComplexType.testComplexType2.testKwantWrd': 88888888.0,
        'testComplexType.testKwantWrdMetKard[]': [88888888.0, 88888888.0],
        'testUnionType.unionKwantWrd': 88888888.0,
        'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_complex_attributes_with_cardinality_and_kwant_wrd_cast_list_True():
    instance = AllCasesTestClass()
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType.testKwantWrdMetKard[0]._waarde.clear_value()
    instance.testComplexType.testKwantWrdMetKard[1]._waarde.clear_value()
    instance.testComplexType.testComplexType2.testKwantWrd._waarde.clear_value()
    instance.testUnionType.unionKwantWrd._waarde.clear_value()

    assert DotnotationDictConverter.to_dict(instance, cast_list=True) == {
        'testComplexType.testComplexType2.testKwantWrd': 88888888.0,
        'testComplexType.testKwantWrdMetKard[]': '88888888.0|88888888.0',
        'testUnionType.unionKwantWrd': 88888888.0,
        'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_errors(subtests):
    instance = AllCasesTestClass()
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[0].testStringFieldMetKard = ['test']
    with subtests.test("error raised when using list of lists"):
        with pytest.raises(DotnotationListOfListError):
            DotnotationDictConverter.to_dict(instance)


def test_from_dict_errors(subtests):
    with subtests.test("error raised when using dict without typeURI"):
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(DotnotationDict(
                {'complex.attribute': 'complex attributes only valid within OTL'}),
                model_directory=model_directory_path)

    with subtests.test("error raised when using dict with invalid typeURI"):
        with pytest.raises(CouldNotCreateInstanceError):
            DotnotationDictConverter.from_dict(DotnotationDict(
                {'complex.attribute': 'complex attributes only valid within OTL', 'typeURI': 'not_valid_uri'}),
                model_directory=model_directory_path)

    with subtests.test("error raised when a key starts with '_'"):
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(DotnotationDict(
                {'typeURI': AllCasesTestClass.typeURI, '_invalid_attribute_key': '_ is not a valid first char'}),
                model_directory=model_directory_path)

        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(DotnotationDict(
                {'typeURI': AllCasesTestClass.typeURI,
                 'complex._invalid_attribute_key': '_ is not a valid first char'}),
                model_directory=model_directory_path)

    with subtests.test("error raised when trying dotnotation with 2 x cardinality indicator"):
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(DotnotationDict(
                {'typeURI': AllCasesTestClass.typeURI, 'complex[].attribute[]': 'lists of lists are not valid'}),
                model_directory=model_directory_path)

    with subtests.test("error raised when trying dotnotation with a complex non-conform attribute"):
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(DotnotationDict(
                {'typeURI': AllCasesTestClass.typeURI,
                 'complex.attribute': 'complex attributes only valid within OTL'}),
                model_directory=model_directory_path)


def test_from_dict_instance_version():
    converter = DotnotationDictConverter(
        separator='+', waarde_shortcut=False, cardinality_indicator='()', cardinality_separator='*')
    expected = AllCasesTestClass()
    expected.testKeuzelijst = 'waarde-2'
    expected.testBooleanField = True
    expected.testComplexTypeMetKard[0].testKwantWrd.waarde = 10.0
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[1].testKwantWrd.waarde = 20.0

    created_instance = converter.from_dict_instance(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testBooleanField': True, 'testKeuzelijst': 'waarde-2',
         'testComplexTypeMetKard()+testKwantWrd+waarde': '10.0*20.0'}),
        model_directory=model_directory_path, cast_list=True)

    assert created_instance == expected


def test_to_dict_instance_version():
    converter = DotnotationDictConverter(
        separator='+', waarde_shortcut=False, cardinality_indicator='()', cardinality_separator='*')

    expected_dict = DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI, 'testBooleanField': True, 'testKeuzelijst': 'waarde-2',
         'testComplexTypeMetKard()+testKwantWrd+waarde': '10.0*20.0'})

    instance = AllCasesTestClass()
    instance.testKeuzelijst = 'waarde-2'
    instance.testBooleanField = True
    instance.testComplexTypeMetKard[0].testKwantWrd.waarde = 10.0
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[1].testKwantWrd.waarde = 20.0

    created_dict = converter.to_dict_instance(instance, cast_list=True)

    assert created_dict == expected_dict