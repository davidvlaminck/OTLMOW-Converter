import os
import unittest
from datetime import date, datetime, time
from pathlib import Path

import pytest
from pandas import DataFrame

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.FileFormats.PandasConverter import PandasConverter
from otlmow_converter.OtlmowConverter import OtlmowConverter

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_init_importer_only_load_with_settings(subtests):
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)

    with subtests.test(msg='load with correct settings'):
        importer = PandasConverter(settings=converter.settings)
        assert importer is not None

    with subtests.test(msg='load without settings'):
        with pytest.raises(ValueError):
            PandasConverter(settings=None)

    with subtests.test(msg='load with incorrect settings (no file_formats)'):
        with pytest.raises(ValueError):
            PandasConverter(settings={"auth_options": [{}]})

    with subtests.test(msg='load with incorrect settings (file_formats but no xls)'):
        with pytest.raises(ValueError):
            PandasConverter(settings={"file_formats": [{}]})


def test_convert_objects_to_dataframe_unnested_attributes():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    converter = PandasConverter(settings=converter.settings)

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testBooleanField = False
    instance.testDateField = date(2019, 9, 20)
    instance.testDateTimeField = datetime(2001, 12, 15, 22, 22, 15)
    instance.testDecimalField = 79.07
    instance.testDecimalFieldMetKard = [10.0, 20.0]
    instance.testIntegerField = -55
    instance.testIntegerFieldMetKard = [76, 2]
    instance.testKeuzelijst = 'waarde-4'
    instance.testKeuzelijstMetKard = ['waarde-4', 'waarde-3']
    instance.testStringField = 'oFfeDLp'
    instance.testStringFieldMetKard = ['string1', 'string2']
    instance.testTimeField = time(11, 5, 26)
    instances = [instance]

    df = converter.convert_objects_to_single_dataframe(list_of_objects=instances)
    assert df.shape == (1, 14)

    assert df['typeURI'][0] == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert df['assetId.identificator'][0] == '0000'
    assert df['testBooleanField'][0] == False
    assert df['testDateField'][0] == date(2019, 9, 20)
    assert df['testDateTimeField'][0] == datetime(2001, 12, 15, 22, 22, 15)
    assert df['testDecimalField'][0] == 79.07
    assert df['testDecimalFieldMetKard[]'][0] == [10.0, 20.0]
    assert df['testIntegerField'][0] == -55
    assert df['testIntegerFieldMetKard[]'][0] == [76, 2]
    assert df['testKeuzelijst'][0] == 'waarde-4'
    assert df['testKeuzelijstMetKard[]'][0] == ['waarde-4', 'waarde-3']
    assert df['testStringField'][0] == 'oFfeDLp'
    assert df['testStringFieldMetKard[]'][0] == ['string1', 'string2']
    assert df['testTimeField'][0] == time(11, 5, 26)




def test_convert_objects_to_dataframe_unnested_attributes():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = PandasConverter()

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testBooleanField = False
    instances = [instance]

    df = converter.convert_objects_to_single_dataframe(list_of_objects=instances)
    assert df.shape == (1, 3)

    assert df['typeURI'][0] == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert df['assetId.identificator'][0] == '0000'
    assert df['testBooleanField'][0] == False



def test_convert_objects_to_multiple_dataframes_unnested_attributes():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    converter = PandasConverter(settings=converter.settings)

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testStringField = 'string1'

    instance_2 = AnotherTestClass()
    instance_2.assetId.identificator = '0001'
    instance_2.toestand = 'in-gebruik'

    instance_3 = AllCasesTestClass()
    instance_3.assetId.identificator = '0002'
    instance_3.testStringField = 'string2'

    instances = [instance, instance_2, instance_3]

    df_dict = converter.convert_objects_to_multiple_dataframes(list_of_objects=instances)

    test_class_df = df_dict['onderdeel#AllCasesTestClass']
    assert test_class_df.shape == (2, 3)
    assert test_class_df['assetId.identificator'][0] == '0000'
    assert test_class_df['testStringField'][0] == 'string1'
    assert test_class_df['assetId.identificator'][1] == '0002'
    assert test_class_df['testStringField'][1] == 'string2'

    another_test_class_df = df_dict['onderdeel#AnotherTestClass']
    assert another_test_class_df.shape == (1, 3)
    assert another_test_class_df['assetId.identificator'][0] == '0001'

    assert list(df_dict.keys()) == ['onderdeel#AllCasesTestClass', 'onderdeel#AnotherTestClass']


