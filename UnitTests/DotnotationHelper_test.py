import json
import logging
import unittest

import pytest

from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.DotnotationHelper import DotnotationHelper


class JsonLdTestData:
    simple = '{ "a": "value a", "b": "value b" }'
    dict_in_dict = '{ "a": "value a", "b": { "c": "value c", "d": "value d" } }'
    list = '{ "a": [1,2] }'
    listdict_in_dict = '{ "a": "value a", "b": [{ "c": "value c", "d": "value d" }, { "e": "value e", "f": "value f" }]}'


def test_flatten_dict_simple():
    input_dict = json.loads(JsonLdTestData.simple)

    output = DotnotationHelper().flatten_dict(input_dict=input_dict)
    expected = {"a": "value a", "b": "value b"}
    assert output == expected


def test_flatten_dict_dict_in_dict():
    input_dict = json.loads(JsonLdTestData.dict_in_dict)

    output = DotnotationHelper().flatten_dict(input_dict)
    expected = {"a": "value a", "b.c": "value c", "b.d": "value d"}
    assert output == expected


def test_flatten_dict_list():
    input_dict = json.loads(JsonLdTestData.list)

    output = DotnotationHelper().flatten_dict(input_dict=input_dict)
    expected = {"a[0]": 1, "a[1]": 2}
    assert output == expected


def test_flatten_dict_listdict_in_dict():
    input_dict = json.loads(JsonLdTestData.listdict_in_dict)

    output = DotnotationHelper().flatten_dict(input_dict=input_dict)
    expected = {"a": "value a", "b[0].c": "value c", "b[0].d": "value d", "b[1].e": "value e", "b[1].f": "value f"}
    assert output == expected


def test_list_attributes_and_values_by_dotnotation_simple_attributes():
    instance = AllCasesTestClass()
    instance.testKeuzelijst = 'waarde-2'
    instance.testBooleanField = True
    attribute_list = list(DotnotationHelper.list_attributes_and_values_by_dotnotation(instance))
    expected_list = [('testBooleanField', True),
                     ('testKeuzelijst', 'waarde-2')]
    assert attribute_list == expected_list


def test_list_attributes_and_values_by_dotnotation_complex_attributes():
    instance = AllCasesTestClass()
    instance.testComplexType.testStringField = 'string 1'
    instance.testComplexType.testComplexType2.testStringField = 'string 2'
    instance.testUnionType.unionKwantWrd.waarde = 2.0
    attribute_list = list(DotnotationHelper.list_attributes_and_values_by_dotnotation(instance))
    expected_list = [('testComplexType.testComplexType2.testStringField', 'string 2'),
                     ('testComplexType.testStringField', 'string 1'),
                     ('testUnionType.unionKwantWrd.waarde', 2.0)]
    assert attribute_list == expected_list


def test_list_attributes_and_values_by_dotnotation_attributes_with_cardinality():
    instance = AllCasesTestClass()
    instance.testStringFieldMetKard = ['a', 'b']
    instance.testComplexType.testStringFieldMetKard = ['c', 'd']
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[0].testStringField = 'e'
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[1].testStringField = 'f'
    attribute_list = list(DotnotationHelper.list_attributes_and_values_by_dotnotation(instance))
    expected_list = [('testComplexType.testStringFieldMetKard[]', ['c', 'd']),
                     ('testComplexTypeMetKard[].testStringField', ['e', 'f']),
                     ('testStringFieldMetKard[]', ['a', 'b'])]
    assert attribute_list == expected_list


def test_list_attributes_and_values_by_dotnotation_attributes_with_different_cardinality():
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

    attribute_list = list(DotnotationHelper.list_attributes_and_values_by_dotnotation(instance))
    expected_list = [('testComplexTypeMetKard[].testBooleanField', [False, True, None]),
                     ('testComplexTypeMetKard[].testStringField', ['1.1', '1.2', '1.3']),
                     ('testComplexTypeMetKard[].testKwantWrd.waarde', [None, 2.0, None])]
    assert attribute_list == expected_list


