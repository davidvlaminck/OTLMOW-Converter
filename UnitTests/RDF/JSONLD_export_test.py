from pathlib import Path

import pytest

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Datatypes.DtcIdentificator import DtcIdentificatorWaarden
from otlmow_converter.FileFormats.JsonLdExporter import JsonLdExporter
from otlmow_converter.FileFormats.OtlAssetJSONLDEncoder import OtlAssetJSONLDEncoder
from otlmow_converter.OtlmowConverter import OtlmowConverter


def set_up_encoder():
    base_dir = Path(__file__).parent
    settings_file_location = Path(base_dir.parent / 'settings_OTLMOW.json')
    otl_facility = OtlmowConverter(settings_path=settings_file_location)
    encoder = OtlAssetJSONLDEncoder(settings=otl_facility.settings)
    return encoder


def test_create_ld_dict_from_asset_only_id():
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


def test_create_ld_dict_from_asset_ComplexTypeMetKard():
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


def test_json_encode_no_assetId():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    with pytest.raises(ValueError):
        encoder.encode(instance)


def test_json_encode_no_identificator():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.assetId = DtcIdentificatorWaarden()
    with pytest.raises(ValueError):
        encoder.encode(instance)


def test_json_encode_KwantWrd():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testKwantWrd.waarde = 1.0
    json_instance = encoder.encode(instance)
    expected = '{"@id": "https://data.awvvlaanderen.be/id/asset/0000", "@type": ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.assetId": ' '{' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator.identificator": ' \
               '"0000"}, ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.typeURI": ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKwantWrd": {' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde": 1.0}}'

    assert json_instance == expected


def test_json_encode_Keuzelijst():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testKeuzelijst = 'waarde-1'
    json_instance = encoder.encode(instance)
    expected = '{"@id": "https://data.awvvlaanderen.be/id/asset/0000", "@type": ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.assetId": ' '{' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator.identificator": ' \
               '"0000"}, ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.typeURI": ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKeuzelijst": ' \
               '"https://wegenenverkeer.data.vlaanderen.be/id/concept/KlTestKeuzelijst/waarde-1"}'

    assert json_instance == expected


def test_json_encode_KeuzelijstKard():
    encoder = set_up_encoder()

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testKeuzelijstMetKard = ['waarde-1', 'waarde-2']
    json_instance = encoder.encode(instance)
    expected = '{"@id": "https://data.awvvlaanderen.be/id/asset/0000", "@type": ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.assetId": ' '{' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator.identificator": ' \
               '"0000"}, ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.typeURI": ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", ' \
               '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKeuzelijstMetKard": ' \
               '["https://wegenenverkeer.data.vlaanderen.be/id/concept/KlTestKeuzelijst/waarde-1", ' \
               '"https://wegenenverkeer.data.vlaanderen.be/id/concept/KlTestKeuzelijst/waarde-2"]}'

    assert json_instance == expected


def test_modify_jsonld_for_context_minimal():
    test_string = '{"@graph": [{"@id": "https://data.awvvlaanderen.be/id/asset/0000", "@type": ' \
                  '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", ' \
                  '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.assetId": ' '{' \
                  '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator.identificator": ' \
                  '"0000"}, ' \
                  '"https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.typeURI": ' \
                  '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", ' \
                  '"https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKeuzelijst": ' \
                  '"https://wegenenverkeer.data.vlaanderen.be/id/concept/KlTestKeuzelijst/waarde-1"}]}'

    expected = '{"@context": {"asset": "https://data.awvvlaanderen.be/id/asset/", ' \
               '"onderdeel": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#", ' \
               '"imel": "https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#", ' \
               '"kl": "https://wegenenverkeer.data.vlaanderen.be/id/concept/"},' \
               '"@graph": [{"@id": "asset:0000", "@type": "onderdeel:AllCasesTestClass", ' \
               '"imel:AIMObject.assetId": {"imel:DtcIdentificator.identificator": "0000"}, ' \
               '"imel:AIMObject.typeURI": "onderdeel:AllCasesTestClass", ' \
               '"onderdeel:AllCasesTestClass.testKeuzelijst": "kl:KlTestKeuzelijst/waarde-1"}]}'

    result_string = JsonLdExporter.modify_jsonld_for_context(test_string)
    assert result_string == expected