def test_convert_objects_to_dataframe_nested_attributes_1_level():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    converter = PandasConverter(settings=converter.settings)

    instance = AllCasesTestClass()
    instance.assetId.identificator = 'YKAzZDhhdTXqkD'
    instance.assetId.toegekendDoor = 'DGcQxwCGiBlR'
    instance.testComplexType.testBooleanField = True
    instance.testComplexType.testKwantWrd.waarde = 65.14
    instance.testComplexType.testKwantWrdMetKard[0].waarde = 10.0
    instance.testComplexType._testKwantWrdMetKard.add_empty_value()
    instance.testComplexType.testKwantWrdMetKard[1].waarde = 20.0
    instance.testComplexType.testStringField = 'KmCtMXM'
    instance.testComplexType.testStringFieldMetKard = ['string1', 'string2']
    instance.testEenvoudigType.waarde = 'string1'
    instance.testEenvoudigTypeMetKard[0].waarde = 'string1'
    instance._testEenvoudigTypeMetKard.add_empty_value()
    instance.testEenvoudigTypeMetKard[1].waarde = 'string2'
    instance.testKwantWrdMetKard[0].waarde = 10.0
    instance._testKwantWrdMetKard.add_empty_value()
    instance.testKwantWrdMetKard[1].waarde = 20.0
    instances = [instance]

    df = converter.convert_objects_to_single_dataframe(list_of_objects=instances)
    assert df.shape == (1, 11)

    assert df['typeURI'][0] == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert df['assetId.identificator'][0] == 'YKAzZDhhdTXqkD'
    assert df['assetId.toegekendDoor'][0] == 'DGcQxwCGiBlR'
    assert df['testComplexType.testBooleanField'][0] == True
    assert df['testComplexType.testKwantWrd'][0] == 65.14
    assert df['testComplexType.testKwantWrdMetKard[]'][0] == [10.0, 20.0]
    assert df['testComplexType.testStringField'][0] == 'KmCtMXM'
    assert df['testComplexType.testStringFieldMetKard[]'][0] == ['string1', 'string2']
    assert df['testEenvoudigType'][0] == 'string1'
    assert df['testEenvoudigTypeMetKard[]'][0] == ['string1', 'string2']
    assert df['testKwantWrdMetKard[]'][0] == [10.0, 20.0]


def test_convert_objects_to_dataframe_nested_attributes_2_levels():
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    converter = PandasConverter(settings=converter.settings)

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

    instances = [instance]

    df = converter.convert_objects_to_single_dataframe(list_of_objects=instances)

    assert df.shape == (1, 8)
    assert df['typeURI'][0] == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert df['assetId.identificator'][0] == '0000'

    assert df['testComplexType.testComplexType2.testKwantWrd'][0] == 76.8
    assert df['testComplexType.testComplexType2.testStringField'][0] == 'GZBzgRhOrQvfZaN'
    assert df['testComplexType.testComplexType2MetKard[].testKwantWrd'][0] == [10.0, 20.0]
    assert df['testComplexType.testComplexType2MetKard[].testStringField'][0] == ['string1', 'string2']
    assert df['testComplexTypeMetKard[].testComplexType2.testKwantWrd'][0] == [10.0, 20.0]
    assert df['testComplexTypeMetKard[].testComplexType2.testStringField'][0] == ['string1', 'string2']


def test_convert_dataframe_to_objects_unnested_attributes(caplog):
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    converter = PandasConverter(settings=converter.settings)

    columns = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testBooleanField',
               'testDateField', 'testDateTimeField', 'testDecimalField', 'testDecimalFieldMetKard[]',
               'testEenvoudigType', 'testEenvoudigTypeMetKard[]', 'testIntegerField',
               'testIntegerFieldMetKard[]', 'testKeuzelijst', 'testKeuzelijstMetKard[]',
               'testKwantWrd', 'testKwantWrdMetKard[]', 'testStringField', 'testStringFieldMetKard[]',
               'testTimeField']

    data = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000', None, False,
             date(2019, 9, 20), datetime(2001, 12, 15, 22, 22, 15),
             79.07, [10.0, 20.0], 'string1', ['string1', 'string2'], -55,
             [76, 2], 'waarde-4', ['waarde-4', 'waarde-3'], 98.21, [10.0, 20.0], 'oFfeDLp', ['string1', 'string2'],
             time(11, 5, 26)]]

    df = DataFrame(data, columns=columns)

    caplog.clear()
    created_objects = converter.convert_dataframe_to_objects(dataframe=df, model_directory=model_directory_path)
    for record in caplog.records:
        print(record.message)
    assert len(caplog.records) == 0

    assert len(created_objects) == 1

    instance = created_objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert not instance.testBooleanField
    assert instance.assetId.identificator == '0000'
    assert instance.testDateField == date(2019, 9, 20)
    assert instance.testDateTimeField == datetime(2001, 12, 15, 22, 22, 15)
    assert instance.testDecimalField == 79.07
    assert instance.testDecimalFieldMetKard == [10.0, 20.0]
    assert instance.testIntegerField == -55
    assert instance.testIntegerFieldMetKard == [76, 2]
    assert instance.testKeuzelijst == 'waarde-4'
    assert instance.testKeuzelijstMetKard == ['waarde-4', 'waarde-3']
    assert instance.testStringField == 'oFfeDLp'
    assert instance.testStringFieldMetKard == ['string1', 'string2']
    assert instance.testTimeField == time(11, 5, 26)


