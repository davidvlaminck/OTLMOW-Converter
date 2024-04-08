from datetime import date, time, datetime
from pathlib import Path

import pytest
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
        {'typeURI' : AllCasesTestClass.typeURI, 'testBooleanField': True, 'testKeuzelijst': 'waarde-2'}),
        model_directory=model_directory_path)

    assert created_instance == expected

def test_to_dict_simple_attributes():
    instance = AllCasesTestClass()
    instance.testKeuzelijst = 'waarde-2'
    instance.testBooleanField = True

    assert DotnotationDictConverter.to_dict(instance) == {'testBooleanField': True, 'testKeuzelijst': 'waarde-2',
        'typeURI': AllCasesTestClass.typeURI}


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
        {'typeURI' : AllCasesTestClass.typeURI,
         'testComplexTypeMetKard[].testBooleanField': 'True|False',
         'testComplexType.testKwantWrdMetKard[]': '3.0|4.0',
         'testDecimalFieldMetKard[]': '1.0|2.0'
         }),
        model_directory=model_directory_path, cast_list=True, waarde_shortcut=True)

    assert created_instance == expected
    assert len(recwarn) == 0


def test_from_dict_datetimes_convert_true(recwarn):
    expected = AllCasesTestClass()
    expected.testDateField = date(2022, 12, 12)
    expected.testTimeField = time(10, 11, 12)
    expected.testDateTimeField = datetime(2022, 12, 12, 10, 11, 12)

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI' : AllCasesTestClass.typeURI, 'testDateField': '2022-12-12', 'testTimeField': '10:11:12',
            'testDateTimeField': '2022-12-12 10:11:12'}),
        model_directory=model_directory_path, cast_datetime=True)

    assert created_instance == expected
    assert len(recwarn) == 0

def test_from_dict_datetimes_convert_false(recwarn):
    expected = AllCasesTestClass()
    expected.testDateField = date(2022, 12, 12)
    expected.testTimeField = time(10, 11, 12)
    expected.testDateTimeField = datetime(2022, 12, 12, 10, 11, 12)

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI': AllCasesTestClass.typeURI,
         'testDateField': date(2022, 12, 12),
         'testTimeField': time(10, 11, 12),
         'testDateTimeField': datetime(2022, 12, 12, 10, 11, 12)}),
        model_directory=model_directory_path)

    assert created_instance == expected
    assert len(recwarn) == 0


def test_to_dict_datetimes():
    instance = AllCasesTestClass()
    instance.testDateField = date(2022, 12, 12)
    instance.testTimeField = time(10, 11, 12)
    instance.testDateTimeField = datetime(2022, 12, 12, 10, 11, 12)

    assert DotnotationDictConverter.to_dict(instance) == {
        'testDateField': date(2022, 12, 12),
        'testTimeField': time(10, 11, 12),
        'testDateTimeField': datetime(2022, 12, 12, 10, 11, 12),
        'typeURI': AllCasesTestClass.typeURI}

    assert DotnotationDictConverter.to_dict(instance, cast_datetime=True) == {
        'testDateField': '2022-12-12',
        'testTimeField': '10:11:12',
        'testDateTimeField': '2022-12-12 10:11:12',
        'typeURI': AllCasesTestClass.typeURI}


