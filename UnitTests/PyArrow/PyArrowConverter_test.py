from datetime import date, datetime, time

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass

from otlmow_converter.FileFormats.PyArrowConverter import PyArrowConverter


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

    print(pa_table.to_pylist())

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
