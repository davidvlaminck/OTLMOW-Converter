import os
import unittest
from datetime import date, datetime, time
from pathlib import Path

from UnitTests.SettingManagerForUnit_test import get_settings_path_for_unittests
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.ExcelExporter import ExcelExporter
from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
from otlmow_converter.OtlmowConverter import OtlmowConverter


class ExcelExporterTests(unittest.TestCase):
    @staticmethod
    def set_up_converter():
        settings_file_location = get_settings_path_for_unittests()
        otl_converter = OtlmowConverter(settings_path=settings_file_location)
        return otl_converter

    def test_init_importer_only_load_with_settings(self):
        otl_converter = self.set_up_converter()

        with self.subTest('load with correct settings'):
            exporter = ExcelExporter(settings=otl_converter.settings)
            self.assertIsNotNone(exporter)

        with self.subTest('load without settings'):
            with self.assertRaises(ValueError):
                ExcelExporter(settings=None)

        with self.subTest('load with incorrect settings (no file_formats)'):
            with self.assertRaises(ValueError):
                ExcelExporter(settings={"auth_options": [{}]})

        with self.subTest('load with incorrect settings (file_formats but no xls)'):
            with self.assertRaises(ValueError):
                ExcelExporter(settings={"file_formats": [{}]})

    def test_export_and_then_import_unnested_attributes(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = ExcelImporter(settings=converter.settings)
        exporter = ExcelExporter(settings=converter.settings, class_directory='UnitTests.TestClasses.Classes')
        file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.xlsx'
        instance = AllCasesTestClass()
        instance.assetId.identificator = '0000-0000'
        instance.testBooleanField = False
        instance.testDateField = date(2019, 9, 20)
        instance.testDateTimeField = datetime(2001, 12, 15, 22, 22, 15)
        instance.testDecimalField = 79.07
        instance.testDecimalFieldMetKard = [10.0, 20.0]
        instance.testEenvoudigType.waarde = 'string1'
        instance.testIntegerField = -55
        instance.testIntegerFieldMetKard = [76, 2]
        instance.testKeuzelijst = 'waarde-4'
        instance.testKeuzelijstMetKard = ['waarde-4', 'waarde-3']
        instance.testKwantWrd.waarde = 98.21
        instance.testStringField = 'oFfeDLp'
        instance.testStringFieldMetKard = ['string1', 'string2']
        instance.testTimeField = time(11, 5, 26)
        exporter.export_to_file(list_of_objects=[instance], filepath=file_location,
                                split_per_type=False)

        objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
        self.assertEqual(1, len(objects))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)
        self.assertEqual('0000-0000', instance.assetId.identificator)

        self.assertEqual(False, instance.testBooleanField)
        self.assertEqual(date(2019, 9, 20), instance.testDateField)
        self.assertEqual(datetime(2001, 12, 15, 22, 22, 15), instance.testDateTimeField)
        self.assertEqual(79.07, instance.testDecimalField)
        self.assertListEqual([10.0, 20.0], instance.testDecimalFieldMetKard)
        self.assertEqual('string1', instance.testEenvoudigType.waarde)
        self.assertEqual(-55, instance.testIntegerField)
        self.assertListEqual([76, 2], instance.testIntegerFieldMetKard)
        self.assertEqual('waarde-4', instance.testKeuzelijst)
        self.assertListEqual(['waarde-4', 'waarde-3'], instance.testKeuzelijstMetKard)
        self.assertEqual(98.21, instance.testKwantWrd.waarde)
        self.assertEqual('oFfeDLp', instance.testStringField)
        self.assertEqual('string1', instance.testStringFieldMetKard[0])
        self.assertEqual('string2', instance.testStringFieldMetKard[1])
        self.assertEqual(time(11, 5, 26), instance.testTimeField)

        os.unlink(file_location)

    def test_export_and_then_import_nested_attributes_level_1(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = ExcelImporter(settings=converter.settings)
        exporter = ExcelExporter(settings=converter.settings, class_directory='UnitTests.TestClasses.Classes')
        file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.xlsx'
        instance = AllCasesTestClass()
        instance.assetId.identificator = '0000'

        instance._testEenvoudigTypeMetKard.add_empty_value()
        instance._testEenvoudigTypeMetKard.add_empty_value()
        instance.testEenvoudigTypeMetKard[0].waarde = 'string1'
        instance.testEenvoudigTypeMetKard[1].waarde = 'string2'
        instance._testKwantWrdMetKard.add_empty_value()
        instance._testKwantWrdMetKard.add_empty_value()
        instance.testKwantWrdMetKard[0].waarde = 10.0
        instance.testKwantWrdMetKard[1].waarde = 20.0

        instance.testComplexType.testBooleanField = True
        instance.testComplexType.testKwantWrd.waarde = 65.14
        instance.testComplexType._testKwantWrdMetKard.add_empty_value()
        instance.testComplexType._testKwantWrdMetKard.add_empty_value()
        instance.testComplexType.testKwantWrdMetKard[0].waarde = 10.0
        instance.testComplexType.testKwantWrdMetKard[1].waarde = 20.0
        instance.testComplexType.testStringField = 'KmCtMXM'
        instance.testComplexType.testStringFieldMetKard = ['string1', 'string2']

        instance._testComplexTypeMetKard.add_empty_value()
        instance._testComplexTypeMetKard.add_empty_value()
        instance.testComplexTypeMetKard[0].testBooleanField = True
        instance.testComplexTypeMetKard[1].testBooleanField = False
        instance.testComplexTypeMetKard[0].testKwantWrd.waarde = 10.0
        instance.testComplexTypeMetKard[1].testKwantWrd.waarde = 20.0
        instance.testComplexTypeMetKard[0].testStringField = 'string1'
        instance.testComplexTypeMetKard[1].testStringField = 'string2'
        instance.testUnionType.unionString = 'RWKofW'

        instance._testUnionTypeMetKard.add_empty_value()
        instance._testUnionTypeMetKard.add_empty_value()
        instance.testUnionTypeMetKard[0].unionKwantWrd.waarde = 10.0
        instance.testUnionTypeMetKard[1].unionKwantWrd.waarde = 20.0

        exporter.export_to_file(list_of_objects=[instance], filepath=file_location,
                                split_per_type=False)

        objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
        self.assertEqual(1, len(objects))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)

        self.assertEqual('string1', instance.testEenvoudigTypeMetKard[0].waarde)
        self.assertEqual('string2', instance.testEenvoudigTypeMetKard[1].waarde)
        self.assertEqual(10.0, instance.testKwantWrdMetKard[0].waarde)
        self.assertEqual(20.0, instance.testKwantWrdMetKard[1].waarde)
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
        self.assertEqual('string1', instance.testComplexTypeMetKard[0].testStringField)
        self.assertEqual('string2', instance.testComplexTypeMetKard[1].testStringField)
        self.assertEqual('RWKofW', instance.testUnionType.unionString)
        self.assertEqual(None, instance.testUnionType.unionKwantWrd.waarde)
        self.assertEqual(10.0, instance.testUnionTypeMetKard[0].unionKwantWrd.waarde)
        self.assertEqual(20.0, instance.testUnionTypeMetKard[1].unionKwantWrd.waarde)
        self.assertEqual('0000', instance.assetId.identificator)

        os.unlink(file_location)

    def test_export_and_then_import_nested_attributes_level_2(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = ExcelImporter(settings=converter.settings)
        exporter = ExcelExporter(settings=converter.settings, class_directory='UnitTests.TestClasses.Classes')
        file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.xlsx'
        instance = AllCasesTestClass()
        instance.assetId.identificator = '0000'

        instance.testComplexType.testComplexType2.testKwantWrd.waarde = 76.8
        instance.testComplexType.testComplexType2.testStringField = 'GZBzgRhOrQvfZaN'
        instance.testComplexType._testComplexType2MetKard.add_empty_value()
        instance.testComplexType._testComplexType2MetKard.add_empty_value()
        instance.testComplexType.testComplexType2MetKard[0].testKwantWrd.waarde = 10.0
        instance.testComplexType.testComplexType2MetKard[1].testKwantWrd.waarde = 20.0
        instance.testComplexType.testComplexType2MetKard[0].testStringField = 'string1'
        instance.testComplexType.testComplexType2MetKard[1].testStringField = 'string2'

        instance._testComplexTypeMetKard.add_empty_value()
        instance._testComplexTypeMetKard.add_empty_value()
        instance.testComplexTypeMetKard[0].testComplexType2.testKwantWrd.waarde = 10.0
        instance.testComplexTypeMetKard[1].testComplexType2.testKwantWrd.waarde = 20.0
        instance.testComplexTypeMetKard[0].testComplexType2.testStringField = 'string1'
        instance.testComplexTypeMetKard[1].testComplexType2.testStringField = 'string2'

        exporter.export_to_file(list_of_objects=[instance], filepath=file_location,
                                split_per_type=False)

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
        self.assertEqual('0000', instance.assetId.identificator)

        os.unlink(file_location)
