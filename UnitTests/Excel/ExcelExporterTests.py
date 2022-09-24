import datetime
import os
import unittest
from pathlib import Path

from pandas import DataFrame

from UnitTests.SettingManagerForUnitTests import get_settings_path_for_unittests
from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestClasses.Classes.Onderdeel.Bevestiging import Bevestiging
from UnitTests.TestClasses.Classes.Onderdeel.Voedt import Voedt
from otlmow_converter.FileFormats.ExcelExporter import ExcelExporter
from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
from otlmow_converter.OtlmowConverter import OtlmowConverter

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class ExcelExporterTests(unittest.TestCase):
    @staticmethod
    def set_up_facility():
        settings_file_location = get_settings_path_for_unittests()
        otl_facility = OtlmowConverter(settings_path=settings_file_location)
        return otl_facility

    def test_init_importer_only_load_with_settings(self):
        otl_facility = self.set_up_facility()

        with self.subTest('load with correct settings'):
            exporter = ExcelExporter(settings=otl_facility.settings)
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

    def test_objects_to_dataframedict_empty_list(self):
        otl_facility = self.set_up_facility()
        exporter = ExcelExporter(settings=otl_facility.settings)
        exporter.create_dataframe_dict_from_objects([])
        self.assertDictEqual({}, exporter.data)

    def test_objects_to_dataframe_dict_relation_object(self):
        otl_facility = self.set_up_facility()
        exporter = ExcelExporter(settings=otl_facility.settings)
        list_of_objects = [Voedt()]
        exporter.create_dataframe_dict_from_objects(list_of_objects)
        data = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Voedt', None, None]]
        df = DataFrame(data, columns=['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'])
        self.assertTrue('Voedt' in exporter.data)
        self.assertEqual(df.iloc[0].tolist(), exporter.data['Voedt'].iloc[0].tolist())

    def test_objects_to_dataframe_dict_2_relation_objects(self):
        otl_facility = self.set_up_facility()
        exporter = ExcelExporter(settings=otl_facility.settings)
        list_of_objects = [Voedt(), Voedt()]
        list_of_objects[0].isActief = True
        exporter.create_dataframe_dict_from_objects(list_of_objects)
        data = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Voedt', None, None, True],
                ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Voedt', None, None, None]]
        df = DataFrame(data, columns=['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'isActief'])
        self.assertTrue('Voedt' in exporter.data)
        self.assertEqual(df.iloc[0].tolist(), exporter.data['Voedt'].iloc[0].tolist())
        self.assertEqual(df.iloc[1].tolist(), exporter.data['Voedt'].iloc[1].tolist())

    def test_objects_to_dataframe_dict_2_relation_objects_diff_types(self):
        otl_facility = self.set_up_facility()
        exporter = ExcelExporter(settings=otl_facility.settings)
        list_of_objects = [Voedt(), Bevestiging(), Bevestiging()]
        list_of_objects[0].isActief = True
        list_of_objects[1].isActief = True
        exporter.create_dataframe_dict_from_objects(list_of_objects)
        data_voeding = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Voedt', None, None, True]]
        df_voeding = DataFrame(data_voeding,
                               columns=['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'isActief'])
        data_bevestiging = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', None, None, True],
                            ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', None, None, None]]
        df_bevestiging = DataFrame(data_bevestiging,
                                   columns=['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'isActief'])
        self.assertTrue('Voedt' in exporter.data)
        self.assertTrue('Bevestiging' in exporter.data)
        self.assertEqual(df_voeding.iloc[0].tolist(), exporter.data['Voedt'].iloc[0].tolist())
        self.assertEqual(df_bevestiging.iloc[0].tolist(), exporter.data['Bevestiging'].iloc[0].tolist())
        self.assertEqual(df_bevestiging.iloc[1].tolist(), exporter.data['Bevestiging'].iloc[1].tolist())

    def test_load_and_writefile(self):
        otl_facility = self.set_up_facility()
        importer = ExcelImporter(settings=otl_facility.settings)
        file_location = Path(ROOT_DIR) / 'test_file_VR.xlsx'
        objects = importer.import_file(file_location)
        exporter = ExcelExporter(settings=otl_facility.settings)
        new_file_location = Path(ROOT_DIR) / 'test_file_VR_output.xlsx'
        if os.path.isfile(new_file_location):
            os.remove(new_file_location)
        exporter.export_to_file(list_of_objects=objects, filepath=new_file_location)
        self.assertTrue(os.path.isfile(new_file_location))

        # https://kanoki.org/2019/02/26/compare-two-excel-files-for-difference-using-python/

    @unittest.skip
    def test_sort_headers(self):
        otl_facility = self.set_up_facility()
        exporter = ExcelExporter(settings=otl_facility.settings)
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

    @unittest.skip
    def test_create_data_from_objects_empty_objects(self):
        otl_facility = self.set_up_facility()
        exporter = ExcelExporter(settings=otl_facility.settings, class_directory='UnitTests.TestClasses.Classes')

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
            Excel_data = exporter.create_data_from_objects(list_of_objects)
            self.assertEqual('typeURI', Excel_data[0][0])
            self.assertEqual('assetId.identificator', Excel_data[0][1])
            self.assertEqual('assetId.toegekendDoor', Excel_data[0][2])
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                             Excel_data[1][0])
            self.assertEqual('0', Excel_data[1][1])
            self.assertEqual(None, Excel_data[1][2])

    @unittest.skip
    def test_create_data_from_objects_nonempty_objects_same_type(self):
        otl_facility = self.set_up_facility()
        exporter = ExcelExporter(settings=otl_facility.settings, class_directory='UnitTests.TestClasses.Classes')

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
        list_of_objects[1].testDateField = datetime.date(2022, 2, 2)
        list_of_objects[1].testDecimalField = 2.5
        list_of_objects[
            1].testComplexType.testComplexType2.testStringField = 'string in complex veld binnenin complex veld'

        Excel_data = exporter.create_data_from_objects(list_of_objects)

        with self.subTest('verify headers'):
            self.assertEqual('typeURI', Excel_data[0][0])
            self.assertEqual('assetId.identificator', Excel_data[0][1])
            self.assertEqual('assetId.toegekendDoor', Excel_data[0][2])
            self.assertEqual('testBooleanField', Excel_data[0][3])
            self.assertEqual('testComplexType.testComplexType2.testStringField', Excel_data[0][4])
            self.assertEqual('testComplexType.testKwantWrd', Excel_data[0][5])
            self.assertEqual('testComplexType.testStringField', Excel_data[0][6])
            self.assertEqual('testDateField', Excel_data[0][7])
            self.assertEqual('testDecimalField', Excel_data[0][8])
            self.assertEqual('testKeuzelijst', Excel_data[0][9])
            self.assertEqual('testKeuzelijstMetKard[]', Excel_data[0][10])

        with self.subTest('verify asset 1'):
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                             Excel_data[1][0])
            self.assertEqual('0', Excel_data[1][1])
            self.assertEqual(None, Excel_data[1][2])
            self.assertEqual(True, Excel_data[1][3])
            self.assertEqual(None, Excel_data[1][4])
            self.assertEqual(2.0, Excel_data[1][5])
            self.assertEqual('string in complex veld', Excel_data[1][6])
            self.assertEqual(1.0, Excel_data[1][8])
            self.assertEqual('waarde-1', Excel_data[1][9])
            self.assertEqual(None, Excel_data[1][10])

        with self.subTest('verify asset 2'):
            self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                             Excel_data[2][0])
            self.assertEqual('1', Excel_data[2][1])
            self.assertEqual(None, Excel_data[2][2])
            self.assertEqual(False, Excel_data[2][3])
            self.assertEqual('string in complex veld binnenin complex veld', Excel_data[2][4])
            self.assertEqual(None, Excel_data[2][5])
            self.assertEqual(None, Excel_data[2][6])
            self.assertEqual('2022-02-02', Excel_data[2][7])
            self.assertEqual(2.5, Excel_data[2][8])
            self.assertEqual(None, Excel_data[2][9])
            self.assertEqual(['waarde-2'], Excel_data[2][10])

    @unittest.skip
    def test_create_data_from_objects_cardinality(self):
        otl_facility = self.set_up_facility()
        exporter = ExcelExporter(settings=otl_facility.settings, class_directory='UnitTests.TestClasses.Classes')

        list_of_objects = [AllCasesTestClass()]
        list_of_objects[0].assetId.identificator = '0'
        list_of_objects[0]._testComplexTypeMetKard.add_empty_value()
        list_of_objects[0].testComplexTypeMetKard[0].testStringField = '1.1'
        list_of_objects[0].testComplexTypeMetKard[0].testBooleanField = False
        list_of_objects[0]._testComplexTypeMetKard.add_empty_value()
        list_of_objects[0].testComplexTypeMetKard[1].testStringField = '1.2'
        list_of_objects[0].testComplexTypeMetKard[1].testBooleanField = True

        Excel_data = exporter.create_data_from_objects(list_of_objects)

        self.assertEqual('typeURI', Excel_data[0][0])
        self.assertEqual('assetId.identificator', Excel_data[0][1])
        self.assertEqual('assetId.toegekendDoor', Excel_data[0][2])
        self.assertEqual('testComplexTypeMetKard[].testBooleanField', Excel_data[0][3])
        self.assertEqual('testComplexTypeMetKard[].testStringField', Excel_data[0][4])
        self.assertEqual('0', Excel_data[1][1])
        self.assertEqual(None, Excel_data[1][2])
        self.assertListEqual([False, True], Excel_data[1][3])
        self.assertListEqual(['1.1', '1.2'], Excel_data[1][4])

    @unittest.skip
    def test_create_data_from_objects_different_settings(self):
        otl_facility = self.set_up_facility()
        exporter = ExcelExporter(settings=otl_facility.settings, class_directory='UnitTests.TestClasses.Classes')
        exporter.settings = {
            "name": "Excel",
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
        list_of_objects[
            1].testComplexType.testComplexType2.testStringField = 'string in complex veld binnenin complex veld'

        Excel_data = exporter.create_data_from_objects(list_of_objects)

        with self.subTest('verify headers with different dotnotation settings'):
            self.assertEqual('assetId+identificator', Excel_data[0][1])
            self.assertEqual('assetId+toegekendDoor', Excel_data[0][2])
            self.assertEqual('testComplexType+testComplexType2+testStringField', Excel_data[0][4])
            self.assertEqual('testComplexType+testKwantWrd', Excel_data[0][5])
            self.assertEqual('testComplexType+testStringField', Excel_data[0][6])
            self.assertEqual('testKeuzelijstMetKard()', Excel_data[0][9])

        Excel_data_lines = exporter.create_data_lines_from_data(Excel_data, delimiter=exporter.settings['delimiter'])
        expected_line_asset_2 = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass,1,,False,string in complex veld binnenin complex veld,,,2.5,,waarde-2$waarde-3'

        with self.subTest('verify data with different settings'):
            self.assertEqual(expected_line_asset_2, Excel_data_lines[2])

    @unittest.skip
    def test_create_with_different_cardinality_among_subattributes(self):
        otl_facility = self.set_up_facility()
        exporter = ExcelExporter(settings=otl_facility.settings, class_directory='UnitTests.TestClasses.Classes')

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

        Excel_data = exporter.create_data_from_objects(list_of_objects)

        self.assertEqual('testComplexTypeMetKard[].testBooleanField', Excel_data[0][3])
        self.assertEqual('testComplexTypeMetKard[].testKwantWrd', Excel_data[0][4])
        self.assertEqual('testComplexTypeMetKard[].testStringField', Excel_data[0][5])

        self.assertListEqual([False, True, None], Excel_data[1][3])
        self.assertListEqual([None, 2.0, None], Excel_data[1][4])
        self.assertListEqual(['1.1', '1.2', '1.3'], Excel_data[1][5])

        Excel_data_lines = exporter.create_data_lines_from_data(Excel_data, ';')

        expected = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass;0;;False|True|;|2.0|;1.1|1.2|1.3'
        self.assertEqual(expected, Excel_data_lines[1])
