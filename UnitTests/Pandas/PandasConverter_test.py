import os
from datetime import date, datetime, time
from pathlib import Path

import pandas as pd
from pandas import DataFrame, isna

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.FileFormats.PandasConverter import PandasConverter

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_convert_objects_to_dataframe_unnested_attributes():
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

    df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=instances)
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


def test_convert_objects_to_dataframe_minimal_test():
    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testBooleanField = False
    instances = [instance]

    df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=instances)
    assert df.shape == (1, 3)

    assert df['typeURI'][0] == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert df['assetId.identificator'][0] == '0000'
    assert df['testBooleanField'][0] == False


def test_convert_objects_to_multiple_dataframes_unnested_attributes():
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

    df_dict = PandasConverter.convert_objects_to_multiple_dataframes(sequence_of_objects=instances)

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


def test_convert_objects_to_dataframe_nested_attributes_1_level_cast_list():
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

    df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=instances, cast_list=True)
    assert df.shape == (1, 11)

    assert df['typeURI'][0] == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert df['assetId.identificator'][0] == 'YKAzZDhhdTXqkD'
    assert df['assetId.toegekendDoor'][0] == 'DGcQxwCGiBlR'
    assert df['testComplexType.testBooleanField'][0] == True
    assert df['testComplexType.testKwantWrd'][0] == 65.14
    assert df['testComplexType.testKwantWrdMetKard[]'][0] == '10.0|20.0'
    assert df['testComplexType.testStringField'][0] == 'KmCtMXM'
    assert df['testComplexType.testStringFieldMetKard[]'][0] == 'string1|string2'
    assert df['testEenvoudigType'][0] == 'string1'
    assert df['testEenvoudigTypeMetKard[]'][0] == 'string1|string2'
    assert df['testKwantWrdMetKard[]'][0] == '10.0|20.0'


def test_convert_objects_to_dataframe_nested_attributes_1_level():
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

    df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=instances)
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

    df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=instances)

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
    created_objects = PandasConverter.convert_dataframe_to_objects(dataframe=df, model_directory=model_directory_path)
    created_objects = list(created_objects)

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
    created_objects = PandasConverter.convert_dataframe_to_objects(dataframe=df, model_directory=model_directory_path)
    created_objects = list(created_objects)
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


def test_convert_dataframe_to_objects_nested_attributes_1_level_cast_list(caplog):
    columns = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'testComplexType.testBooleanField',
               'testComplexType.testKwantWrd', 'testComplexType.testKwantWrdMetKard[]',
               'testComplexType.testStringField', 'testComplexType.testStringFieldMetKard[]',
               'testComplexTypeMetKard[].testBooleanField', 'testComplexTypeMetKard[].testKwantWrd',
               'testComplexTypeMetKard[].testStringField', 'testUnionType.unionString',
               'testUnionTypeMetKard[].unionKwantWrd']

    data = [['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', '0000', 'OTLMOW',
             True, 65.14, '10.0|20.0', 'KmCtMXM', 'string1|string2', 'True|False', '10.0|20.0',
             'string1|string2', 'RWKofW', '10.0|20.0']]

    df = DataFrame(data, columns=columns)

    caplog.clear()
    created_objects = PandasConverter.convert_dataframe_to_objects(dataframe=df, model_directory=model_directory_path,
                                                                   cast_list=True)
    created_objects = list(created_objects)
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
    created_objects = PandasConverter.convert_dataframe_to_objects(dataframe=df, model_directory=model_directory_path)
    created_objects = list(created_objects)
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


def test_convert_dataframe_to_objects_nan_values(caplog):
    instance = AllCasesTestClass()
    instance.assetId.identificator = '01'
    instance.testBooleanField = True
    instance2 = AnotherTestClass()
    instance2.assetId.identificator = '02'
    instance2.notitie = 'random note'

    instances = [instance, instance2]

    df = DataFrame(PandasConverter.convert_objects_to_single_dataframe(list_of_objects=instances))
    assert df.shape == (2, 4)

    assert df['typeURI'][0] == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert df['assetId.identificator'][0] == '01'
    assert df['testBooleanField'][0]
    assert isna(df['notitie'][0])

    assert df['typeURI'][1] == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'
    assert df['assetId.identificator'][1] == '02'
    assert df['notitie'][1] == 'random note'
    assert isna(df['testBooleanField'][1])

    objects = list(PandasConverter.convert_dataframe_to_objects(dataframe=df, model_directory=model_directory_path))
    assert len(objects) == 2
    assert objects[0].typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert objects[0].assetId.identificator == '01'
    assert objects[0].testBooleanField
    assert objects[0].notitie is None

    assert objects[1].typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'
    assert objects[1].assetId.identificator == '02'
    assert objects[1].notitie == 'random note'


