import os
from datetime import date, datetime, time
from pathlib import Path

from otlmow_model.OtlmowModel.Classes.Installatie.BeweegbareWaterkerendeConstructie import \
    BeweegbareWaterkerendeConstructie
from otlmow_model.OtlmowModel.Classes.Installatie.Bochtafbakeningsinstallatie import Bochtafbakeningsinstallatie

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.Bevestiging import Bevestiging
from otlmow_converter.FileFormats.ExcelExporter import ExcelExporter
from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_export_filled_dummy_data_all_testcasesclass(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'all_dummy_data_generated.xlsx'

    instance = AllCasesTestClass()
    instance.fill_with_dummy_data()
    instance.testComplexTypeMetKard[0].testComplexType2MetKard = None
    instance.testComplexTypeMetKard[0].testKwantWrdMetKard = None
    instance.testComplexTypeMetKard[0].testStringFieldMetKard = None
    instance.testUnionType = None
    instance.testUnionTypeMetKard = None
    ExcelExporter.from_objects(sequence_of_objects=[instance], filepath=file_location)
    warns = [w for w in recwarn.list if w.category is not DeprecationWarning] # remove deprecation warnings
    assert not warns

    data = ExcelImporter.get_data_dict_from_file_path(filepath=file_location)
    first_row = list(data['onderdeel#AllCasesTestClass'][0])

    assert first_row == ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor', 'bestekPostNummer[]',
        'datumOprichtingObject', 'geometry', 'isActief', 'notitie', 'standaardBestekPostNummer[]',
        'testBooleanField', 'testComplexType.testBooleanField',
        'testComplexType.testComplexType2.testKwantWrd', 'testComplexType.testComplexType2.testStringField',
        'testComplexType.testComplexType2MetKard[].testKwantWrd',
        'testComplexType.testComplexType2MetKard[].testStringField', 'testComplexType.testKwantWrd',
        'testComplexType.testKwantWrdMetKard[]', 'testComplexType.testStringField',
        'testComplexType.testStringFieldMetKard[]', 'testComplexTypeMetKard[].testBooleanField',
        'testComplexTypeMetKard[].testComplexType2.testKwantWrd',
        'testComplexTypeMetKard[].testComplexType2.testStringField', 'testComplexTypeMetKard[].testKwantWrd',
        'testComplexTypeMetKard[].testStringField', 'testDateField', 'testDateTimeField',
        'testDecimalField', 'testDecimalFieldMetKard[]', 'testEenvoudigType', 'testEenvoudigTypeMetKard[]',
        'testIntegerField', 'testIntegerFieldMetKard[]', 'testKeuzelijst', 'testKeuzelijstMetKard[]',
        'testKwantWrd', 'testKwantWrdMetKard[]', 'testStringField', 'testStringFieldMetKard[]',
        'testTimeField', 'theoretischeLevensduur', 'toestand']

    os.unlink(file_location)


def test_export_and_then_import_unnested_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes_generated.xlsx'
    instance = AllCasesTestClass()
    instance.geometry = 'POINT Z (200000 200000 0)'
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

    ExcelExporter.from_objects(sequence_of_objects=[instance], filepath=file_location)
    warns = [w for w in recwarn.list if w.category is not DeprecationWarning] # remove deprecation warnings
    assert not warns

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
    assert len(objects) == 1

    instanceImported = objects[0]
    assert instanceImported.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instanceImported.assetId.identificator == '0000-0000'

    assert not instanceImported.testBooleanField
    assert instanceImported.testDateField == date(2019, 9, 20)
    assert instanceImported.testDateTimeField == datetime(2001, 12, 15, 22, 22, 15)
    assert instanceImported.testDecimalField == 79.07
    assert instanceImported.testDecimalFieldMetKard == [10.0, 20.0]
    assert instanceImported.testEenvoudigType.waarde == 'string1'
    assert instanceImported.testIntegerField == -55
    assert instanceImported.testIntegerFieldMetKard == [76, 2]
    assert instanceImported.testKeuzelijst == 'waarde-4'
    assert instanceImported.testKeuzelijstMetKard == ['waarde-4', 'waarde-3']
    assert instanceImported.testKwantWrd.waarde == 98.21
    assert instanceImported.testStringField == 'oFfeDLp'
    assert instanceImported.testStringFieldMetKard[0] == 'string1'
    assert instanceImported.testStringFieldMetKard[1] == 'string2'
    assert instanceImported.testTimeField == time(11, 5, 26)
    assert instanceImported.geometry == 'POINT Z (200000 200000 0)'

    os.unlink(file_location)