def test_list_attributes_and_values_by_dotnotation_waarde_shortcut():
    instance = AllCasesTestClass()
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType.testKwantWrdMetKard[0].waarde = 3.0
    instance.testComplexType.testKwantWrdMetKard[1].waarde = 4.0
    instance.testComplexType.testComplexType2.testKwantWrd.waarde = 5.0
    instance.testUnionType.unionKwantWrd.waarde = 2.0
    attribute_list = list(DotnotationHelper.list_attributes_and_values_by_dotnotation(instance,
                                                                                      waarde_shortcut=True))
    expected_list = [('testComplexType.testComplexType2.testKwantWrd', 5.0),
                     ('testComplexType.testKwantWrdMetKard[]', [3.0, 4.0]),
                     ('testUnionType.unionKwantWrd', 2.0)]
    assert attribute_list == expected_list


def test_get_dotnotation_default_values_waarde_shortcut(subtests):
    instance = AllCasesTestClass()
    with subtests.test(msg='attribute 2 levels deep with waarde shortcut enabled'):
        dotnotation = DotnotationHelper().get_dotnotation(instance.testKwantWrd._waarde,
                                                          waarde_shortcut=True)
        assert dotnotation == 'testKwantWrd'

    with subtests.test(msg='attribute 2 levels deep with waarde shortcut enabled and cardinality > 1'):
        dotnotation = DotnotationHelper().get_dotnotation(instance.testKwantWrdMetKard[0]._waarde,
                                                          waarde_shortcut=True)
        assert dotnotation == 'testKwantWrdMetKard[]'

    with subtests.test(msg='attribute 4 levels deep with waarde shortcut disabled'):
        dotnotation = DotnotationHelper().get_dotnotation(
            instance.testComplexType.testComplexType2.testKwantWrd._waarde,
            waarde_shortcut=True)
        assert dotnotation == 'testComplexType.testComplexType2.testKwantWrd'


def test_get_dotnotation_default_values(subtests):
    instance = AllCasesTestClass()
    with subtests.test(msg='attribute 1 level deep'):
        dotnotation = DotnotationHelper().get_dotnotation(instance._testDecimalField)
        assert dotnotation == 'testDecimalField'

    with subtests.test(msg='attribute 1 level deep with cardinality > 1'):
        dotnotation = DotnotationHelper().get_dotnotation(instance._testStringFieldMetKard)
        assert dotnotation == 'testStringFieldMetKard[]'

    with subtests.test(msg='attribute 2 levels deep with waarde shortcut disabled'):
        dotnotation = DotnotationHelper().get_dotnotation(instance.testKwantWrd._waarde, waarde_shortcut=False)
        assert dotnotation == 'testKwantWrd.waarde'

    with subtests.test(msg='attribute 2 levels deep'):
        dotnotation = DotnotationHelper().get_dotnotation(instance.testComplexType._testStringField)
        assert dotnotation == 'testComplexType.testStringField'

    with subtests.test(msg='attribute 2 levels deep with cardinality > 1'):
        dotnotation = DotnotationHelper().get_dotnotation(instance.testComplexTypeMetKard[0]._testStringFieldMetKard)
        assert dotnotation == 'testComplexTypeMetKard[].testStringFieldMetKard[]'

    with subtests.test(msg='attribute 3 levels deep'):
        dotnotation = DotnotationHelper().get_dotnotation(instance.testComplexType.testComplexType2._testStringField)
        assert dotnotation == 'testComplexType.testComplexType2.testStringField'

    with subtests.test(msg='attribute 3 levels deep with cardinality > 1'):
        dotnotation = DotnotationHelper().get_dotnotation(instance.testComplexTypeMetKard[0].testComplexType2MetKard[0]._testStringField)
        assert dotnotation == 'testComplexTypeMetKard[].testComplexType2MetKard[].testStringField'

    with subtests.test(msg='attribute 4 levels deep with waarde shortcut disabled'):
        dotnotation = DotnotationHelper().get_dotnotation(instance.testComplexType.testComplexType2.testKwantWrd._waarde,
                                                          waarde_shortcut=False)
        assert dotnotation == 'testComplexType.testComplexType2.testKwantWrd.waarde'