def test_pandas_version_compatibility():
    """Test that PandasConverter works correctly with both pandas 2 and pandas 3.
    
    This test verifies compatibility with key differences between pandas versions:
    - NaN handling: pandas 3 may produce 'nan' strings instead of None/NaN
    - Float NaN values: need to be properly detected and converted to None
    - tolist() method: used for numpy arrays in dataframes
    """
    # Get pandas version
    pandas_version = pd.__version__.split('.')[0]
    
    # Create test instances with mixed attributes
    instance = AllCasesTestClass()
    instance.assetId.identificator = 'test-id-001'
    instance.testBooleanField = True
    instance.testStringField = 'test value'
    
    instance2 = AnotherTestClass()
    instance2.assetId.identificator = 'test-id-002'
    instance2.notitie = 'a note'
    
    instances = [instance, instance2]
    
    # Test 1: Convert objects to dataframe
    df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=instances)
    assert df.shape == (2, 5)  # typeURI, assetId.identificator, testBooleanField, testStringField, notitie
    
    # Test 2: Verify NaN values are properly represented
    # In pandas 2, NaN is represented as pd.NA or np.nan
    # In pandas 3, NaN might also appear as 'nan' string in some cases
    assert isna(df['notitie'][0])  # Should be NaN/None for first instance
    assert df['notitie'][1] == 'a note'  # Should have value for second instance
    
    # Test 3: Convert back to objects - this is where pandas 2/3 differences matter most
    objects = list(PandasConverter.convert_dataframe_to_objects(
        dataframe=df, model_directory=model_directory_path))
    
    assert len(objects) == 2
    
    # Test 4: Verify NaN values are properly converted to None
    assert objects[0].notitie is None, f"Expected None, got {repr(objects[0].notitie)}"
    assert objects[0].testBooleanField is True
    assert objects[0].assetId.identificator == 'test-id-001'
    assert objects[0].testStringField == 'test value'
    
    assert objects[1].notitie == 'a note'
    assert objects[1].assetId.identificator == 'test-id-002'
    
    # Test 5: Test with explicit 'nan' string (pandas 3 compatibility)
    # This simulates what might happen in pandas 3 when converting dataframes
    df_with_nan_string = DataFrame({
        'typeURI': ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                    'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'],
        'assetId.identificator': ['id-1', 'id-2'],
        'notitie': ['nan', 'valid note'],  # 'nan' string that pandas 3 might produce
        'testBooleanField': [True, None]
    })
    
    objects_from_nan_string = list(PandasConverter.convert_dataframe_to_objects(
        dataframe=df_with_nan_string, model_directory=model_directory_path))
    
    assert len(objects_from_nan_string) == 2
    # The 'nan' string should be converted to None
    assert objects_from_nan_string[0].notitie is None, \
        f"Expected None for 'nan' string, got {repr(objects_from_nan_string[0].notitie)}"
    assert objects_from_nan_string[1].notitie == 'valid note'
    
    # Test 6: Test with float NaN values (another pandas 3 edge case)
    import math
    df_with_float_nan = DataFrame({
        'typeURI': ['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'],
        'assetId.identificator': ['id-3'],
        'notitie': [float('nan')],  # Explicit float NaN
        'testBooleanField': [False]
    })
    
    objects_from_float_nan = list(PandasConverter.convert_dataframe_to_objects(
        dataframe=df_with_float_nan, model_directory=model_directory_path))
    
    assert len(objects_from_float_nan) == 1
    assert objects_from_float_nan[0].notitie is None, \
        f"Expected None for float NaN, got {repr(objects_from_float_nan[0].notitie)}"
    
    # Test 7: Test tolist_if_possible method with numpy arrays
    import numpy as np
    np_array = np.array([1.0, 2.0, 3.0])
    result = PandasConverter.tolist_if_possible(np_array)
    assert result == [1.0, 2.0, 3.0], "tolist_if_possible should convert numpy arrays to lists"
    
    # Test 8: Test tolist_if_possible with non-array values
    assert PandasConverter.tolist_if_possible('string') == 'string'
    assert PandasConverter.tolist_if_possible(42) == 42
    assert PandasConverter.tolist_if_possible([1, 2, 3]) == [1, 2, 3]
    
    # Test 9: Round-trip conversion with multiple object types
    instance3 = AllCasesTestClass()
    instance3.assetId.identificator = 'round-trip-id'
    instance3.testIntegerField = 42
    instance3.testStringFieldMetKard = ['a', 'b', 'c']
    
    df_roundtrip = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=[instance3])
    objects_roundtrip = list(PandasConverter.convert_dataframe_to_objects(
        dataframe=df_roundtrip, model_directory=model_directory_path))
    
    assert len(objects_roundtrip) == 1
    assert objects_roundtrip[0].assetId.identificator == 'round-trip-id'
    assert objects_roundtrip[0].testIntegerField == 42
    assert objects_roundtrip[0].testStringFieldMetKard == ['a', 'b', 'c']
