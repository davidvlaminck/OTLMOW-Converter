import os
import unittest
from datetime import date, datetime, time
from pathlib import Path

from UnitTests.SettingManagerForUnitTests import get_settings_path_for_unittests
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestClasses.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.Exceptions.BadTypeWarning import BadTypeWarning
from otlmow_converter.FileFormats.CsvExporter import CsvExporter
from otlmow_converter.FileFormats.CsvImporter import CsvImporter
from otlmow_converter.FileFormats.TableExporter import TableExporter
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_converter.SettingsManager import load_settings


class TableExporterTests(unittest.TestCase):
    @staticmethod
    def set_up_exporter(class_dir_test_class=True):
        settings_file_location = get_settings_path_for_unittests()
        settings = load_settings(settings_file_location)
        csv_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'csv'), None)
        if class_dir_test_class:
            class_dir = 'UnitTests.TestClasses.Classes'
        else:
            class_dir = None
        return TableExporter(dotnotation_settings=csv_settings['dotnotation'], class_directory=class_dir)

    def test_init_exporter_only_load_with_settings(self):
        with self.subTest('load with correct settings'):
            exporter = self.set_up_exporter()
            self.assertIsNotNone(exporter)

        with self.subTest('load without settings'):
            with self.assertRaises(ValueError):
                TableExporter()

        with self.subTest('load with incorrect settings (attribute missing)'):
            with self.assertRaises(ValueError):
                TableExporter(dotnotation_settings={
                    "cardinality separator": "|",
                    "cardinality indicator": "[]"})

        with self.subTest('_import_aim_object otlmow_model'):
            exporter = self.set_up_exporter(class_dir_test_class=False)
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject',
                             exporter.aim_object_ref.typeURI)

        with self.subTest('_import_relatie_object otlmow_model'):
            exporter = self.set_up_exporter(class_dir_test_class=False)
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#RelatieObject',
                             exporter.relatie_object_ref.typeURI)

        with self.subTest('_import_aim_object unittestclass'):
            exporter = self.set_up_exporter()
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject',
                             exporter.aim_object_ref.typeURI)

        with self.subTest('_import_relatie_object unittestclass'):
            exporter = self.set_up_exporter()
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#RelatieObject',
                             exporter.relatie_object_ref.typeURI)

    def test_master_dict(self):
        with self.subTest('empty list'):
            exporter = self.set_up_exporter()
            exporter.fill_master_dict([])
            expected_master_dict = {}
            self.assertDictEqual(expected_master_dict, exporter.master)

        with self.subTest('list with bad object'):
            with self.assertWarns(BadTypeWarning):
                exporter = self.set_up_exporter()
                exporter.fill_master_dict([BadTypeWarning])
                expected_master_dict = {}
                self.assertDictEqual(expected_master_dict, exporter.master)

        with self.subTest('single AllCasesTestClass'):
            exporter = self.set_up_exporter()
            exporter.ignore_empty_asset_id = True
            exporter.fill_master_dict([AllCasesTestClass()])
            expected_master_dict = {'onderdeel#AllCasesTestClass': {
                'headers': ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'],
                'data': [{
                    'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                    'assetId.identificator': None, 'assetId.toegekendDoor': None
                }]
            }}
            self.assertDictEqual(expected_master_dict, exporter.master)

        with self.subTest('double AllCasesTestClass'):
            exporter = self.set_up_exporter()
            exporter.ignore_empty_asset_id = True
            exporter.fill_master_dict([AllCasesTestClass(), AllCasesTestClass()])
            expected_master_dict = {'onderdeel#AllCasesTestClass': {
                'headers': ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'],
                'data': [{
                    'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                    'assetId.identificator': None, 'assetId.toegekendDoor': None
                }, {
                    'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                    'assetId.identificator': None, 'assetId.toegekendDoor': None
                }]
            }}

            self.assertDictEqual(expected_master_dict, exporter.master)

        with self.subTest('two different classes'):
            exporter = self.set_up_exporter()
            exporter.ignore_empty_asset_id = True
            exporter.fill_master_dict([AllCasesTestClass(), AnotherTestClass()])
            expected_master_dict = {'onderdeel#AllCasesTestClass': {
                'headers': ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'],
                'data': [{
                    'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                    'assetId.identificator': None, 'assetId.toegekendDoor': None
                }]
            }, 'onderdeel#AnotherTestClass': {
                'headers': ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'],
                'data': [{
                    'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
                    'assetId.identificator': None, 'assetId.toegekendDoor': None
                }]
            }}
            self.assertDictEqual(expected_master_dict, exporter.master)

    def test_sort_headers(self):
        with self.subTest('no headers'):
            result = TableExporter.sort_headers(['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'])
            expected = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor']
            self.assertListEqual(expected, result)

        with self.subTest('2 headers'):
            result = TableExporter.sort_headers(['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'b', 'a'])
            expected = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'a', 'b']
            self.assertListEqual(expected, result)

        with self.subTest('complex headers'):
            result = TableExporter.sort_headers(
                ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'a.2', 'a.1'])
            expected = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'a.1', 'a.2']
            self.assertListEqual(expected, result)

    def test_fill_master_dict_edge_cases(self):
        with self.subTest('empty list of objects'):
            exporter = self.set_up_exporter()
            list_of_objects = []
            exporter.fill_master_dict(list_of_objects)
            self.assertEqual(len(exporter.master.items()), 0)

        with self.subTest('object in list without valid assetId'):
            exporter = self.set_up_exporter()
            with self.assertRaises(ValueError):
                list_of_objects = [AllCasesTestClass()]
                exporter.fill_master_dict(list_of_objects)

        with self.subTest('object in list without valid assetId and ignore True'):
            exporter = self.set_up_exporter()
            exporter.ignore_empty_asset_id = True
            list_of_objects = [AllCasesTestClass()]
            exporter.fill_master_dict(list_of_objects)
            tabular_data = exporter.master['onderdeel#AllCasesTestClass']
            self.assertEqual(None, tabular_data['data'][0]['assetId.identificator'])

        with self.subTest('object in list without valid assetId -> empty string'):
            exporter = self.set_up_exporter()
            with self.assertRaises(ValueError):
                list_of_objects = [AllCasesTestClass()]
                list_of_objects[0].assetId.identificator = ''
                exporter.fill_master_dict(list_of_objects)

        with self.subTest('object in list with valid assetId -> string'):
            exporter = self.set_up_exporter()
            list_of_objects = [AllCasesTestClass()]
            list_of_objects[0].assetId.identificator = '0'
            exporter.fill_master_dict(list_of_objects)
            tabular_data = exporter.master['onderdeel#AllCasesTestClass']

            self.assertEqual('typeURI', tabular_data['headers'][0])
            self.assertEqual('assetId.identificator', tabular_data['headers'][1])
            self.assertEqual('assetId.toegekendDoor', tabular_data['headers'][2])
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                             tabular_data['data'][0]['typeURI'])
            self.assertEqual('0', tabular_data['data'][0]['assetId.identificator'])
            self.assertEqual(None, tabular_data['data'][0]['assetId.toegekendDoor'])

    def test_get_data_as_table_basic_functionality(self):
        with self.subTest('no data'):
            exporter = self.set_up_exporter()
            exporter.ignore_empty_asset_id = True
            exporter.fill_master_dict([])
            with self.assertRaises(ValueError):
                exporter.get_data_as_table()

        with self.subTest('one object, no attributes'):
            exporter = self.set_up_exporter()
            list_of_objects = [AllCasesTestClass()]
            list_of_objects[0].assetId.identificator = '0'
            exporter.fill_master_dict(list_of_objects)
            table_data = exporter.get_data_as_table('onderdeel#AllCasesTestClass')
            self.assertListEqual([['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'],
                                  ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0',
                                   None]], table_data)

        with self.subTest('one object, primitive attributes in reverse order'):
            exporter = self.set_up_exporter()
            list_of_objects = [AllCasesTestClass()]
            list_of_objects[0].assetId.identificator = '0'
            list_of_objects[0].testStringField = 'test'
            list_of_objects[0].testIntegerField = 1
            exporter.fill_master_dict(list_of_objects)
            table_data = exporter.get_data_as_table('onderdeel#AllCasesTestClass')
            expected_data = [
                ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testIntegerField', 'testStringField'],
                ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0', None, '1', 'test']]
            self.assertListEqual(expected_data, table_data)

    def test_get_data_as_table_basic_nonempty_objects_same_type(self):
        exporter = self.set_up_exporter()
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

        exporter.fill_master_dict(list_of_objects)
        table_data = exporter.get_data_as_table('onderdeel#AllCasesTestClass')
        expected_data = [
            ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testBooleanField',
             'testComplexType.testKwantWrd', 'testComplexType.testStringField', 'testDateField', 'testDecimalField',
             'testKeuzelijst', 'testKeuzelijstMetKard[]'],
            ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0', None, 'True', '2.0',
             'string in complex veld', None, '1.0', 'waarde-1', None],
            ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '1', None, 'False', None, None,
             '2022-02-02', '2.5', None, 'waarde-2']]
        self.assertListEqual(expected_data, table_data)

    def test_fill_master_dict_cardinality(self):
        with self.subTest('empty list'):
            exporter = self.set_up_exporter()
            list_of_objects = [AllCasesTestClass()]
            list_of_objects[0].assetId.identificator = '0'
            list_of_objects[0].testStringFieldMetKard = []
            exporter.fill_master_dict(list_of_objects)
            self.assertListEqual([],
                                 exporter.master['onderdeel#AllCasesTestClass']['data'][0]['testStringFieldMetKard[]'])

        with self.subTest('list one element'):
            exporter = self.set_up_exporter()
            list_of_objects = [AllCasesTestClass()]
            list_of_objects[0].assetId.identificator = '0'
            list_of_objects[0].testStringFieldMetKard = ['test']
            exporter.fill_master_dict(list_of_objects)
            self.assertListEqual(['test'],
                                 exporter.master['onderdeel#AllCasesTestClass']['data'][0]['testStringFieldMetKard[]'])

        with self.subTest('list multiple elements'):
            exporter = self.set_up_exporter()
            list_of_objects = [AllCasesTestClass()]
            list_of_objects[0].assetId.identificator = '0'
            list_of_objects[0].testStringFieldMetKard = ['string1', 'string2']
            exporter.fill_master_dict(list_of_objects)
            self.assertListEqual(['string1', 'string2'],
                                 exporter.master['onderdeel#AllCasesTestClass']['data'][0]['testStringFieldMetKard[]'])

    def test_stringify_value(self):
        exporter = self.set_up_exporter()
        with self.subTest('None, values_as_strings = True'):
            self.assertIsNone(exporter._stringify_value(None))
        with self.subTest('None, values_as_strings = False'):
            self.assertIsNone(exporter._stringify_value(None, values_as_strings=False))
        with self.subTest('str, values_as_strings = True'):
            self.assertEquals('test1', exporter._stringify_value('test1'))
        with self.subTest('str, values_as_strings = False'):
            self.assertEquals('test2', exporter._stringify_value('test2', values_as_strings=False))
        with self.subTest('float, values_as_strings = True'):
            self.assertEquals('1.0', exporter._stringify_value(1.00))
        with self.subTest('float, values_as_strings = False'):
            self.assertEquals(2.0, exporter._stringify_value(2.00, values_as_strings=False))
        with self.subTest('empty list'):
            self.assertEquals(None, exporter._stringify_value([]))
        with self.subTest('list of 1 strings, values_as_strings = True'):
            self.assertEquals('1', exporter._stringify_value(['1']))
        with self.subTest('list of 2 strings, values_as_strings = True'):
            self.assertEquals('1|2', exporter._stringify_value(['1', '2']))
        with self.subTest('list of 1 strings, values_as_strings = False'):
            self.assertEquals('1', exporter._stringify_value(['1'], values_as_strings=False))
        with self.subTest('list of 2 strings, values_as_strings = False'):
            self.assertEquals('1|2', exporter._stringify_value(['1', '2'], values_as_strings=False))
        with self.subTest('list of 1 floats, values_as_strings = True'):
            self.assertEquals('1.0', exporter._stringify_value([1.00]))
        with self.subTest('list of 2 floats, values_as_strings = True'):
            self.assertEquals('1.0|2.0', exporter._stringify_value([1.00, 2.00]))
        with self.subTest('list of 1 floats, values_as_strings = False'):
            self.assertEquals('1.0', exporter._stringify_value([1.00], values_as_strings=False))
        with self.subTest('list of 2 floats, values_as_strings = False'):
            self.assertEquals('1.0|2.0', exporter._stringify_value([1.00, 2.00], values_as_strings=False))
        with self.subTest('list of list'):
            with self.assertRaises(ValueError):
                exporter._stringify_value([[]])

    def test_get_data_as_table_different_cardinality_among_subattributes(self):
        with self.subTest('empty list'):
            exporter = self.set_up_exporter()
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

            exporter.fill_master_dict([instance])
            table_data = exporter.get_data_as_table('onderdeel#AllCasesTestClass')

            expected_data = [
                ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor',
                 'testComplexTypeMetKard[].testBooleanField', 'testComplexTypeMetKard[].testKwantWrd',
                 'testComplexTypeMetKard[].testStringField'],
                ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000-0000', None,
                 'False|True|', '|2.0|', '1.1|1.2|1.3']]
            self.assertListEqual(expected_data, table_data)

    @unittest.skip
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



    @unittest.skip
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

    @unittest.skip
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

    @unittest.skip
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

    @unittest.skip
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