def test_from_dict_with_non_conform_otl_attributes(subtests, recwarn):
    expected = AllCasesTestClass()
    expected.non_conform_attribute = 'non-conform'
    expected.testBooleanField = True

    input_dict = DotnotationDict({'typeURI' : AllCasesTestClass.typeURI, 'testBooleanField': True,
                                  'non_conform_attribute': 'non-conform'})

    with subtests.test('Test with warn_for_non_otl_conform_attributes set to False'):
        created_instance = DotnotationDictConverter.from_dict(input_dict, model_directory=model_directory_path,
            warn_for_non_otl_conform_attributes=False)

        assert created_instance == expected
        assert len(recwarn) == 0

    with subtests.test('Test with allow_non_otl_conform_attributes set to True'):
        with pytest.warns(NonStandardAttributeWarning):
            created_instance = DotnotationDictConverter.from_dict(input_dict, model_directory=model_directory_path)

            assert created_instance == expected

    with subtests.test('Test with allow_non_otl_conform_attributes set to False'):
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(input_dict,
                model_directory=model_directory_path, allow_non_otl_conform_attributes=False)

    with subtests.test('Test with allow_non_otl_conform_attributes with bad key'):
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(
                DotnotationDict({'typeURI' : AllCasesTestClass.typeURI, 'testBooleanField': True,
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

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict({
        'typeURI' : AllCasesTestClass.typeURI, 'testIntegerFieldMetKard[]': [1, 2, 3],
        'testStringFieldMetKard[]': ['a', 'b', 'c']
    }), model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_simple_attribute_with_cardinality_converted_lists(recwarn):
    expected = AllCasesTestClass()
    expected.testIntegerFieldMetKard = [1, 2]
    expected.testStringFieldMetKard = ['a', 'b']

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict({
        'typeURI' : AllCasesTestClass.typeURI, 'testIntegerFieldMetKard[]': '1|2',
        'testStringFieldMetKard[]': 'a|b'}), cast_list=True, model_directory=model_directory_path)

    assert created_instance == expected
    assert len(recwarn) == 0


def test_to_dict_simple_attribute_with_cardinality():
    instance = AllCasesTestClass()
    instance.testIntegerFieldMetKard = [1, 2, 3]
    instance.testStringFieldMetKard = ['a', 'b', 'c']

    assert DotnotationDictConverter.to_dict(instance) == {
        'testIntegerFieldMetKard[]': [1, 2, 3],
        'testStringFieldMetKard[]': ['a', 'b', 'c'],
        'typeURI': AllCasesTestClass.typeURI}


def test_from_dict_simple_attribute_with_cardinality_convert_lists(recwarn):
    expected = AllCasesTestClass()
    expected.testIntegerFieldMetKard = [1, 2]
    expected._testKwantWrdMetKard.add_empty_value()
    expected.testKwantWrdMetKard[0].waarde = 1.0
    expected._testKwantWrdMetKard.add_empty_value()
    expected.testKwantWrdMetKard[1].waarde = 2.0

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict({
        'typeURI' : AllCasesTestClass.typeURI, 'testIntegerFieldMetKard[]': '1|2',
        'testKwantWrdMetKard[]': '1.0|2.0'}), cast_list=True, model_directory=model_directory_path)

    assert created_instance == expected
    assert len(recwarn) == 0


def test_to_dict_simple_attribute_with_cardinality_convert_lists():
    instance = AllCasesTestClass()
    instance.testIntegerFieldMetKard = [1, 2]
    instance._testKwantWrdMetKard.add_empty_value()
    instance.testKwantWrdMetKard[0].waarde = 1.0
    instance._testKwantWrdMetKard.add_empty_value()
    instance.testKwantWrdMetKard[1].waarde = 2.0

    assert DotnotationDictConverter.to_dict(instance, cast_list=True, waarde_shortcut=True) == {
        'testIntegerFieldMetKard[]': '1|2',
        'testKwantWrdMetKard[]': '1.0|2.0',
        'typeURI': AllCasesTestClass.typeURI}


def test_from_dict_simple_attributes_waarde_shortcut():
    expected = AllCasesTestClass()
    expected.testEenvoudigType.waarde = 'A.B.C.D'
    expected.testKwantWrd.waarde = 2.0

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI' : AllCasesTestClass.typeURI, 'testEenvoudigType': 'A.B.C.D', 'testKwantWrd': 2.0}),
        waarde_shortcut=True, model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_simple_attributes_waarde_shortcut_set_to_false():
    expected = AllCasesTestClass()
    expected.testEenvoudigType.waarde = 'A.B.C.D'
    expected.testKwantWrd.waarde = 2.0

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI' : AllCasesTestClass.typeURI, 'testEenvoudigType.waarde': 'A.B.C.D', 'testKwantWrd.waarde': 2.0}),
        model_directory=model_directory_path)

    assert created_instance == expected


