from datetime import date, datetime, time
from pathlib import Path

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass

from otlmow_converter.FileFormats.PyArrowConverter import PyArrowConverter

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_pyarrow_table_from_objects_unnested_attributes():
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

    pa_table = PyArrowConverter.convert_objects_to_single_table(list_of_objects=instances)

    print(pa_table)

    assert pa_table.num_rows == 1
    assert pa_table.num_columns == 14

    # Check some values
    assert pa_table['typeURI'][0].as_py() == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert pa_table['assetId.identificator'][0].as_py() == '0000'
    assert pa_table['testBooleanField'][0].as_py() == False
    assert pa_table['testDateField'][0].as_py() == date(2019, 9, 20)
    assert pa_table['testDateTimeField'][0].as_py() == datetime(2001, 12, 15, 22, 22, 15)
    assert pa_table['testDecimalField'][0].as_py() == 79.07
    assert pa_table['testDecimalFieldMetKard[]'][0].as_py() == [10.0, 20.0]
    assert pa_table['testIntegerField'][0].as_py() == -55
    assert pa_table['testIntegerFieldMetKard[]'][0].as_py() == [76, 2]
    assert pa_table['testKeuzelijst'][0].as_py() == 'waarde-4'
    assert pa_table['testKeuzelijstMetKard[]'][0].as_py() == ['waarde-4', 'waarde-3']
    assert pa_table['testStringField'][0].as_py() == 'oFfeDLp'
    assert pa_table['testStringFieldMetKard[]'][0].as_py() == ['string1', 'string2']
    assert pa_table['testTimeField'][0].as_py() == time(11, 5, 26)


def test_convert_objects_to_dataframe_minimal_test():
    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testBooleanField = False

    instance2 = AllCasesTestClass()
    instance2.assetId.identificator = '0001'
    instance2.testDecimalFieldMetKard = [10.0, 20.0]

    instances = [instance, instance2]

    pa_table = PyArrowConverter.convert_objects_to_single_table(list_of_objects=instances)


    assert pa_table.num_rows == 2
    assert pa_table.num_columns == 4

    assert pa_table['typeURI'][0].as_py() == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert pa_table['assetId.identificator'][0].as_py() == '0000'
    assert pa_table['testBooleanField'][0].as_py() == False
    assert pa_table['testDecimalFieldMetKard[]'][0].as_py() is None
    assert pa_table['typeURI'][1].as_py() == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert pa_table['assetId.identificator'][1].as_py() == '0001'
    assert pa_table['testBooleanField'][1].as_py() is None
    assert pa_table['testDecimalFieldMetKard[]'][1].as_py() == [10.0, 20.0]


def test_pyarrow_table_from_objects_multiple_types_unnested_attributes():
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

    pa_tables = PyArrowConverter.convert_objects_to_multiple_tables(instances)

    # Test AllCasesTestClass table
    test_class_table = pa_tables['onderdeel#AllCasesTestClass']
    assert test_class_table.num_rows == 2
    assert test_class_table['assetId.identificator'][0].as_py() == '0000'
    assert test_class_table['testStringField'][0].as_py() == 'string1'
    assert test_class_table['assetId.identificator'][1].as_py() == '0002'
    assert test_class_table['testStringField'][1].as_py() == 'string2'

    # Test AnotherTestClass table
    another_test_class_table = pa_tables['onderdeel#AnotherTestClass']
    assert another_test_class_table.num_rows == 1
    assert another_test_class_table['assetId.identificator'][0].as_py() == '0001'
    assert another_test_class_table['toestand'][0].as_py() == 'in-gebruik'

    assert set(pa_tables.keys()) == {'onderdeel#AnotherTestClass', 'onderdeel#AllCasesTestClass'}


def test_convert_table_to_objects_from_pyarrow_table():
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

    pa_table = PyArrowConverter.convert_objects_to_single_table(list_of_objects=instances)

    objects = list(PyArrowConverter.convert_table_to_objects(pa_table, model_directory=model_directory_path))
    assert len(objects) == 1
    obj = objects[0]

    # Check that all attributes are correctly restored
    assert obj.assetId.identificator == '0000'
    assert obj.testBooleanField is False
    assert obj.testDateField == date(2019, 9, 20)
    assert obj.testDateTimeField == datetime(2001, 12, 15, 22, 22, 15)
    assert obj.testDecimalField == 79.07
    assert obj.testDecimalFieldMetKard == [10.0, 20.0]
    assert obj.testIntegerField == -55
    assert obj.testIntegerFieldMetKard == [76, 2]
    assert obj.testKeuzelijst == 'waarde-4'
    assert obj.testKeuzelijstMetKard == ['waarde-4', 'waarde-3']
    assert obj.testStringField == 'oFfeDLp'
    assert obj.testStringFieldMetKard == ['string1', 'string2']
    assert obj.testTimeField == time(11, 5, 26)
    assert obj.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'


def test_convert_table_to_objects_from_pyarrow_table_nested_1_level():
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

    pa_table = PyArrowConverter.convert_objects_to_single_table(list_of_objects=instances)

    objects = list(PyArrowConverter.convert_table_to_objects(pa_table, model_directory=model_directory_path))
    assert len(objects) == 1
    obj = objects[0]

    assert obj.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert obj.assetId.identificator == 'YKAzZDhhdTXqkD'
    assert obj.assetId.toegekendDoor == 'DGcQxwCGiBlR'
    assert obj.testComplexType.testBooleanField
    assert obj.testComplexType.testKwantWrd.waarde == 65.14
    assert obj.testComplexType.testKwantWrdMetKard[0].waarde == 10.0
    assert obj.testComplexType.testKwantWrdMetKard[1].waarde == 20.0
    assert obj.testComplexType.testStringField == 'KmCtMXM'
    assert obj.testComplexType.testStringFieldMetKard == ['string1', 'string2']
    assert obj.testEenvoudigType.waarde == 'string1'
    assert obj.testEenvoudigTypeMetKard[0].waarde == 'string1'
    assert obj.testEenvoudigTypeMetKard[1].waarde == 'string2'
    assert obj.testKwantWrdMetKard[0].waarde == 10.0
    assert obj.testKwantWrdMetKard[1].waarde == 20.0


def test_convert_table_to_objects_from_pyarrow_table_nested_2_levels():
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

    pa_table = PyArrowConverter.convert_objects_to_single_table(list_of_objects=instances)

    objects = list(PyArrowConverter.convert_table_to_objects(pa_table, model_directory=model_directory_path))
    assert len(objects) == 1
    obj = objects[0]

    assert obj.assetId.identificator == '0000'
    assert obj.testComplexType.testComplexType2.testKwantWrd.waarde == 76.8
    assert obj.testComplexType.testComplexType2.testStringField == 'GZBzgRhOrQvfZaN'
    assert obj.testComplexType.testComplexType2MetKard[0].testKwantWrd.waarde == 10.0
    assert obj.testComplexType.testComplexType2MetKard[1].testKwantWrd.waarde == 20.0
    assert obj.testComplexType.testComplexType2MetKard[0].testStringField == 'string1'
    assert obj.testComplexType.testComplexType2MetKard[1].testStringField == 'string2'
    assert obj.testComplexTypeMetKard[0].testComplexType2.testKwantWrd.waarde == 10.0
    assert obj.testComplexTypeMetKard[1].testComplexType2.testKwantWrd.waarde == 20.0
    assert obj.testComplexTypeMetKard[0].testComplexType2.testStringField == 'string1'
    assert obj.testComplexTypeMetKard[1].testComplexType2.testStringField == 'string2'