def test_get_attribute_by_dotnotation_default_values(subtests):
    instance = AllCasesTestClass()

    with subtests.test(msg="attribute 1 level deep"):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(instance, 'testDecimalField')
        expected_attribute = instance._testDecimalField
        assert result_attribute == expected_attribute

    with subtests.test(msg='attribute 1 level deep with cardinality > 1'):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(instance, 'testStringFieldMetKard[]')
        expected_attribute = instance._testStringFieldMetKard
        assert result_attribute == expected_attribute

    with subtests.test(msg='attribute 2 levels deep with waarde shortcut disabled'):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(instance, 'testKwantWrd.waarde',
                                                                          waarde_shortcut=False)
        expected_attribute = instance.testKwantWrd._waarde
        assert result_attribute == expected_attribute

    with subtests.test(msg='attribute 2 levels deep with waarde shortcut disabled'):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(instance, 'testKwantWrd')
        expected_attribute = instance.testKwantWrd._waarde
        assert result_attribute == expected_attribute

    with subtests.test(msg='attribute 2 levels deep'):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(instance,
                                                                           'testComplexType.testStringField')
        expected_attribute = instance.testComplexType._testStringField
        assert result_attribute == expected_attribute

    with subtests.test(msg='attribute 2 levels deep with cardinality > 1'):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(instance,
                                                                           'testComplexTypeMetKard[].testStringField')
        assert result_attribute == instance.testComplexTypeMetKard[0]._testStringField

    with subtests.test(msg='attribute with multiple cardinality'):
        with pytest.raises(ValueError):
            result_attribute = DotnotationHelper.get_attribute_by_dotnotation(
                instance, 'testComplexTypeMetKard[].testComplexType2MetKard[].testStringField')

    with subtests.test(msg='attribute 3 levels deep with cardinality > 1'):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(
            instance, 'testComplexTypeMetKard[].testComplexType2.testStringField')
        expected_attribute = instance.testComplexTypeMetKard[0].testComplexType2._testStringField
        assert result_attribute == expected_attribute

    with subtests.test(msg='attribute 3 levels deep with cardinality > 1'):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(
            instance, 'testComplexTypeMetKard[].testComplexType2.testStringField')
        assert result_attribute == instance.testComplexTypeMetKard[0].testComplexType2._testStringField

    with subtests.test(msg='attribute 4 levels deep with waarde shortcut disabled'):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(
            instance, 'testComplexType.testComplexType2.testKwantWrd.waarde')
        expected_attribute = instance.testComplexType.testComplexType2.testKwantWrd._waarde
        assert result_attribute == expected_attribute


def test_get_attribute_by_dotnotation_waarde_shortcut(subtests):
    instance = AllCasesTestClass()
    with subtests.test(msg='attribute 2 levels deep with waarde shortcut enabled'):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(instance, 'testKwantWrd')
        expected_attribute = instance.testKwantWrd._waarde
        assert result_attribute.objectUri == expected_attribute.objectUri

    with subtests.test(msg='attribute 2 levels deep with waarde shortcut enabled and cardinality > 1'):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(instance, 'testKwantWrdMetKard[]')
        expected_attribute = instance.testKwantWrdMetKard[0]._waarde
        assert result_attribute.objectUri == expected_attribute.objectUri

    with subtests.test(msg='attribute 4 levels deep with waarde shortcut enabled'):
        result_attribute = DotnotationHelper.get_attribute_by_dotnotation(instance,
                                                                           'testComplexType.testComplexType2.testKwantWrd')
        expected_attribute = instance.testComplexType.testComplexType2.testKwantWrd._waarde
        assert result_attribute.objectUri == expected_attribute.objectUri


def test_set_attribute_by_dotnotation_complex_value_convert_scenarios(subtests):
    instance = AllCasesTestClass()

    with subtests.test(msg='setting None'):
        DotnotationHelper.set_attribute_by_dotnotation(instance,
                                                       dotnotation='testComplexTypeMetKard[].testStringField',
                                                       value='value1|value2', convert_warnings=False)
        assert instance.testComplexTypeMetKard[0].testStringField == 'value1'
        assert instance.testComplexTypeMetKard[1].testStringField == 'value2'

    with subtests.test(msg='setting None'):
        DotnotationHelper.set_attribute_by_dotnotation(instance,
                                                       dotnotation='testComplexTypeMetKard[].testStringField',
                                                       value='value1', convert_warnings=False)
        assert instance.testComplexTypeMetKard[0].testStringField == 'value1'


