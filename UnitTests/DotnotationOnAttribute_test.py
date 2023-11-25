from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.DotnotationHelper import DotnotationHelper


def test_fill_with_dummy_data_complex_attr():
    instance = AllCasesTestClass()
    attr = instance._testComplexType
    attr.fill_with_dummy_data()
    assert instance.testComplexType.testBooleanField is not None
    assert instance.testComplexType.testComplexType2MetKard[0].testStringField is not None
    assert instance.testComplexType.testKwantWrd.waarde is not None
    assert 'testComplexType.testComplexType2MetKard[].testStringField' == DotnotationHelper.get_dotnotation(
        instance.testComplexType.testComplexType2MetKard[0]._testStringField)


def test_dotnotation_on_attribute(subtests):
    instance = AllCasesTestClass()

    with subtests.test(msg='complex attribute'):
        assert DotnotationHelper.get_dotnotation(instance._testComplexType) == 'testComplexType'
        assert DotnotationHelper.get_dotnotation(
            instance.testComplexType._testBooleanField) == 'testComplexType.testBooleanField'
        assert DotnotationHelper.get_dotnotation(
            instance.testComplexType._testComplexType2) == 'testComplexType.testComplexType2'
        assert DotnotationHelper.get_dotnotation(
            instance.testComplexType.testComplexType2._testStringField) == 'testComplexType.testComplexType2.testStringField'
        assert DotnotationHelper.get_dotnotation(
            waarde_shortcut=False,
            attribute=instance.testComplexType.testComplexType2._testKwantWrd) == 'testComplexType.testComplexType2.testKwantWrd'
        assert DotnotationHelper.get_dotnotation(
            instance.testComplexType.testComplexType2.testKwantWrd._waarde,
            waarde_shortcut=False) == 'testComplexType.testComplexType2.testKwantWrd.waarde'
        assert DotnotationHelper.get_dotnotation(
            instance.testComplexType.testComplexType2.testKwantWrd._waarde,
            waarde_shortcut=True) == 'testComplexType.testComplexType2.testKwantWrd'

    with subtests.test(msg='complex attribute with cardinality'):
        assert 'testComplexTypeMetKard[]' == DotnotationHelper.get_dotnotation(instance._testComplexTypeMetKard)
        assert 'testComplexTypeMetKard[].testBooleanField' == DotnotationHelper.get_dotnotation(
            instance.testComplexTypeMetKard[0]._testBooleanField)
        assert 'testComplexTypeMetKard[].testComplexType2MetKard[]' == DotnotationHelper.get_dotnotation(
            instance.testComplexTypeMetKard[0]._testComplexType2MetKard)
        assert 'testComplexTypeMetKard[].testComplexType2MetKard[].testStringField' == DotnotationHelper.get_dotnotation(
            instance.testComplexTypeMetKard[0].testComplexType2MetKard[0]._testStringField)

    with subtests.test(msg='non-complex attributes'):
        assert DotnotationHelper.get_dotnotation(instance._testKeuzelijst) == 'testKeuzelijst'
        assert DotnotationHelper.get_dotnotation(instance._testStringField) == 'testStringField'
        assert DotnotationHelper.get_dotnotation(instance._testBooleanField) == 'testBooleanField'
        assert DotnotationHelper.get_dotnotation(instance._testDecimalField) == 'testDecimalField'

    with subtests.test(msg='non-complex attribute with cardinality'):
        assert DotnotationHelper.get_dotnotation(instance._testKeuzelijstMetKard) == 'testKeuzelijstMetKard[]'
        assert DotnotationHelper.get_dotnotation(instance._testStringFieldMetKard) == 'testStringFieldMetKard[]'
        assert DotnotationHelper.get_dotnotation(instance._testDecimalFieldMetKard) == 'testDecimalFieldMetKard[]'

    with subtests.test(msg='dte attribute'):
        assert DotnotationHelper.get_dotnotation(instance._testEenvoudigType) == 'testEenvoudigType'

    with subtests.test(msg='kwant waarde attribute'):
        assert DotnotationHelper.get_dotnotation(instance._testKwantWrd, waarde_shortcut=False) == 'testKwantWrd'
        assert DotnotationHelper.get_dotnotation(instance.testKwantWrd._waarde, waarde_shortcut=False) == 'testKwantWrd.waarde'
        assert DotnotationHelper.get_dotnotation(
            instance.testKwantWrd._standaardEenheid) == 'testKwantWrd.standaardEenheid'
        assert DotnotationHelper.get_dotnotation(instance._testKwantWrdMetKard, waarde_shortcut=False) == 'testKwantWrdMetKard[]'
        assert DotnotationHelper.get_dotnotation(
            instance.testKwantWrdMetKard[0]._waarde, waarde_shortcut=False) == 'testKwantWrdMetKard[].waarde'
        assert DotnotationHelper.get_dotnotation(
            instance.testKwantWrdMetKard[0]._standaardEenheid) == 'testKwantWrdMetKard[' \
                                                                  '].standaardEenheid'

    with subtests.test(msg='union attribute'):
        assert DotnotationHelper.get_dotnotation(instance._testUnionType) == 'testUnionType'
        assert DotnotationHelper.get_dotnotation(instance.testUnionType._unionString) == 'testUnionType.unionString'
        assert DotnotationHelper.get_dotnotation(instance.testUnionType._unionKwantWrd) == 'testUnionType.unionKwantWrd'
        assert DotnotationHelper.get_dotnotation(
            instance.testUnionType.unionKwantWrd._waarde, waarde_shortcut=False) == 'testUnionType.unionKwantWrd.waarde'

    with subtests.test(msg='union attribute with cardinality'):
        assert DotnotationHelper.get_dotnotation(instance._testUnionTypeMetKard) == 'testUnionTypeMetKard[]'
        assert DotnotationHelper.get_dotnotation(
            instance.testUnionTypeMetKard[0]._unionString) == 'testUnionTypeMetKard[].unionString'
        assert DotnotationHelper.get_dotnotation(
            instance.testUnionTypeMetKard[0]._unionKwantWrd) == 'testUnionTypeMetKard[].unionKwantWrd'
        assert DotnotationHelper.get_dotnotation(
            instance.testUnionTypeMetKard[0].unionKwantWrd._waarde) == 'testUnionTypeMetKard[].unionKwantWrd'
        assert DotnotationHelper.get_dotnotation(
            instance.testUnionTypeMetKard[0].unionKwantWrd._waarde,
            waarde_shortcut=False) == 'testUnionTypeMetKard[].unionKwantWrd.waarde'