def test_convert_dataframe_to_objects_nested_attributes_1_level(caplog):
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    converter = PandasConverter(settings=converter.settings)

    columns = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testComplexType.testBooleanField',
               'testComplexType.testKwantWrd', 'testComplexType.testKwantWrdMetKard[]',
               'testComplexType.testStringField', 'testComplexType.testStringFieldMetKard[]',
               'testComplexTypeMetKard[].testBooleanField', 'testComplexTypeMetKard[].testKwantWrd',
               'testComplexTypeMetKard[].testStringField', 'testUnionType.unionString',
               'testUnionTypeMetKard[].unionKwantWrd']

    data = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000', 'OTLMOW',
             True, 65.14, [10.0, 20.0], 'KmCtMXM', ['string1', 'string2'], [True, False], [10.0, 20.0],
             ['string1', 'string2'], 'RWKofW', [10.0, 20.0]]]

    df = DataFrame(data, columns=columns)

    caplog.clear()
    created_objects = converter.convert_dataframe_to_objects(dataframe=df, model_directory=model_directory_path)
    assert len(caplog.records) == 0

    assert len(created_objects) == 1

    instance = created_objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == '0000'
    assert instance.assetId.toegekendDoor == 'OTLMOW'
    assert instance.testComplexType.testBooleanField
    assert instance.testComplexType.testKwantWrd.waarde == 65.14
    assert instance.testComplexType.testKwantWrdMetKard[0].waarde == 10.0
    assert instance.testComplexType.testKwantWrdMetKard[1].waarde == 20.0
    assert instance.testComplexType.testStringField == 'KmCtMXM'
    assert instance.testComplexType.testStringFieldMetKard == ['string1', 'string2']
    assert instance.testComplexTypeMetKard[0].testBooleanField == True
    assert instance.testComplexTypeMetKard[1].testBooleanField == False
    assert instance.testComplexTypeMetKard[0].testKwantWrd.waarde == 10.0
    assert instance.testComplexTypeMetKard[1].testKwantWrd.waarde == 20.0
    assert instance.testComplexTypeMetKard[0].testStringField == 'string1'
    assert instance.testComplexTypeMetKard[1].testStringField == 'string2'
    assert instance.testUnionType.unionString == 'RWKofW'
    assert instance.testUnionTypeMetKard[0].unionKwantWrd.waarde == 10.0
    assert instance.testUnionTypeMetKard[1].unionKwantWrd.waarde == 20.0


def test_convert_dataframe_to_objects_nested_attributes_2_level(caplog):
    settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
    converter = OtlmowConverter(settings_path=settings_file_location)
    converter = PandasConverter(settings=converter.settings)

    columns = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor',
               'testComplexType.testComplexType2.testKwantWrd',
               'testComplexType.testComplexType2.testStringField',
               'testComplexType.testComplexType2MetKard[].testKwantWrd',
               'testComplexType.testComplexType2MetKard[].testStringField',
               'testComplexTypeMetKard[].testComplexType2.testKwantWrd',
               'testComplexTypeMetKard[].testComplexType2.testStringField']

    data = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000', '',
             76.8, 'GZBzgRhOrQvfZaN', [10.0, 20.0], ['string1', 'string2'], [10.0, 20.0], ['string1', 'string2']]]
    df = DataFrame(data, columns=columns)

    caplog.clear()
    created_objects = converter.convert_dataframe_to_objects(dataframe=df, model_directory=model_directory_path)
    assert len(caplog.records) == 0

    assert len(created_objects) == 1

    instance = created_objects[0]
    assert instance.assetId.identificator == '0000'
    assert instance.testComplexType.testComplexType2.testKwantWrd.waarde == 76.8
    assert instance.testComplexType.testComplexType2.testStringField == 'GZBzgRhOrQvfZaN'
    assert instance.testComplexType.testComplexType2MetKard[0].testKwantWrd.waarde == 10.0
    assert instance.testComplexType.testComplexType2MetKard[1].testKwantWrd.waarde == 20.0
    assert instance.testComplexType.testComplexType2MetKard[0].testStringField == 'string1'
    assert instance.testComplexType.testComplexType2MetKard[1].testStringField == 'string2'
    assert instance.testComplexTypeMetKard[0].testComplexType2.testKwantWrd.waarde == 10.0
    assert instance.testComplexTypeMetKard[1].testComplexType2.testKwantWrd.waarde == 20.0
    assert instance.testComplexTypeMetKard[0].testComplexType2.testStringField == 'string1'
    assert instance.testComplexTypeMetKard[1].testComplexType2.testStringField == 'string2'