def test_set_attribute_by_dotnotation_decimal_value_convert_scenarios(subtests, caplog):
    instance = AllCasesTestClass()

    with subtests.test(msg='setting None'):
        instance.testDecimalField = 1.0
        assert instance.testDecimalField == 1.0
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testDecimalField', None, convert_warnings=False)
        assert instance.testDecimalField is None

    with subtests.test(msg='correctly typed and convert=True'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testDecimalField', 9.0, convert_warnings=False)
        assert instance.testDecimalField == 9.0

    with subtests.test(msg='correctly typed and convert=False'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testDecimalField', 8.0, convert=False,
                                                       convert_warnings=False)
        assert instance.testDecimalField == 8.0

    with subtests.test(msg='incorrectly typed and convert=True'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testDecimalField', "7.0", convert_warnings=False)
        assert instance.testDecimalField == 7.0

    with subtests.test(msg='incorrectly typed and convert=False (converted by set_waarde method on attribute itself)'):
        caplog.clear()
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testDecimalField', "6.0", convert=False)
        assert instance.testDecimalField == 6.0
        assert caplog.records[0].levelno == logging.WARNING
        caplog.clear()

    with subtests.test(msg='cardinality > 1 and correctly typed and convert=True'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testDecimalFieldMetKard', [9.0],
                                                       convert_warnings=False)
        assert instance.testDecimalFieldMetKard[0] == 9.0

    with subtests.test(msg='cardinality > 1 and correctly typed and convert=False'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testDecimalFieldMetKard', [8.0], convert=False)
        assert instance.testDecimalFieldMetKard[0] == 8.0

    with subtests.test(msg='cardinality > 1 and incorrectly typed and convert=True'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testDecimalFieldMetKard', ["7.0"],
                                                       convert_warnings=False)
        assert instance.testDecimalFieldMetKard[0] == 7.0

    with subtests.test(msg='cardinality > 1 and incorrectly typed and convert=False (converted by set_waarde method on attribute itself)'):
        caplog.clear()
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testDecimalFieldMetKard', ["6.0"], convert=False)
        assert instance.testDecimalFieldMetKard[0] == 6.0
        assert caplog.records[0].levelno == logging.WARNING
        caplog.clear()


def test_set_attributes_by_dotnotation_default_values(subtests):
    instance = AllCasesTestClass()

    with subtests.test(msg='attribute 1 level deep'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testDecimalField', 6.0)
        assert instance.testDecimalField == 6.0

    with subtests.test(msg='attribute 1 level deep with cardinality > 1'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testStringFieldMetKard[]', 'a|b')
        assert instance.testStringFieldMetKard == ['a', 'b']

    with subtests.test(msg='attribute keuzelijst 1 level deep with cardinality > 1'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testKeuzelijstMetKard[]', 'waarde-1|waarde-2')
        assert instance.testKeuzelijstMetKard == ['waarde-1', 'waarde-2']

    with subtests.test(msg='attribute 2 levels deep with waarde shortcut disabled'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testKwantWrd.waarde', 5.0)
        assert instance.testKwantWrd.waarde == 5.0

    with subtests.test(msg='attribute 2 levels deep'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testComplexType.testStringField', "abc")
        assert instance.testComplexType.testStringField == 'abc'

    with subtests.test(msg='attribute 2 levels deep with cardinality > 1 and cardinality in first attribute'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testComplexTypeMetKard[].testStringField', '1.1|2.1')
        assert instance.testComplexTypeMetKard[1].testStringField == '2.1'

    with subtests.test(msg='attribute 2 levels deep with cardinality > 1 and cardinality in second attribute'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testComplexType.testStringFieldMetKard[]',
                                                       '1.1|1.2')
        assert instance.testComplexType.testStringFieldMetKard[0] == '1.1'
        assert instance.testComplexType.testStringFieldMetKard[1] == '1.2'

    with subtests.test(msg='attribute 2 levels deep with cardinality > 1'):
        with pytest.raises(ValueError):
            DotnotationHelper.set_attribute_by_dotnotation(instance,
                                                           'testComplexTypeMetKard[].testStringFieldMetKard[]', '')

    with subtests.test(msg='attribute 3 levels deep'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testComplexType.testComplexType2.testStringField',
                                                       "def")
        assert instance.testComplexType.testComplexType2.testStringField == 'def'

    with subtests.test(msg='attribute 3 levels deep with cardinality > 1'):
        with pytest.raises(ValueError):
            DotnotationHelper.set_attribute_by_dotnotation(
                instance, 'testComplexTypeMetKard[].testComplexType2MetKard[].testStringField', '')

    with subtests.test(msg='attribute 4 levels deep with waarde shortcut disabled'):
        DotnotationHelper.set_attribute_by_dotnotation(instance,
                                                       'testComplexType.testComplexType2.testKwantWrd.waarde', 4.0)
        assert instance.testComplexType.testComplexType2.testKwantWrd.waarde == 4.0


def test_set_attributes_by_dotnotation_default_values_empty(subtests):
    instance = AllCasesTestClass()

    with subtests.test(msg='attribute 1 level deep'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testDecimalField', '')
        assert instance.testDecimalField is None

    with subtests.test(msg='attribute 1 level deep with cardinality > 1'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testStringFieldMetKard[]', '')
        assert instance.testStringFieldMetKard == []

    with subtests.test(msg='attribute keuzelijst 1 level deep with cardinality > 1'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testKeuzelijstMetKard[]', '')
        assert instance.testKeuzelijstMetKard == []

    with subtests.test(msg='attribute 2 levels deep with waarde shortcut disabled'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testKwantWrd.waarde', '')
        assert instance.testKwantWrd.waarde is None

    with subtests.test(msg='attribute 2 levels deep'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testComplexType.testStringField', '')
        assert instance.testComplexType.testStringField is None

    with subtests.test(msg='attribute 2 levels deep with cardinality > 1 and cardinality in first attribute'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testComplexTypeMetKard[].testStringField', '')
        assert instance.testComplexTypeMetKard[0].testStringField is None

    with subtests.test(msg='attribute 2 levels deep with cardinality > 1 and cardinality in second attribute'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testComplexType.testStringFieldMetKard[]', '')
        assert instance.testComplexType.testStringFieldMetKard == []


def test_set_attribute_by_dotnotation_using_settings(subtests):
    dnh = DotnotationHelper(cardinality_indicator='()', separator='*', waarde_shortcut=False, cardinality_separator='/')

    instance = AllCasesTestClass()

    with subtests.test(msg='attribute 1 level deep with cardinality > 1'):
        dnh.set_attribute_by_dotnotation_instance(instance, 'testStringFieldMetKard()', 'a/b')
        assert instance.testStringFieldMetKard == ['a', 'b']

    with subtests.test(msg='attribute 2 levels deep'):
        dnh.set_attribute_by_dotnotation_instance(instance, 'testComplexType*testStringField', "abc")
        assert instance.testComplexType.testStringField == 'abc'

    with subtests.test(msg='attribute 2 levels deep with cardinality > 1'):
        dnh.set_attribute_by_dotnotation_instance(instance,
                                                       'testComplexTypeMetKard()*testStringField', '1.1/1.2')
        assert instance.testComplexTypeMetKard[1].testStringField == '1.2'


def test_set_attribute_by_dotnotation_waarde_shortcut(subtests):
    instance = AllCasesTestClass()

    with subtests.test(msg='attribute 1 level deep with waarde shortcut enabled'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testKwantWrd', 5.0)
        assert instance.testKwantWrd.waarde == 5.0

    with subtests.test(msg='attribute 1 level deep with cardinality > 1 and waarde shortcut enabled'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testKwantWrdMetKard[]', '0.0|1.0')
        assert instance.testKwantWrdMetKard[0].waarde == 0.0
        assert instance.testKwantWrdMetKard[1].waarde == 1.0

    with subtests.test(msg='attribute 2 levels deep with cardinality > 1 (first part) and with waarde shortcut enabled'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testComplexTypeMetKard[].testKwantWrd', '8.0|9.0')
        assert instance.testComplexTypeMetKard[0].testKwantWrd.waarde == 8.0
        assert instance.testComplexTypeMetKard[1].testKwantWrd.waarde == 9.0

    with subtests.test(msg='attribute 2 levels deep with cardinality > 1 (last part) and with waarde shortcut enabled'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testComplexType.testKwantWrdMetKard[]', '2.0|3.0')
        assert instance.testComplexType.testKwantWrdMetKard[0].waarde == 2.0
        assert instance.testComplexType.testKwantWrdMetKard[1].waarde == 3.0

    with subtests.test(msg='attribute 3 levels deep with waarde shortcut enabled'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testComplexType.testComplexType2.testKwantWrd', 4.0)
        assert instance.testComplexType.testComplexType2.testKwantWrd.waarde == 4.0

    with subtests.test(msg='attribute 3 levels deep with cardinality > 1 (second part) and with waarde shortcut enabled'):
        DotnotationHelper.set_attribute_by_dotnotation(instance, 'testComplexType.testComplexType2MetKard[].testKwantWrd',
                                                       '6.0|7.0')
        assert instance.testComplexType.testComplexType2MetKard[0].testKwantWrd.waarde == 6.0
        assert instance.testComplexType.testComplexType2MetKard[1].testKwantWrd.waarde == 7.0
