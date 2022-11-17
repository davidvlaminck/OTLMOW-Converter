from unittest import TestCase

from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.DotnotationHelper import DotnotationHelper


class DotnotationOnAttributeTests(TestCase):
    def test_fill_with_dummy_data_complex_attr(self):
        instance = AllCasesTestClass()
        attr = instance._testComplexType
        attr.fill_with_dummy_data()
        self.assertIsNotNone(instance.testComplexType.testBooleanField)
        self.assertIsNotNone(instance.testComplexType.testComplexType2MetKard[0].testStringField)
        self.assertIsNotNone(instance.testComplexType.testKwantWrd.waarde)
        self.assertEquals('testComplexType.testComplexType2MetKard[].testStringField',
                          DotnotationHelper.get_dotnotation(instance.testComplexType.testComplexType2MetKard[0]._testStringField))

    def test_dotnotation_on_attribute(self):
        instance = AllCasesTestClass()

        with self.subTest('complex attribute'):
            self.assertEqual('testComplexType', DotnotationHelper.get_dotnotation(instance._testComplexType))
            self.assertEqual('testComplexType.testBooleanField',
                             DotnotationHelper.get_dotnotation(instance.testComplexType._testBooleanField))
            self.assertEqual('testComplexType.testComplexType2',
                             DotnotationHelper.get_dotnotation(instance.testComplexType._testComplexType2))
            self.assertEqual('testComplexType.testComplexType2.testStringField',
                             DotnotationHelper.get_dotnotation(instance.testComplexType.testComplexType2._testStringField))
            self.assertEqual('testComplexType.testComplexType2.testKwantWrd',
                             DotnotationHelper.get_dotnotation(instance.testComplexType.testComplexType2._testKwantWrd))
            self.assertEqual('testComplexType.testComplexType2.testKwantWrd.waarde',
                             DotnotationHelper.get_dotnotation(instance.testComplexType.testComplexType2.testKwantWrd._waarde))

        with self.subTest('complex attribute with cardinality'):
            self.assertEqual('testComplexTypeMetKard[]',
                             DotnotationHelper.get_dotnotation(instance._testComplexTypeMetKard))
            self.assertEqual('testComplexTypeMetKard[].testBooleanField',
                             DotnotationHelper.get_dotnotation(instance.testComplexTypeMetKard[0]._testBooleanField))
            self.assertEqual('testComplexTypeMetKard[].testComplexType2MetKard[]',
                             DotnotationHelper.get_dotnotation(instance.testComplexTypeMetKard[0]._testComplexType2MetKard))
            self.assertEqual('testComplexTypeMetKard[].testComplexType2MetKard[].testStringField',
                             DotnotationHelper.get_dotnotation(instance.testComplexTypeMetKard[0].testComplexType2MetKard[0]._testStringField))

        with self.subTest('non-complex attributes'):
            self.assertEqual('testKeuzelijst', DotnotationHelper.get_dotnotation(instance._testKeuzelijst))
            self.assertEqual('testStringField', DotnotationHelper.get_dotnotation(instance._testStringField))
            self.assertEqual('testBooleanField', DotnotationHelper.get_dotnotation(instance._testBooleanField))
            self.assertEqual('testDecimalField', DotnotationHelper.get_dotnotation(instance._testDecimalField))

        with self.subTest('non-complex attribute with cardinality'):
            self.assertEqual('testKeuzelijstMetKard[]', DotnotationHelper.get_dotnotation(instance._testKeuzelijstMetKard))
            self.assertEqual('testStringFieldMetKard[]', DotnotationHelper.get_dotnotation(instance._testStringFieldMetKard))
            self.assertEqual('testDecimalFieldMetKard[]', DotnotationHelper.get_dotnotation(instance._testDecimalFieldMetKard))

        with self.subTest('dte attribute'):
            self.assertEqual('testEenvoudigType', DotnotationHelper.get_dotnotation(instance._testEenvoudigType))

        with self.subTest('kwant waarde attribute'):
            self.assertEqual('testKwantWrd', DotnotationHelper.get_dotnotation(instance._testKwantWrd))
            self.assertEqual('testKwantWrd.waarde', DotnotationHelper.get_dotnotation(instance.testKwantWrd._waarde))
            self.assertEqual('testKwantWrd.standaardEenheid',
                             DotnotationHelper.get_dotnotation(instance.testKwantWrd._standaardEenheid))
            self.assertEqual('testKwantWrdMetKard[]', DotnotationHelper.get_dotnotation(instance._testKwantWrdMetKard))
            self.assertEqual('testKwantWrdMetKard[].waarde',
                             DotnotationHelper.get_dotnotation(instance.testKwantWrdMetKard[0]._waarde))
            self.assertEqual('testKwantWrdMetKard[].standaardEenheid',
                             DotnotationHelper.get_dotnotation(instance.testKwantWrdMetKard[0]._standaardEenheid))

        with self.subTest('union attribute'):
            self.assertEqual('testUnionType', DotnotationHelper.get_dotnotation(instance._testUnionType))
            self.assertEqual('testUnionType.unionString',
                             DotnotationHelper.get_dotnotation(instance.testUnionType._unionString))
            self.assertEqual('testUnionType.unionKwantWrd',
                             DotnotationHelper.get_dotnotation(instance.testUnionType._unionKwantWrd))
            self.assertEqual('testUnionType.unionKwantWrd.waarde',
                             DotnotationHelper.get_dotnotation(instance.testUnionType.unionKwantWrd._waarde))

        with self.subTest('union attribute with cardinality'):
            self.assertEqual('testUnionTypeMetKard[]',
                             DotnotationHelper.get_dotnotation(instance._testUnionTypeMetKard))
            self.assertEqual('testUnionTypeMetKard[].unionString',
                             DotnotationHelper.get_dotnotation(instance.testUnionTypeMetKard[0]._unionString))
            self.assertEqual('testUnionTypeMetKard[].unionKwantWrd',
                             DotnotationHelper.get_dotnotation(instance.testUnionTypeMetKard[0]._unionKwantWrd))
            self.assertEqual('testUnionTypeMetKard[].unionKwantWrd.waarde',
                             DotnotationHelper.get_dotnotation(instance.testUnionTypeMetKard[0].unionKwantWrd._waarde))
