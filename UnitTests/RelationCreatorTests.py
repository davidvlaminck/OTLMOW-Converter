import unittest

from otlmow_model.Classes.Onderdeel.Bevestiging import Bevestiging
from otlmow_model.Classes.Onderdeel.Voedt import Voedt
from otlmow_model.Exceptions.RelationDeprecationWarning import RelationDeprecationWarning
from otlmow_model.Helpers.RelationValidator import RelationValidator

from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestClasses.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.Exceptions.CouldNotCreateRelationError import CouldNotCreateRelationError
from otlmow_converter.RelationCreator import create_relation


class RelationCreatorTests(unittest.TestCase):
    def test_create_valid_relation(self):
        all_cases = AllCasesTestClass()
        all_cases.assetId.identificator = 'all_cases'
        another = AnotherTestClass()
        another.assetId.identificator = 'another'

        relation = create_relation(source=another, target=all_cases, relation=Bevestiging)
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
            relation = create_relation(source=another, target=all_cases, relation=Voedt)
            self.assertIsNone(relation)

    def test_create_deprecated_relation(self):
        all_cases = AllCasesTestClass()
        all_cases.assetId.identificator = 'all_cases'
        another = AnotherTestClass()
        another.assetId.identificator = 'another'

        with self.assertWarns(RelationDeprecationWarning):
            relation = create_relation(source=all_cases, target=another, relation=Voedt)

        self.assertIsNotNone(relation)

    def test_create_valid_relation_without_assetIds(self):
        all_cases = AllCasesTestClass()
        another = AnotherTestClass()

        with self.assertRaises(AttributeError):
            relation = create_relation(source=another, target=all_cases, relation=Bevestiging)
            self.assertIsNone(relation)
