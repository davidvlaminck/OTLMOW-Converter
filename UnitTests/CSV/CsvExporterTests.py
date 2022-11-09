import os
import unittest
from datetime import date, datetime, time
from pathlib import Path

from UnitTests.SettingManagerForUnitTests import get_settings_path_for_unittests
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.CsvExporter import CsvExporter
from otlmow_converter.FileFormats.CsvImporter import CsvImporter
from otlmow_converter.OtlmowConverter import OtlmowConverter


class CsvExporterTests(unittest.TestCase):
    @staticmethod
    def set_up_facility():
        settings_file_location = get_settings_path_for_unittests()
        otl_facility = OtlmowConverter(settings_path=settings_file_location)
        return otl_facility

    def test_init_importer_only_load_with_settings(self):
        otl_facility = self.set_up_facility()

        with self.subTest('load with correct settings'):
            exporter = CsvExporter(settings=otl_facility.settings)
            self.assertIsNotNone(exporter)

        with self.subTest('load without settings'):
            with self.assertRaises(ValueError):
                CsvExporter(settings=None)

        with self.subTest('load with incorrect settings (no file_formats)'):
            with self.assertRaises(ValueError):
                CsvExporter(settings={"auth_options": [{}]})

        with self.subTest('load with incorrect settings (file_formats but no csv)'):
            with self.assertRaises(ValueError):
                CsvExporter(settings={"file_formats": [{}]})

    def test_load_and_writefile(self):
        otl_facility = self.set_up_facility()
        importer = CsvImporter(settings=otl_facility.settings)
        file_location = Path(__file__).parent / 'test_file_VR.csv'
        objects = importer.import_file(file_location)
        exporter = CsvExporter(settings=otl_facility.settings)
        new_file_location = Path(__file__).parent / 'test_export_file_VR.csv'
        if os.path.isfile(new_file_location):
            os.remove(new_file_location)
        exporter.export_to_file(list_of_objects=objects, filepath=new_file_location)
        self.assertTrue(os.path.isfile(new_file_location))

    def test_find_sorted_header_index(self):
        otl_facility = self.set_up_facility()
        exporter = CsvExporter(settings=otl_facility.settings)
        with self.subTest('no headers yet'):
            exporter.csv_headers = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor']
            result = exporter.find_sorted_header_index('a')
            expected = 3
            self.assertEqual(expected, result)

        with self.subTest('1 header after'):
            exporter.csv_headers = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'a']
            result = exporter.find_sorted_header_index('b')
            expected = 4
            self.assertEqual(expected, result)

        with self.subTest('1 header before'):
            exporter.csv_headers = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'b']
            result = exporter.find_sorted_header_index('a')
            expected = 3
            self.assertEqual(expected, result)

    def test_sort_headers(self):
        otl_facility = self.set_up_facility()
        exporter = CsvExporter(settings=otl_facility.settings)
        with self.subTest('no headers'):
            result = exporter.sort_headers(['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'])
            expected = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor']
            self.assertListEqual(expected, result)

        with self.subTest('2 headers'):
            result = exporter.sort_headers(['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'b', 'a'])
            expected = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'a', 'b']
            self.assertListEqual(expected, result)

        with self.subTest('complex headers'):
            result = exporter.sort_headers(['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'a.2', 'a.1'])
            expected = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'a.1', 'a.2']
            self.assertListEqual(expected, result)

    def test_create_data_from_objects_empty_objects(self):
        otl_facility = self.set_up_facility()
        exporter = CsvExporter(settings=otl_facility.settings, class_directory='UnitTests.TestClasses.Classes')

        with self.subTest('empty list of objects'):
            with self.assertRaises(ValueError):
                list_of_objects = []
                exporter.create_data_from_objects(list_of_objects)

        with self.subTest('object in list without valid assetId'):
            with self.assertRaises(ValueError):
                list_of_objects = [AllCasesTestClass()]
                exporter.create_data_from_objects(list_of_objects)

        with self.subTest('object in list without valid assetId -> empty string'):
            with self.assertRaises(ValueError):
                list_of_objects = [AllCasesTestClass()]
                list_of_objects[0].assetId.identificator = ''
                exporter.create_data_from_objects(list_of_objects)

        with self.subTest('object in list with valid assetId -> string'):
            list_of_objects = [AllCasesTestClass()]
            list_of_objects[0].assetId.identificator = '0'
            csv_data = exporter.create_data_from_objects(list_of_objects)
            self.assertEqual('typeURI', csv_data[0][0])
            self.assertEqual('assetId.identificator', csv_data[0][1])
            self.assertEqual('assetId.toegekendDoor', csv_data[0][2])
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', csv_data[1][0])
            self.assertEqual('0', csv_data[1][1])
            self.assertEqual(None, csv_data[1][2])

    def test_create_data_from_objects_nonempty_objects_same_type(self):
        otl_facility = self.set_up_facility()
        exporter = CsvExporter(settings=otl_facility.settings, class_directory='UnitTests.TestClasses.Classes')

        list_of_objects = [AllCasesTestClass(), AllCasesTestClass()]
        list_of_objects[0].assetId.identificator = '0'
        list_of_objects[0].testDecimalField = 1.0
        list_of_objects[0].testBooleanField = True
        list_of_objects[0].testKeuzelijst = 'waarde-1'
        list_of_objects[0].testComplexType.testStringField = 'string in complex veld'
        list_of_objects[0].testComplexType.testKwantWrd.waarde = 2.0

        list_of_objects[1].assetId.identificator = '1'
        list_of_objects[1].testBooleanField = False
        list_of_objects[1].testKeuzelijstMetKard = ['waarde-2']
        list_of_objects[1].testDateField = date(2022, 2, 2)
        list_of_objects[1].testDecimalField = 2.5
        list_of_objects[1].testComplexType.testComplexType2.testStringField = 'string in complex veld binnenin complex veld'

        csv_data = exporter.create_data_from_objects(list_of_objects)

        with self.subTest('verify headers'):
            self.assertEqual('typeURI', csv_data[0][0])
            self.assertEqual('assetId.identificator', csv_data[0][1])
            self.assertEqual('assetId.toegekendDoor', csv_data[0][2])
            self.assertEqual('testBooleanField', csv_data[0][3])
            self.assertEqual('testComplexType.testComplexType2.testStringField', csv_data[0][4])
            self.assertEqual('testComplexType.testKwantWrd', csv_data[0][5])
            self.assertEqual('testComplexType.testStringField', csv_data[0][6])
            self.assertEqual('testDateField', csv_data[0][7])
            self.assertEqual('testDecimalField', csv_data[0][8])
            self.assertEqual('testKeuzelijst', csv_data[0][9])
            self.assertEqual('testKeuzelijstMetKard[]', csv_data[0][10])

        with self.subTest('verify asset 1'):
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', csv_data[1][0])
            self.assertEqual('0', csv_data[1][1])
            self.assertEqual(None, csv_data[1][2])
            self.assertEqual(True, csv_data[1][3])
            self.assertEqual(None, csv_data[1][4])
            self.assertEqual(2.0, csv_data[1][5])
            self.assertEqual('string in complex veld', csv_data[1][6])
            self.assertEqual(1.0, csv_data[1][8])
            self.assertEqual('waarde-1', csv_data[1][9])
            self.assertEqual(None, csv_data[1][10])

        with self.subTest('verify asset 2'):
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', csv_data[2][0])
            self.assertEqual('1', csv_data[2][1])
            self.assertEqual(None, csv_data[2][2])
            self.assertEqual(False, csv_data[2][3])
            self.assertEqual('string in complex veld binnenin complex veld', csv_data[2][4])
            self.assertEqual(None, csv_data[2][5])
            self.assertEqual(None, csv_data[2][6])
            self.assertEqual('2022-02-02', csv_data[2][7])
            self.assertEqual(2.5, csv_data[2][8])
            self.assertEqual(None, csv_data[2][9])
            self.assertEqual(['waarde-2'], csv_data[2][10])

    def test_create_with_different_cardinality_among_subattributes(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = CsvImporter(settings=converter.settings)
        exporter = CsvExporter(settings=converter.settings, class_directory='UnitTests.TestClasses.Classes')
        file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.csv'
        instance = AllCasesTestClass()
        instance.assetId.identificator = '0000-0000'

        instance._testComplexTypeMetKard.add_empty_value()
        instance.testComplexTypeMetKard[0].testBooleanField = False
        instance.testComplexTypeMetKard[0].testStringField = '1.1'
        instance._testComplexTypeMetKard.add_empty_value()
        instance.testComplexTypeMetKard[1].testBooleanField = True
        instance.testComplexTypeMetKard[1].testKwantWrd.waarde = 2.0
        instance.testComplexTypeMetKard[1].testStringField = '1.2'
        instance._testComplexTypeMetKard.add_empty_value()
        instance.testComplexTypeMetKard[2].testStringField = '1.3'

        exporter.export_to_file(list_of_objects=[instance], filepath=file_location,
                                split_per_type=False)

        objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
        self.assertEqual(1, len(objects))
        self.assertEqual(5, len(importer.data['AllCasesTestClass'].columns))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)
        self.assertEqual('0000-0000', instance.assetId.identificator)

        self.assertEqual(False, instance.testComplexTypeMetKard[0].testBooleanField)
        self.assertEqual(True, instance.testComplexTypeMetKard[1].testBooleanField)
        self.assertEqual(None, instance.testComplexTypeMetKard[2].testBooleanField)

        self.assertEqual(None, instance.testComplexTypeMetKard[0].testKwantWrd.waarde)
        self.assertEqual(2.0, instance.testComplexTypeMetKard[1].testKwantWrd.waarde)
        self.assertEqual(None, instance.testComplexTypeMetKard[2].testKwantWrd.waarde)

        self.assertEqual('1.1', instance.testComplexTypeMetKard[0].testStringField)
        self.assertEqual('1.2', instance.testComplexTypeMetKard[1].testStringField)
        self.assertEqual('1.3', instance.testComplexTypeMetKard[2].testStringField)

        os.unlink(file_location)

    def test_create_data_from_objects_cardinality(self):
        otl_facility = self.set_up_facility()
        exporter = CsvExporter(settings=otl_facility.settings, class_directory='UnitTests.TestClasses.Classes')

        list_of_objects = [AllCasesTestClass()]
        list_of_objects[0].assetId.identificator = '0'
        list_of_objects[0]._testComplexTypeMetKard.add_empty_value()
        list_of_objects[0].testComplexTypeMetKard[0].testStringField = '1.1'
        list_of_objects[0].testComplexTypeMetKard[0].testBooleanField = False
        list_of_objects[0]._testComplexTypeMetKard.add_empty_value()
        list_of_objects[0].testComplexTypeMetKard[1].testStringField = '1.2'
        list_of_objects[0].testComplexTypeMetKard[1].testBooleanField = True

        csv_data = exporter.create_data_from_objects(list_of_objects)

        self.assertEqual('typeURI', csv_data[0][0])
        self.assertEqual('assetId.identificator', csv_data[0][1])
        self.assertEqual('assetId.toegekendDoor', csv_data[0][2])
        self.assertEqual('testComplexTypeMetKard[].testBooleanField', csv_data[0][3])
        self.assertEqual('testComplexTypeMetKard[].testStringField', csv_data[0][4])
        self.assertEqual('0', csv_data[1][1])
        self.assertEqual(None, csv_data[1][2])
        self.assertListEqual([False, True], csv_data[1][3])
        self.assertListEqual(['1.1', '1.2'], csv_data[1][4])

    def test_create_data_from_objects_different_settings(self):
        otl_facility = self.set_up_facility()
        exporter = CsvExporter(settings=otl_facility.settings, class_directory='UnitTests.TestClasses.Classes')
        exporter.settings = {
            "name": "csv",
            "dotnotation": {
                "separator": "+",
                "cardinality separator": "$",
                "cardinality indicator": "()",
                "waarde_shortcut_applicable": True
            },
            "delimiter": ','
        }

        list_of_objects = [AllCasesTestClass(), AllCasesTestClass()]
        list_of_objects[0].assetId.identificator = '0'
        list_of_objects[0].testDecimalField = 1.0
        list_of_objects[0].testBooleanField = True
        list_of_objects[0].testKeuzelijst = 'waarde-1'
        list_of_objects[0].testComplexType.testStringField = 'string in complex veld'
        list_of_objects[0].testComplexType.testKwantWrd.waarde = 2.0

        list_of_objects[1].assetId.identificator = '1'
        list_of_objects[1].testBooleanField = False
        list_of_objects[1].testKeuzelijstMetKard = ['waarde-2', 'waarde-3']
        list_of_objects[1].testDecimalField = 2.5
        list_of_objects[1].testComplexType.testComplexType2.testStringField = 'string in complex veld binnenin complex veld'

        csv_data = exporter.create_data_from_objects(list_of_objects)

        with self.subTest('verify headers with different dotnotation settings'):
            self.assertEqual('assetId+identificator', csv_data[0][1])
            self.assertEqual('assetId+toegekendDoor', csv_data[0][2])
            self.assertEqual('testComplexType+testComplexType2+testStringField', csv_data[0][4])
            self.assertEqual('testComplexType+testKwantWrd', csv_data[0][5])
            self.assertEqual('testComplexType+testStringField', csv_data[0][6])
            self.assertEqual('testKeuzelijstMetKard()', csv_data[0][9])

        csv_data_lines = exporter.create_data_lines_from_data(csv_data, delimiter=exporter.settings['delimiter'])
        expected_line_asset_2 = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass,1,,False,string in complex veld binnenin complex veld,,,2.5,,waarde-2$waarde-3'

        with self.subTest('verify data with different settings'):
            self.assertEqual(expected_line_asset_2, csv_data_lines[2])

    # TODO refactor
    def test_create_with_different_cardinality_among_subattributes(self):
        otl_facility = self.set_up_facility()
        exporter = CsvExporter(settings=otl_facility.settings, class_directory='UnitTests.TestClasses.Classes')

        list_of_objects = [AllCasesTestClass()]
        list_of_objects[0].assetId.identificator = '0'
        list_of_objects[0]._testComplexTypeMetKard.add_empty_value()
        list_of_objects[0].testComplexTypeMetKard[0].testBooleanField = False
        list_of_objects[0].testComplexTypeMetKard[0].testStringField = '1.1'
        list_of_objects[0]._testComplexTypeMetKard.add_empty_value()
        list_of_objects[0].testComplexTypeMetKard[1].testBooleanField = True
        list_of_objects[0].testComplexTypeMetKard[1].testKwantWrd.waarde = 2.0
        list_of_objects[0].testComplexTypeMetKard[1].testStringField = '1.2'
        list_of_objects[0]._testComplexTypeMetKard.add_empty_value()
        list_of_objects[0].testComplexTypeMetKard[2].testStringField = '1.3'

        csv_data = exporter.create_data_from_objects(list_of_objects)

        self.assertEqual('testComplexTypeMetKard[].testBooleanField', csv_data[0][3])
        self.assertEqual('testComplexTypeMetKard[].testKwantWrd', csv_data[0][4])
        self.assertEqual('testComplexTypeMetKard[].testStringField', csv_data[0][5])

        self.assertListEqual([False, True, None], csv_data[1][3])
        self.assertListEqual([None, 2.0, None], csv_data[1][4])
        self.assertListEqual(['1.1', '1.2', '1.3'], csv_data[1][5])

        csv_data_lines = exporter.create_data_lines_from_data(csv_data, ';')

        expected = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass;0;;False|True|;|2.0|;1.1|1.2|1.3'
        self.assertEqual(expected, csv_data_lines[1])

    def test_export_and_then_import_unnested_attributes(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = CsvImporter(settings=converter.settings)
        exporter = CsvExporter(settings=converter.settings, class_directory='UnitTests.TestClasses.Classes')
        file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.csv'
        instance = AllCasesTestClass()
        instance.assetId.identificator = '0000'
        instance.testBooleanField = False
        instance.testDateField = date(2019, 9, 20)
        instance.testDateTimeField = datetime(2001, 12, 15, 22, 22, 15)
        instance.testDecimalField = 79.07
        instance.testDecimalFieldMetKard = [10.0, 20.0]
        instance.testEenvoudigType.waarde = 'string1'
        instance._testEenvoudigTypeMetKard.add_empty_value()
        instance._testEenvoudigTypeMetKard.add_empty_value()
        instance.testEenvoudigTypeMetKard[0].waarde = 'string1'
        instance.testEenvoudigTypeMetKard[1].waarde = 'string2'
        instance.testIntegerField = -55
        instance.testIntegerFieldMetKard = [76, 2]
        instance.testKeuzelijst = 'waarde-4'
        instance.testKeuzelijstMetKard = ['waarde-4', 'waarde-3']
        instance.testKwantWrd.waarde = 98.21
        instance._testKwantWrdMetKard.add_empty_value()
        instance._testKwantWrdMetKard.add_empty_value()
        instance.testKwantWrdMetKard[0].waarde = 10.0
        instance.testKwantWrdMetKard[1].waarde = 20.0
        instance.testStringField = 'oFfeDLp'
        instance.testStringFieldMetKard = ['string1', 'string2']
        instance.testTimeField = time(11, 5, 26)

        exporter.export_to_file(list_of_objects=[instance], filepath=file_location,
                                split_per_type=False)

        objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
        self.assertEqual(1, len(objects))
        self.assertEqual(19, len(importer.headers))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)
        self.assertEqual('0000', instance.assetId.identificator)

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

        os.unlink(file_location)
        
    def test_export_and_then_import_nested_attributes_level_1(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = CsvImporter(settings=converter.settings)
        exporter = CsvExporter(settings=converter.settings, class_directory='UnitTests.TestClasses.Classes')
        file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.csv'
        instance = AllCasesTestClass()
        instance.assetId.identificator = '0000'

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
        self.assertEqual(13, len(importer.headers))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)
        self.assertEqual('0000', instance.assetId.identificator)

        self.assertEqual('0000', instance.assetId.identificator)
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

        os.unlink(file_location)

    def test_export_and_then_import_nested_attributes_level_2(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = CsvImporter(settings=converter.settings)
        exporter = CsvExporter(settings=converter.settings, class_directory='UnitTests.TestClasses.Classes')
        file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.csv'
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
        self.assertEqual(9, len(importer.headers))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)
        self.assertEqual('0000', instance.assetId.identificator)

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

        os.unlink(file_location)

    def test_export_and_then_import_list_of_lists(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = CsvImporter(settings=converter.settings)
        exporter = CsvExporter(settings=converter.settings, class_directory='UnitTests.TestClasses.Classes')
        file_location = Path(__file__).parent / 'Testfiles' / 'export_then_import.csv'
        instance = AllCasesTestClass()
        instance.assetId.identificator = '0000'

        instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde = 10.0
        exporter.export_to_file(list_of_objects=[instance], filepath=file_location,
                                split_per_type=False)

        with self.assertLogs(level='WARNING') as log:
            objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
            self.assertEqual(len(log.output), 1)

        self.assertEqual(None, objects[0].testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde)

        os.unlink(file_location)
        