def test_to_dict_simple_attributes_waarde_shortcut():
    instance = AllCasesTestClass()
    instance.testEenvoudigType.waarde = 'A.B.C.D'
    instance.testKwantWrd.waarde = 2.0

    assert DotnotationDictConverter.to_dict(instance) == {'testEenvoudigType': 'A.B.C.D', 'testKwantWrd': 2.0,
        'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_simple_attributes_waarde_shortcut_set_to_false():
    instance = AllCasesTestClass()
    instance.testEenvoudigType.waarde = 'A.B.C.D'
    instance.testKwantWrd.waarde = 2.0

    assert DotnotationDictConverter.to_dict(instance, waarde_shortcut=False) == {
        'testEenvoudigType.waarde': 'A.B.C.D', 'testKwantWrd.waarde': 2.0, 'typeURI': AllCasesTestClass.typeURI}


def test_from_dict_complex_attributes():
    expected = AllCasesTestClass()
    expected.testComplexType.testStringField = 'string 1'
    expected.testComplexType.testComplexType2.testStringField = 'string 2'

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI' : AllCasesTestClass.typeURI, 'testComplexType.testStringField': 'string 1',
         'testComplexType.testComplexType2.testStringField': 'string 2'}),
        model_directory=model_directory_path)

    assert created_instance == expected


def test_from_dict_complex_attributes_with_kwant_wrd():
    expected = AllCasesTestClass()
    expected.testUnionType.unionKwantWrd.waarde = 2.0

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI' : AllCasesTestClass.typeURI, 'testUnionType.unionKwantWrd': 2.0}),
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


def test_from_dict_complex_attributes_with_cardinality():
    expected = AllCasesTestClass()
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[0].testStringField = 'e'
    expected._testComplexTypeMetKard.add_empty_value()
    expected.testComplexTypeMetKard[1].testStringField = 'f'
    expected.testComplexType.testStringFieldMetKard = ['c', 'd']

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI' : AllCasesTestClass.typeURI, 'testComplexTypeMetKard[].testStringField': 'e|f',
         'testComplexType.testStringFieldMetKard[]': 'c|d'}), cast_list=True,
        model_directory=model_directory_path)

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
        'typeURI' : AllCasesTestClass.typeURI,
        'testComplexTypeMetKard[].testBooleanField': [False, True, None],
        'testComplexTypeMetKard[].testStringField': ['1.1', '1.2', '1.3'],
        'testComplexTypeMetKard[].testKwantWrd': [None, 2.0, None]}), model_directory=model_directory_path)

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


def test_from_dict_complex_attributes_with_cardinality_and_kwant_wrd():
    expected = AllCasesTestClass()
    expected.testComplexType._testKwantWrdMetKard.add_empty_value()
    expected.testComplexType._testKwantWrdMetKard.add_empty_value()
    expected.testComplexType.testKwantWrdMetKard[0].waarde = 3.0
    expected.testComplexType.testKwantWrdMetKard[1].waarde = 4.0
    expected.testComplexType.testComplexType2.testKwantWrd.waarde = 5.0
    expected.testUnionType.unionKwantWrd.waarde = 2.0

    created_instance = DotnotationDictConverter.from_dict(DotnotationDict(
        {'typeURI' : AllCasesTestClass.typeURI, 'testComplexType.testKwantWrdMetKard[]': [3.0, 4.0],
            'testComplexType.testComplexType2.testKwantWrd': 5.0, 'testUnionType.unionKwantWrd': 2.0}),
        model_directory=model_directory_path, waarde_shortcut=True)

    assert created_instance == expected



