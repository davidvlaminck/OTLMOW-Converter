import os
import unittest
from datetime import date, datetime, time
from pathlib import Path

from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
from otlmow_converter.OtlmowConverter import OtlmowConverter

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class ExcelImporterTests(unittest.TestCase):
    def test_init_importer_only_load_with_settings(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)

        with self.subTest('load with correct settings'):
            importer = ExcelImporter(settings=converter.settings)
            self.assertIsNotNone(importer)

        with self.subTest('load without settings'):
            with self.assertRaises(ValueError):
                ExcelImporter(settings=None)

        with self.subTest('load with incorrect settings (no file_formats)'):
            with self.assertRaises(ValueError):
                ExcelImporter(settings={"auth_options": [{}]})

        with self.subTest('load with incorrect settings (file_formats but no xls)'):
            with self.assertRaises(ValueError):
                ExcelImporter(settings={"file_formats": [{}]})

    def test_load_test_unnested_attributes(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = ExcelImporter(settings=converter.settings)
        file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes.xlsx'
        objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
        self.assertEqual(1, len(objects))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)
        self.assertEqual(False, instance.testBooleanField)
        self.assertEqual(date(2019, 9, 20), instance.testDateField)
        self.assertEqual(datetime(2001, 12, 15, 22, 22, 15), instance.testDateTimeField)
        self.assertEqual(79.07, instance.testDecimalField)
        self.assertListEqual([10.0, 20.0], instance.testDecimalFieldMetKard)
        self.assertEqual('string1', instance.testEenvoudigType.waarde)
        self.assertEqual('string1', instance.testEenvoudigTypeMetKard[0].waarde)
        self.assertEqual('string2', instance.testEenvoudigTypeMetKard[1].waarde)
        self.assertEqual(-55, instance.testIntegerField)
        self.assertListEqual([76, 2], instance.testIntegerFieldMetKard)
        self.assertEqual('waarde-4', instance.testKeuzelijst)
        self.assertListEqual(['waarde-4', 'waarde-3'], instance.testKeuzelijstMetKard)
        self.assertEqual(98.21, instance.testKwantWrd.waarde)
        self.assertEqual(10.0, instance.testKwantWrdMetKard[0].waarde)
        self.assertEqual(20.0, instance.testKwantWrdMetKard[1].waarde)
        self.assertEqual('oFfeDLp', instance.testStringField)
        self.assertEqual('string1', instance.testStringFieldMetKard[0])
        self.assertEqual('string2', instance.testStringFieldMetKard[1])
        self.assertEqual(time(11, 5, 26), instance.testTimeField)

    def test_load_test_ested_attributes_1_level(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = ExcelImporter(settings=converter.settings)
        file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_1.xlsx'
        objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
        self.assertEqual(1, len(objects))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)
        self.assertEqual('YKAzZDhhdTXqkD', instance.assetId.identificator)
        self.assertEqual('DGcQxwCGiBlR', instance.assetId.toegekendDoor)
        self.assertEqual(True, instance.testComplexType.testBooleanField)
        self.assertEqual(65.14, instance.testComplexType.testKwantWrd.waarde)
        self.assertEqual(10.0, instance.testComplexType.testKwantWrdMetKard[0].waarde)
        self.assertEqual(20.0, instance.testComplexType.testKwantWrdMetKard[1].waarde)
        self.assertEqual('KmCtMXM', instance.testComplexType.testStringField)
        self.assertEqual('string1', instance.testComplexType.testStringFieldMetKard[0])
        self.assertEqual('string2', instance.testComplexType.testStringFieldMetKard[1])
        self.assertEqual(True, instance.testComplexTypeMetKard[0].testBooleanField)
        self.assertEqual(False, instance.testComplexTypeMetKard[1].testBooleanField)
        self.assertEqual(10.0, instance.testComplexTypeMetKard[0].testKwantWrd.waarde)
        self.assertEqual(20.0, instance.testComplexTypeMetKard[1].testKwantWrd.waarde)
        self.assertEqual(None, instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde)
        self.assertEqual(None, instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde)
        self.assertEqual('string1', instance.testComplexTypeMetKard[0].testStringField)
        self.assertEqual('string2', instance.testComplexTypeMetKard[1].testStringField)
        self.assertEqual('RWKofW', instance.testUnionType.unionString)
        self.assertEqual(None, instance.testUnionType.unionKwantWrd.waarde)
        self.assertEqual(10.0, instance.testUnionTypeMetKard[0].unionKwantWrd.waarde)
        self.assertEqual(20.0, instance.testUnionTypeMetKard[1].unionKwantWrd.waarde)

    def test_load_test_ested_attributes_2_levels(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = ExcelImporter(settings=converter.settings)
        file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_2.xlsx'
        objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
        self.assertEqual(1, len(objects))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)
        self.assertEqual(76.8, instance.testComplexType.testComplexType2.testKwantWrd.waarde)
        self.assertEqual('GZBzgRhOrQvfZaN', instance.testComplexType.testComplexType2.testStringField)
        self.assertEqual(10.0, instance.testComplexType.testComplexType2MetKard[0].testKwantWrd.waarde)
        self.assertEqual(20.0, instance.testComplexType.testComplexType2MetKard[1].testKwantWrd.waarde)
        self.assertEqual('string1', instance.testComplexType.testComplexType2MetKard[0].testStringField)
        self.assertEqual('string2', instance.testComplexType.testComplexType2MetKard[1].testStringField)
        self.assertEqual(10.0, instance.testComplexTypeMetKard[0].testComplexType2.testKwantWrd.waarde)
        self.assertEqual(20.0, instance.testComplexTypeMetKard[1].testComplexType2.testKwantWrd.waarde)
        self.assertEqual('string1', instance.testComplexTypeMetKard[0].testComplexType2.testStringField)
        self.assertEqual('string2', instance.testComplexTypeMetKard[1].testComplexType2.testStringField)
        self.assertEqual(None, instance.testComplexTypeMetKard[0].testComplexType2MetKard[0].testKwantWrd.waarde)
        self.assertEqual(None, instance.testComplexTypeMetKard[0].testComplexType2MetKard[0].testStringField)