def test_export_and_then_import_nested_attributes_level_1(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_nested_attributes_1_generated.xlsx'
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

    ExcelExporter.from_objects(sequence_of_objects=[instance], filepath=file_location)
    warns = [w for w in recwarn.list if w.category is not DeprecationWarning] # remove deprecation warnings
    assert not warns

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'

    assert instance.testEenvoudigTypeMetKard[0].waarde == 'string1'
    assert instance.testEenvoudigTypeMetKard[1].waarde == 'string2'
    assert instance.testKwantWrdMetKard[0].waarde == 10.0
    assert instance.testKwantWrdMetKard[1].waarde == 20.0
    assert instance.testComplexType.testBooleanField
    assert instance.testComplexType.testKwantWrd.waarde == 65.14
    assert instance.testComplexType.testKwantWrdMetKard[0].waarde == 10.0
    assert instance.testComplexType.testKwantWrdMetKard[1].waarde == 20.0
    assert instance.testComplexType.testStringField == 'KmCtMXM'
    assert instance.testComplexType.testStringFieldMetKard[0] == 'string1'
    assert instance.testComplexType.testStringFieldMetKard[1] == 'string2'
    assert instance.testComplexTypeMetKard[0].testBooleanField
    assert not instance.testComplexTypeMetKard[1].testBooleanField
    assert instance.testComplexTypeMetKard[0].testKwantWrd.waarde == 10.0
    assert instance.testComplexTypeMetKard[1].testKwantWrd.waarde == 20.0
    assert instance.testComplexTypeMetKard[0].testStringField == 'string1'
    assert instance.testComplexTypeMetKard[1].testStringField == 'string2'
    assert instance.testUnionType.unionString == 'RWKofW'
    assert instance.testUnionType.unionKwantWrd.waarde is None
    assert instance.testUnionTypeMetKard[0].unionKwantWrd.waarde == 10.0
    assert instance.testUnionTypeMetKard[1].unionKwantWrd.waarde == 20.0
    assert instance.assetId.identificator == '0000'

    os.unlink(file_location)


def test_export_and_then_import_nested_attributes_level_2(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_nested_attributes_2_generated.xlsx'
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

    ExcelExporter.from_objects(sequence_of_objects=[instance], filepath=file_location)
    warns = [w for w in recwarn.list if w.category is not DeprecationWarning] # remove deprecation warnings
    assert not warns

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
    assert len(objects) == 1
    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'

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
    assert instance.assetId.identificator == '0000'

    os.unlink(file_location)


def test_export_and_then_import_sheetname_abbreviation(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'sheetname_abbreviation_generated.xlsx'
    instance = Bevestiging()
    instance_to_be_abbreviated = Bochtafbakeningsinstallatie()
    instance_to_be_abbreviated2 = BeweegbareWaterkerendeConstructie()

    ExcelExporter.from_objects(sequence_of_objects=[instance,instance_to_be_abbreviated,instance_to_be_abbreviated2],
                               filepath=file_location,abbreviate_excel_sheettitles=True)
    warns = [w for w in recwarn.list if w.category is not DeprecationWarning] # remove deprecation warnings
    # if sheetTitle is to long it will trigger UserWarning('Title is more than 31 characters. Some applications may not be able to read the file')
    assert not warns

    # first load the objects in the template to see it the basics are there
    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
    assert len(objects) == 3

    instance_imported, instance_to_be_abbreviated_imported, instance_to_be_abbreviated2_imported = objects

    assert instance_imported.typeURI == "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging"
    assert instance_to_be_abbreviated_imported.typeURI == "https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Bochtafbakeningsinstallatie"
    assert instance_to_be_abbreviated2_imported.typeURI == "https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie"

    # second do a lower level load of the file that includs the sheet titles with ExcelImporter
    data = ExcelImporter.get_data_dict_from_file_path(filepath=file_location)

    sheet_titles = list(data.keys())
    assert len(sheet_titles) == 3

    assert sheet_titles[0] == "ond#Bevestiging"
    assert sheet_titles[1] == "ins#Bochtafbakeningsinstallatie"
    assert sheet_titles[2] == "ins#BeweegbareWaterkerendeConst" # installatie#BeweegbareWaterkerendeConstructie

    os.unlink(file_location)