def test_to_dict_complex_attributes_with_cardinality_and_kwant_wrd_cast_list_False():
    instance = AllCasesTestClass()
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType.testKwantWrdMetKard[0].waarde = 3.0
    instance.testComplexType.testKwantWrdMetKard[1].waarde = 4.0
    instance.testComplexType.testComplexType2.testKwantWrd.waarde = 5.0
    instance.testUnionType.unionKwantWrd.waarde = 2.0

    assert DotnotationDictConverter.to_dict(instance) == {
        'testComplexType.testComplexType2.testKwantWrd': 5.0,
        'testComplexType.testKwantWrdMetKard[]': [3.0, 4.0],
        'testUnionType.unionKwantWrd': 2.0,
        'typeURI': AllCasesTestClass.typeURI}


def test_to_dict_complex_attributes_with_cardinality_and_kwant_wrd_cast_list_True():
    instance = AllCasesTestClass()
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType.testKwantWrdMetKard[0].waarde = 3.0
    instance.testComplexType.testKwantWrdMetKard[1].waarde = 4.0
    instance.testComplexType.testComplexType2.testKwantWrd.waarde = 5.0
    instance.testUnionType.unionKwantWrd.waarde = 2.0

    assert DotnotationDictConverter.to_dict(instance, cast_list=True) == {
        'testComplexType.testComplexType2.testKwantWrd': 5.0,
        'testComplexType.testKwantWrdMetKard[]': '3.0|4.0',
        'testUnionType.unionKwantWrd': 2.0,
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
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(DotnotationDict(
                {'complex.attribute': 'complex attributes only valid within OTL', 'typeURI': 'not_valid_uri'}),
                model_directory=model_directory_path)


    with subtests.test("error raised when a key starts with '_'"):
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(DotnotationDict(
                {'typeURI' : AllCasesTestClass.typeURI, '_invalid_attribute_key': '_ is not a valid first char'}),
                model_directory=model_directory_path)

        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(DotnotationDict(
                {'typeURI': AllCasesTestClass.typeURI, 'complex._invalid_attribute_key': '_ is not a valid first char'}),
                model_directory=model_directory_path)

    with subtests.test("error raised when trying dotnotation with 2 x cardinality indicator"):
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(DotnotationDict(
                {'typeURI': AllCasesTestClass.typeURI, 'complex[].attribute[]': 'lists of lists are not valid'}),
                model_directory=model_directory_path)

    with subtests.test("error raised when trying dotnotation with a complex non-conform attribute"):
        with pytest.raises(ValueError):
            DotnotationDictConverter.from_dict(DotnotationDict(
                {'typeURI': AllCasesTestClass.typeURI, 'complex.attribute': 'complex attributes only valid within OTL'}),
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
        {'typeURI' : AllCasesTestClass.typeURI, 'testBooleanField': True, 'testKeuzelijst': 'waarde-2',
         'testComplexTypeMetKard()+testKwantWrd+waarde': '10.0*20.0'}),
        model_directory=model_directory_path, cast_list=True)

    assert created_instance == expected


def test_to_dict_instance_version():
    converter = DotnotationDictConverter(
        separator='+', waarde_shortcut=False, cardinality_indicator='()', cardinality_separator='*')

    expected_dict = DotnotationDict(
        {'typeURI' : AllCasesTestClass.typeURI, 'testBooleanField': True, 'testKeuzelijst': 'waarde-2',
         'testComplexTypeMetKard()+testKwantWrd+waarde': '10.0*20.0'})

    instance = AllCasesTestClass()
    instance.testKeuzelijst = 'waarde-2'
    instance.testBooleanField = True
    instance.testComplexTypeMetKard[0].testKwantWrd.waarde = 10.0
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[1].testKwantWrd.waarde = 20.0

    created_dict = converter.to_dict_instance(instance, cast_list=True)

    assert created_dict == expected_dict

