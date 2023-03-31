from pathlib import Path

from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.OtlAssetJSONEncoder import OtlAssetJSONEncoder
from otlmow_converter.OtlmowConverter import OtlmowConverter


def set_up_encoder():
    base_dir = Path(__file__).parent
    settings_file_location = Path(base_dir.parent / 'settings_OTLMOW.json')
    otl_facility = OtlmowConverter(settings_path=settings_file_location)
    encoder = OtlAssetJSONEncoder(settings=otl_facility.settings)
    return encoder


def test_JsonEncode_only_id():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000-b25kZXJkZWVsI0FsbENhc2VzVGVzdENsYXNz'
    json_ld_dict = encoder.create_ld_dict_from_asset(instance)
    expected = {
        '@id': 'https://data.awvvlaanderen.be/id/asset/0000-b25kZXJkZWVsI0FsbENhc2VzVGVzdENsYXNz',
        '@type': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
        'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.assetId': {
            'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator.identificator':
                '0000-b25kZXJkZWVsI0FsbENhc2VzVGVzdENsYXNz'
        }
    }

    assert json_ld_dict == expected


def test_JsonEncode_ComplexTypeMetKard():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.toestand = 'in-gebruik'
    instance.assetId.identificator = '0000-b25kZXJkZWVsI0FsbENhc2VzVGVzdENsYXNz'
    instance.testComplexTypeMetKard[0].testStringField = 'string'
    instance.testComplexTypeMetKard[0].testStringFieldMetKard = ['lijst', 'waardes']
    instance._testComplexTypeMetKard.add_empty_value()
    instance.testComplexTypeMetKard[1].testStringField = 'string 2'
    instance.testComplexTypeMetKard[1].testStringFieldMetKard = ['lijst2', 'waardes']
    instance.testKwantWrd.waarde = 1.1
    json_ld_dict = encoder.create_ld_dict_from_asset(instance)
    expected = {
        '@id': 'https://data.awvvlaanderen.be/id/asset/0000-b25kZXJkZWVsI0FsbENhc2VzVGVzdENsYXNz',
        '@type': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
        'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMToestand.toestand':
            'https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/in-gebruik',
        'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKwantWrd': {
            'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde': 1.1
        },
        'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.assetId': {
            'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator.identificator':
                '0000-b25kZXJkZWVsI0FsbENhc2VzVGVzdENsYXNz'
        },
        'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexTypeMetKard': [{
            'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testStringField': 'string',
            'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testStringFieldMetKard':
            ['lijst', 'waardes']
        }, {
            'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testStringField': 'string 2',
            'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testStringFieldMetKard':
                ['lijst2', 'waardes']
        }]
    }

    assert json_ld_dict == expected