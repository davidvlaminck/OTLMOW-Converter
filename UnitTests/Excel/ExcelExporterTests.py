import datetime
import logging
import os
import unittest
from pathlib import Path

import numpy
import pandas
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

    def test_objects_to_dataframedict_empty_list(self):
        otl_converter = self.set_up_converter()
        exporter = ExcelExporter(settings=otl_converter.settings)
        exporter.create_dataframe_dict_from_objects([])
        self.assertDictEqual({}, exporter.data)

    def test_objects_to_dataframe_dict_relation_object(self):
        otl_converter = self.set_up_converter()
        exporter = ExcelExporter(settings=otl_converter.settings)
        list_of_objects = [Voedt()]
        exporter.create_dataframe_dict_from_objects(list_of_objects)
        data = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Voedt', None]]
        df = DataFrame(data, columns=['typeURI', 'assetId.identificator'])
        self.assertTrue('Voedt' in exporter.data)
        self.assertEqual(df.iloc[0].tolist(), exporter.data['Voedt'].iloc[0].tolist())

    def test_objects_to_dataframe_dict_2_relation_objects(self):
        otl_converter = self.set_up_converter()
        exporter = ExcelExporter(settings=otl_converter.settings)
        list_of_objects = [Voedt(), Voedt()]
        list_of_objects[0].isActief = True
        exporter.create_dataframe_dict_from_objects(list_of_objects)
        data = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Voedt', None, True],
                ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Voedt', None, None]]
        df = DataFrame(data, columns=['typeURI', 'assetId.identificator', 'isActief'])
        self.assertTrue('Voedt' in exporter.data)
        self.assertEqual(df.iloc[0].tolist(), exporter.data['Voedt'].iloc[0].tolist())
        self.assertEqual(df.iloc[1].tolist(), exporter.data['Voedt'].iloc[1].tolist())

    def test_objects_to_dataframe_dict_2_relation_objects_diff_types(self):
        otl_converter = self.set_up_converter()
        exporter = ExcelExporter(settings=otl_converter.settings)
        list_of_objects = [Voedt(), Bevestiging(), Bevestiging()]
        list_of_objects[0].isActief = True
        list_of_objects[1].isActief = True
        exporter.create_dataframe_dict_from_objects(list_of_objects)
        data_voeding = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Voedt', None, True]]
        df_voeding = DataFrame(data_voeding,
                               columns=['typeURI', 'assetId.identificator', 'isActief'])
        data_bevestiging = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', None, True],
                            ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', None, None]]
        df_bevestiging = DataFrame(data_bevestiging,
                                   columns=['typeURI', 'assetId.identificator', 'isActief'])
        self.assertTrue('Voedt' in exporter.data)
        self.assertTrue('Bevestiging' in exporter.data)
        self.assertEqual(df_voeding.iloc[0].tolist(), exporter.data['Voedt'].iloc[0].tolist())
        self.assertEqual(df_bevestiging.iloc[0].tolist(), exporter.data['Bevestiging'].iloc[0].tolist())
        self.assertEqual(df_bevestiging.iloc[1].tolist(), exporter.data['Bevestiging'].iloc[1].tolist())

    def test_import_and_export_file(self):
        otl_converter = self.set_up_converter()
        
        importer = ExcelImporter(settings=otl_converter.settings)
        import_file_location = Path(ROOT_DIR) / 'test_file_VR.xlsx'
        objects = importer.import_file(import_file_location)
        
        exporter = ExcelExporter(settings=otl_converter.settings)
        export_file_location = Path(ROOT_DIR) / 'test_file_VR_output.xlsx'
        if os.path.isfile(export_file_location):
            os.remove(export_file_location)
        exporter.export_to_file(list_of_objects=objects, filepath=export_file_location)
        
        self.assertTrue(os.path.isfile(export_file_location))
        self.assertTrue(self.verify_excel_files_are_equal(import_file_location, export_file_location))

    @unittest.skip
    def test_sort_headers(self):
        pass

    @unittest.skip
    def test_create_data_from_objects_cardinality(self):
        pass

    @unittest.skip
    def test_create_data_from_objects_different_settings(self):
        otl_converter = self.set_up_converter()
        exporter = ExcelExporter(settings=otl_converter.settings, class_directory='UnitTests.TestClasses.Classes')
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

        pass

    @unittest.skip
    def test_create_with_different_cardinality_among_subattributes(self):
        otl_converter = self.set_up_converter()
        exporter = ExcelExporter(settings=otl_converter.settings, class_directory='UnitTests.TestClasses.Classes')

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

    def verify_excel_files_are_equal(self, file1_location, file2_location):
        df_dict1 = pandas.read_excel(file1_location, sheet_name=None)
        df_dict2 = pandas.read_excel(file2_location, sheet_name=None)
        keys = set(df_dict1.keys())
        keys.union(set(df_dict2.keys()))
        for k in keys:
            df1 = df_dict1[k]
            df2 = df_dict2[k]
            if not df1.equals(df2):
                print(f'found difference in sheet: {k}')
                return False
            comparison_values = df1.values == df2.values
            if isinstance(comparison_values, bool):
                if not comparison_values:
                    print(f'found difference in sheet: {k}')
                    return False
            elif len(comparison_values) == 1:
                cols = list(filter(lambda x: not x, comparison_values[0]))
                if len(cols) != 0:
                    print(f'found difference in sheet: {k}')
                    return False
            else:
                rows, cols = numpy.where(comparison_values == False)
                if len(rows) != 0 or len(cols) != 0:
                    print(f'found difference in sheet: {k}')
                    return False
        return True
