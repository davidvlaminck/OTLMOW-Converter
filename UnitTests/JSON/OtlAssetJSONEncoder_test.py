from datetime import datetime, date, time
from pathlib import Path

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.OtlAssetJSONEncoder import OtlAssetJSONEncoder
from otlmow_converter.OtlmowConverter import OtlmowConverter


def set_up_encoder():
    base_dir = Path(__file__).parent
    settings_file_location = Path(base_dir.parent / 'settings_OTLMOW.json')
    converter = OtlmowConverter(settings_path=settings_file_location)
    return OtlAssetJSONEncoder(settings=converter.settings)


def test_init_encoder():
    encoder = set_up_encoder()
    assert encoder is not None


def test_JsonEncode_Boolean():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.testBooleanField = True
    json_instance = encoder.encode(instance)
    expected = '{"testBooleanField": true, ' \
               '"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"}'

    assert json_instance == expected


def test_JsonEncode_Keuzelijst():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.testKeuzelijst = 'waarde-2'
    json_instance = encoder.encode(instance)
    expected = '{"testKeuzelijst": "waarde-2", ' \
               '"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"}'

    assert json_instance == expected


def test_JsonEncode_UnionType():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.testUnionType.unionString = 'union waarde'
    json_instance = encoder.encode(instance)
    expected = '{"testUnionType": {"unionString": "union waarde"}, ' \
               '"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"}'
    assert json_instance == expected

    instance.testUnionType.unionKwantWrd.waarde = 1.0
    json_instance = encoder.encode(instance)
    expected = '{"testUnionType": {"unionKwantWrd": 1.0}, ' \
               '"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"}'
    assert json_instance == expected


def test_JsonEncode_ComplexType():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.testComplexType.testStringField = 'string'
    instance.testComplexType.testBooleanField = True
    instance.testComplexType.testComplexType2.testStringField = 'string niveau 2'
    json_instance = encoder.encode(instance)
    expected = '{"testComplexType": {"testBooleanField": true, ' \
               '"testComplexType2": {"testStringField": "string niveau 2"}, ' \
               '"testStringField": "string"}, ' \
               '"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"}'

    assert json_instance == expected


def test_JsonEncode_StringMetKard():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.testStringFieldMetKard = ['a', 'b', 'c']
    json_instance = encoder.encode(instance)
    expected = '{"testStringFieldMetKard": ["a", "b", "c"], ' \
               '"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"}'

    assert json_instance == expected


def test_JsonEncode_KwantWrd():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.testKwantWrd.waarde = 1.0
    json_instance = encoder.encode(instance)
    expected = '{"testKwantWrd": 1.0, ' \
               '"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"}'

    assert json_instance == expected


def test_JsonEncode_ComplexTypeMetKard():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.testComplexTypeMetKard[0].testStringField = 'string'
    instance.testComplexTypeMetKard[0].testStringFieldMetKard = ['lijst', 'waardes']
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[1].testStringField = 'string 2'
    instance.testComplexTypeMetKard[1].testStringFieldMetKard = ['lijst2', 'waardes']
    json_instance = encoder.encode(instance)
    expected = '{"testComplexTypeMetKard": [{"testStringField": "string", ' \
               '"testStringFieldMetKard": ["lijst", "waardes"]}, ' \
               '{"testStringField": "string 2", ' \
               '"testStringFieldMetKard": ["lijst2", "waardes"]}], ' \
               '"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"}'

    assert json_instance == expected


def test_JsonEncode_DateTimeField():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.testDateTimeField = datetime(2022, 2, 2, 22, 22, 22)
    json_instance = encoder.encode(instance)
    expected = '{"testDateTimeField": "2022-02-02 22:22:22", ' \
               '"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"}'

    assert json_instance == expected


def test_JsonEncode_DateField():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.testDateField = date(2022, 2, 2)
    json_instance = encoder.encode([instance])
    expected = '[{"testDateField": "2022-02-02", ' \
               '"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"}]'

    assert json_instance == expected


def test_JsonEncode_TimeField():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.testTimeField = time(22, 22, 22)
    json_instance = encoder.encode([instance])
    expected = '[{"testTimeField": "22:22:22", ' \
               '"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"}]'

    assert json_instance == expected