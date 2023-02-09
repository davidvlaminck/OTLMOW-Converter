import unittest


from otlmow_model.Exceptions.RelationDeprecationWarning import RelationDeprecationWarning

from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestClasses.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from UnitTests.TestClasses.Classes.Onderdeel.Bevestiging import Bevestiging
from UnitTests.TestClasses.Classes.Onderdeel.Voedt import Voedt

from otlmow_converter.Exceptions.CouldNotCreateRelationError import CouldNotCreateRelationError
from otlmow_converter.RelationCreator import create_relation


class RelationCreatorTests(unittest.TestCase):
    def test_create_valid_relation(self):
        all_cases = AllCasesTestClass()
        all_cases.assetId.identificator = 'all_cases'
        another = AnotherTestClass()
        another.assetId.identificator = 'another'

        relation = create_relation(source=another, target=all_cases, relation_type=Bevestiging)
        self.assertIsNotNone(relation)
        self.assertEqual(relation.typeURI, Bevestiging.typeURI)
        self.assertEqual(relation.bronAssetId.identificator, another.assetId.identificator)
        self.assertEqual(relation.doelAssetId.identificator, all_cases.assetId.identificator)

    def test_create_relation_input_parameters(self):
        all_cases = AllCasesTestClass()
        all_cases.assetId.identificator = 'all_cases'
        another = AnotherTestClass()
        another.assetId.identificator = 'another'

        with self.subTest('testing if there are enough not None parameters'):
            with self.assertRaises(ValueError):
                create_relation(source=None, source_typeURI=None, source_uuid='', target=all_cases,
                                relation_type=Bevestiging,
                                class_directory='UnitTests.TestClasses.Classes')
            with self.assertRaises(ValueError):
                create_relation(source=None, source_typeURI='', source_uuid=None, target=all_cases,
                                relation_type=Bevestiging,
                                class_directory='UnitTests.TestClasses.Classes')
            with self.assertRaises(ValueError):
                create_relation(target=None, target_typeURI=None, target_uuid='', source=all_cases,
                                relation_type=Bevestiging,
                                class_directory='UnitTests.TestClasses.Classes')
            with self.assertRaises(ValueError):
                create_relation(target=None, target_typeURI='', target_uuid=None, source=all_cases,
                                relation_type=Bevestiging,
                                class_directory='UnitTests.TestClasses.Classes')

        with self.subTest('testing uuid format'):
            relation = create_relation(source_typeURI=another.typeURI, target=all_cases,
                                       source_uuid='00000000-0000-0000-0000-000000000000',
                                       relation_type=Bevestiging, class_directory='UnitTests.TestClasses.Classes')
            self.assertIsNotNone(relation)
            relation = create_relation(target_typeURI=another.typeURI, source=all_cases,
                                       target_uuid='00000000-0000-0000-0000-000000000000',
                                       relation_type=Bevestiging, class_directory='UnitTests.TestClasses.Classes')
            self.assertIsNotNone(relation)
            with self.assertRaises(ValueError):
                create_relation(source_typeURI=another.typeURI, source_uuid='', target=all_cases,
                                relation_type=Bevestiging, class_directory='UnitTests.TestClasses.Classes')
            with self.assertRaises(ValueError):
                create_relation(target_typeURI=another.typeURI, target_uuid='', source=all_cases,
                                relation_type=Bevestiging, class_directory='UnitTests.TestClasses.Classes')

        with self.subTest('testing for warning if there are too many not None parameters'):
            with self.assertWarns(RuntimeWarning):
                create_relation(source=another, source_typeURI=another.typeURI, source_uuid='', target=all_cases,
                                relation_type=Bevestiging,
                                class_directory='UnitTests.TestClasses.Classes')
            with self.assertWarns(RuntimeWarning):
                create_relation(source=another, target=all_cases, target_typeURI=all_cases.typeURI,
                                relation_type=Bevestiging)

        with self.subTest('creating relations using uuid and typeURI'):
            relation = create_relation(source_typeURI=another.typeURI, source_uuid='00000000-0000-0000-0000-000000000000',
                                       target=all_cases, relation_type=Bevestiging,
                                       class_directory='UnitTests.TestClasses.Classes')
            self.assertIsNotNone(relation)
            self.assertEqual(relation.typeURI, Bevestiging.typeURI)
            self.assertEqual(relation.bronAssetId.identificator, '00000000-0000-0000-0000-000000000000'
                                                                 '-b25kZXJkZWVsI0Fub3RoZXJUZXN0Q2xhc3M')
            self.assertEqual(relation.doelAssetId.identificator, all_cases.assetId.identificator)

            relation = create_relation(target_typeURI=another.typeURI, target_uuid='00000000-0000-0000-0000-000000000000',
                                       source=all_cases, relation_type=Bevestiging,
                                       class_directory='UnitTests.TestClasses.Classes')
            self.assertIsNotNone(relation)
            self.assertEqual(relation.typeURI, Bevestiging.typeURI)
            self.assertEqual(relation.doelAssetId.identificator, '00000000-0000-0000-0000-000000000000'
                                                                 '-b25kZXJkZWVsI0Fub3RoZXJUZXN0Q2xhc3M')
            self.assertEqual(relation.bronAssetId.identificator, all_cases.assetId.identificator)

        with self.subTest('creating relations using instances of objects'):
            relation = create_relation(source=another, target=all_cases, relation_type=Bevestiging, class_directory='UnitTests.TestClasses.Classes')
            self.assertIsNotNone(relation)
            self.assertEqual(relation.typeURI, Bevestiging.typeURI)
            self.assertEqual(relation.bronAssetId.identificator, another.assetId.identificator)
            self.assertEqual(relation.doelAssetId.identificator, all_cases.assetId.identificator)

    def test_create_invalid_relation(self):
        all_cases = AllCasesTestClass()
        all_cases.assetId.identificator = 'all_cases'
        another = AnotherTestClass()
        another.assetId.identificator = 'another'

        with self.assertRaises(CouldNotCreateRelationError):
            relation = create_relation(source=another, target=all_cases, relation_type=Voedt)
            self.assertIsNone(relation)

    def test_create_deprecated_relation(self):
        all_cases = AllCasesTestClass()
        all_cases.assetId.identificator = 'all_cases'
        another = AnotherTestClass()
        another.assetId.identificator = 'another'

        with self.assertWarns(RelationDeprecationWarning):
            relation = create_relation(source=all_cases, target=another, relation_type=Voedt)

        self.assertIsNotNone(relation)

    def test_create_valid_relation_without_assetIds(self):
        all_cases = AllCasesTestClass()
        another = AnotherTestClass()

        with self.assertRaises(AttributeError):
            relation = create_relation(source=another, target=all_cases, relation_type=Bevestiging)
            self.assertIsNone(relation)
