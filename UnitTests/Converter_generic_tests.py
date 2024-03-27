from datetime import date
from pathlib import Path

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_converter.SettingsManager import _load_settings_by_dict, update_settings_by_dict


model_directory_path = Path(__file__).parent / 'TestModel'


def test_generic_use_of_to_dicts():
    instance1 = AllCasesTestClass()
    instance1.notitie = 'notitie'
    instance2 = AnotherTestClass()
    instance2.notitie = 'notitie2'
    sequence_of_objects = [instance1, instance2]

    dicts = OtlmowConverter.to_dicts(sequence_of_objects)
    assert list(dicts) == [{'notitie': 'notitie',
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'},
                           {'notitie': 'notitie2',
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'}]

    dicts = OtlmowConverter.to_dicts(sequence_of_objects, rdf=True)
    assert list(dicts) == [
        {'@type': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
         'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.notitie': 'notitie'},
        {'@type': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass',
         'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.notitie': 'notitie2'}]


def test_using_to_dicts_with_altered_settings():
    instance1 = AllCasesTestClass()
    instance1.testDateField = date(2020, 1, 1)
    sequence_of_objects = [instance1]

    settings = {
        "formats": {
            "OTLMOW": {
                "datetime_as_string": True
            }
        }
    }

    dicts = OtlmowConverter.to_dicts(sequence_of_objects)
    assert list(dicts) == [{'testDateField': date(2020, 1, 1),
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'}]

    update_settings_by_dict(settings)
    dicts = OtlmowConverter.to_dicts(sequence_of_objects)
    assert list(dicts) == [{'testDateField': "2020-01-01",
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'}]


def test_generic_use_of_from_dicts():
    dicts = [{'notitie': 'notitie',
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'},
                           {'notitie': 'notitie2',
                            'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'}]
    objects = OtlmowConverter.from_dicts(dicts, model_directory=model_directory_path)
    instance1 = AllCasesTestClass()
    instance1.notitie = 'notitie'
    instance2 = AnotherTestClass()
    instance2.notitie = 'notitie2'
    sequence_of_objects = [instance1, instance2]
    assert list(objects) == sequence_of_objects


def test_generic_use_of_to_file_excel():
    instance1 = AllCasesTestClass()
    instance1.notitie = 'notitie'
    instance1.assetId.identificator = 'id1'
    instance2 = AnotherTestClass()
    instance2.notitie = 'notitie2'
    instance2.assetId.identificator = 'id2'
    sequence_of_objects = [instance1, instance2]

    excel_path = Path(__file__).parent / 'test_excel.xlsx'

    OtlmowConverter.to_file(sequence_of_objects=sequence_of_objects, file_path=excel_path)
    assert excel_path.exists()

    # TODO check contents of excel file

    if excel_path.exists():
        excel_path.unlink()


def test_generic_use_of_from_file_excel():
    csv_path = Path(__file__).parent / 'CSV' / 'Testfiles' / 'import_then_export_input.csv'

    assets = list(OtlmowConverter.from_file(file_path=csv_path, model_directory=model_directory_path))
    assert len(assets) == 1
