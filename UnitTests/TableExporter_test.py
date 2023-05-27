import unittest
from datetime import date

from otlmow_model.BaseClasses.OTLObject import OTLObject

from UnitTests.SettingManagerForUnit_test import get_settings_path_for_unittests
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestClasses.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.Exceptions.BadTypeWarning import BadTypeWarning
from otlmow_converter.FileFormats.TableExporter import TableExporter
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
                    "cardinality_separator": "|",
                    "cardinality indicator": "[]"})

        with self.subTest('_import_otl_object otlmow_model'):
            exporter = self.set_up_exporter(class_dir_test_class=False)
            self.assertEqual(None,
                             exporter.otl_object_ref.typeURI)

        with self.subTest('_import_relatie_object otlmow_model'):
            exporter = self.set_up_exporter(class_dir_test_class=False)
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#RelatieObject',
                             exporter.relatie_object_ref.typeURI)

        with self.subTest('_import_otl_object unittestclass'):
            exporter = self.set_up_exporter()
            self.assertEqual(None,
                             exporter.otl_object_ref.typeURI)
            self.assertTrue(issubclass(exporter.otl_object_ref, OTLObject))

        with self.subTest('_import_relatie_object unittestclass'):
            exporter = self.set_up_exporter()
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#RelatieObject',
                             exporter.relatie_object_ref.typeURI)

    def test_master_dict_basic_functionality(self):
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

        with self.subTest('two different classes, split_per_type=False'):
            exporter = self.set_up_exporter()
            exporter.ignore_empty_asset_id = True
            list_of_objects = [AllCasesTestClass(), AnotherTestClass()]
            list_of_objects[0].assetId.identificator = '0'
            list_of_objects[1].assetId.identificator = '1'
            list_of_objects[0].testStringField = 'string1'
            list_of_objects[1].notitie = 'notitie2'

            exporter.fill_master_dict(list_of_objects, split_per_type=False)
            expected_master_dict = {'single': {
                'headers': ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testStringField', 'notitie'],
                'data': [{
                    'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                    'assetId.identificator': '0', 'assetId.toegekendDoor': None, 'testStringField': 'string1'
                }, {
                    'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
                    'assetId.identificator': '1', 'assetId.toegekendDoor': None, 'notitie': 'notitie2'
                }]
            }}
            self.assertDictEqual(expected_master_dict, exporter.master)

    def test_sort_headers(self):
        with self.subTest('no headers'):
            result = TableExporter._sort_headers(['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'])
            expected = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor']
            self.assertListEqual(expected, result)

        with self.subTest('2 headers'):
            result = TableExporter._sort_headers(['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'b', 'a'])
            expected = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'a', 'b']
            self.assertListEqual(expected, result)

        with self.subTest('complex headers'):
            result = TableExporter._sort_headers(
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
                                   '']], table_data)

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
                ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0', '', '1', 'test']]
            self.assertListEqual(expected_data, table_data)

    def test_get_data_as_table_two_different_types_split_false(self):
        exporter = self.set_up_exporter()
        exporter.ignore_empty_asset_id = True
        list_of_objects = [AllCasesTestClass(), AnotherTestClass()]
        list_of_objects[0].assetId.identificator = '0'
        list_of_objects[1].assetId.identificator = '1'
        list_of_objects[0].testStringField = 'string1'
        list_of_objects[1].notitie = 'notitie2'

        exporter.fill_master_dict(list_of_objects, split_per_type=False)
        table_data = exporter.get_data_as_table()
        expected_data = [
            ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'notitie', 'testStringField'],
            ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0', '', '', 'string1'],
            ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass', '1', '', 'notitie2', '']]
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
            ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0', '', 'True', '2.0',
             'string in complex veld', '', '1.0', 'waarde-1', ''],
            ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '1', '', 'False', '', '',
             '2022-02-02', '2.5', '', 'waarde-2']]
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
            self.assertEqual('', exporter._stringify_value(None))
        with self.subTest('None, values_as_strings = False'):
            self.assertEqual(None, exporter._stringify_value(None, values_as_strings=False))
        with self.subTest('str, values_as_strings = True'):
            self.assertEqual('test1', exporter._stringify_value('test1'))
        with self.subTest('str, values_as_strings = False'):
            self.assertEqual('test2', exporter._stringify_value('test2', values_as_strings=False))
        with self.subTest('date, values_as_strings = True'):
            self.assertEqual('2022-02-01', exporter._stringify_value(date(2022, 2, 1)))
        with self.subTest('date, values_as_strings = False'):
            self.assertEqual(date(2022, 2, 2), exporter._stringify_value(date(2022, 2, 2), values_as_strings=False))
        with self.subTest('float, values_as_strings = True'):
            self.assertEqual('1.0', exporter._stringify_value(1.00))
        with self.subTest('float, values_as_strings = False'):
            self.assertEqual(2.0, exporter._stringify_value(2.00, values_as_strings=False))
        with self.subTest('empty list'):
            self.assertEqual('', exporter._stringify_value([]))
        with self.subTest('list of 1 strings, values_as_strings = True'):
            self.assertEqual('1', exporter._stringify_value(['1']))
        with self.subTest('list of 2 strings, values_as_strings = True'):
            self.assertEqual('1|2', exporter._stringify_value(['1', '2']))
        with self.subTest('list of 1 strings, values_as_strings = False'):
            self.assertEqual('1', exporter._stringify_value(['1'], values_as_strings=False))
        with self.subTest('list of 2 strings, values_as_strings = False'):
            self.assertEqual('1|2', exporter._stringify_value(['1', '2'], values_as_strings=False))
        with self.subTest('list of 1 floats, values_as_strings = True'):
            self.assertEqual('1.0', exporter._stringify_value([1.00]))
        with self.subTest('list of 2 floats, values_as_strings = True'):
            self.assertEqual('1.0|2.0', exporter._stringify_value([1.00, 2.00]))
        with self.subTest('list of 1 floats, values_as_strings = False'):
            self.assertEqual('1.0', exporter._stringify_value([1.00], values_as_strings=False))
        with self.subTest('list of 2 floats, values_as_strings = False'):
            self.assertEqual('1.0|2.0', exporter._stringify_value([1.00, 2.00], values_as_strings=False))
        with self.subTest('list of 1 float and None, values_as_strings = False'):
            self.assertEqual('1.0|', exporter._stringify_value([1.00, None], values_as_strings=False))
        with self.subTest('list of None and 1 float, values_as_strings = False'):
            self.assertEqual('|2.0', exporter._stringify_value([None, 2.00], values_as_strings=False))
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
                ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000-0000', '',
                 'False|True|', '|2.0|', '1.1|1.2|1.3']]
            self.assertListEqual(expected_data, table_data)

    def test_get_data_as_table_different_dotnotation_settings(self):
        with self.subTest('empty list'):
            settings = {
                "separator": "+",
                "cardinality_separator": "*",
                "cardinality indicator": "()",
                "waarde_shortcut": False
            }
            exporter = TableExporter(dotnotation_settings=settings, class_directory='UnitTests.TestClasses.Classes')

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
                ['typeURI', 'assetId+identificator', 'assetId+toegekendDoor',
                 'testComplexTypeMetKard()+testBooleanField', 'testComplexTypeMetKard()+testKwantWrd+waarde',
                 'testComplexTypeMetKard()+testStringField'],
                ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000-0000', '',
                 'False*True*', '*2.0*', '1.1*1.2*1.3']]
            self.assertListEqual(expected_data, table_data)
