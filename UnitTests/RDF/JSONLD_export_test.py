import json
import os
from datetime import date, datetime, time
from pathlib import Path

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.JsonLdExporter import JsonLdExporter


def test_export_unnested_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_unnested_attributes_generated.jsonld'

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

    recwarn.clear()
    JsonLdExporter.from_objects(sequence_of_objects=[instance], filepath=file_location)
    assert len(recwarn.list) == 0

    # read json file at file_location
    with open(file_location) as file:
        json_data = json.load(file)

    assert json_data == {'@context':
                             {"asset": "https://data.awvvlaanderen.be/id/asset/",
                              'imel': 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#',
                              'kl': 'https://wegenenverkeer.data.vlaanderen.be/id/concept/',
                              'loc': 'https://loc.data.wegenenverkeer.be/ns/implementatieelement#',
                              'onderdeel': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#'},
        '@graph': [{'@type': 'onderdeel:AllCasesTestClass',
                    '@id' : 'asset:0000-0000',
             'imel:AIMObject.typeURI': 'onderdeel:AllCasesTestClass',
             'imel:AIMObject.assetId': {'imel:DtcIdentificator.identificator': '0000-0000'},
             'loc:Locatie.geometrie': 'POINT Z (200000 200000 0)',
             'onderdeel:AllCasesTestClass.testBooleanField': False,
             'onderdeel:AllCasesTestClass.testDateField': '2019-09-20',
             'onderdeel:AllCasesTestClass.testDateTimeField': '2001-12-15 '
                                                              '22:22:15',
             'onderdeel:AllCasesTestClass.testDecimalField': 79.07,
             'onderdeel:AllCasesTestClass.testDecimalFieldMetKard': [10.0, 20.0],
             'onderdeel:AllCasesTestClass.testEenvoudigType': {'imel:DteTestEenvoudigType.waarde': 'string1'},
             'onderdeel:AllCasesTestClass.testIntegerField': -55,
             'onderdeel:AllCasesTestClass.testIntegerFieldMetKard': [76, 2],
             'onderdeel:AllCasesTestClass.testKeuzelijst': 'kl:KlTestKeuzelijst/waarde-4',
             'onderdeel:AllCasesTestClass.testKeuzelijstMetKard': ['kl:KlTestKeuzelijst/waarde-4',
                                                                   'kl:KlTestKeuzelijst/waarde-3'],
             'onderdeel:AllCasesTestClass.testKwantWrd': {'imel:KwantWrdTest.waarde': 98.21},
             'onderdeel:AllCasesTestClass.testStringField': 'oFfeDLp',
             'onderdeel:AllCasesTestClass.testStringFieldMetKard': ['string1', 'string2'],
             'onderdeel:AllCasesTestClass.testTimeField': '11:05:26'}]}

    os.unlink(file_location)


def test_export_nested_attributes_1(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_nested_attributes_1_generated.jsonld'

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000-0000'

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

    recwarn.list.clear()
    JsonLdExporter.from_objects(sequence_of_objects=[instance], filepath=file_location)
    assert len(recwarn.list) == 0

    with open(file_location) as file:
        json_data = json.load(file)

    assert json_data == {
    "@context": {
        "asset": "https://data.awvvlaanderen.be/id/asset/",
        "onderdeel": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#",
        "imel": "https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#"
    },
    "@graph": [
        {
        "@id": "asset:0000-0000",
        "@type": "onderdeel:AllCasesTestClass",
        "imel:AIMObject.assetId": {
                "imel:DtcIdentificator.identificator":  "0000-0000"
        },
        "imel:AIMObject.typeURI": "onderdeel:AllCasesTestClass",
        "onderdeel:AllCasesTestClass.testComplexType": {
            "imel:DtcTestComplexType.testBooleanField": True,
            "imel:DtcTestComplexType.testKwantWrd": {
                "imel:KwantWrdTest.waarde": 65.14
            },
            "imel:DtcTestComplexType.testKwantWrdMetKard": [
                {
                "imel:KwantWrdTest.waarde": 10.0
                },
                {
                    "imel:KwantWrdTest.waarde": 20.0
                }
            ],
            "imel:DtcTestComplexType.testStringField": "KmCtMXM",
            "imel:DtcTestComplexType.testStringFieldMetKard": [
                "string1",
                "string2"
            ]
        },
        "onderdeel:AllCasesTestClass.testComplexTypeMetKard": [
            {
                "imel:DtcTestComplexType.testBooleanField": True,
                "imel:DtcTestComplexType.testKwantWrd": {
                    "imel:KwantWrdTest.waarde": 10.0
                },
                "imel:DtcTestComplexType.testStringField": "string1"
            },
            {
                "imel:DtcTestComplexType.testBooleanField": False,
                "imel:DtcTestComplexType.testKwantWrd": {
                    "imel:KwantWrdTest.waarde": 20.0
                },
                "imel:DtcTestComplexType.testStringField": "string2"
            }
        ],
        "onderdeel:AllCasesTestClass.testEenvoudigTypeMetKard": [
            {
            "imel:DteTestEenvoudigType.waarde": "string1"
            },
            {
            "imel:DteTestEenvoudigType.waarde": "string2"
            }
        ],
        "onderdeel:AllCasesTestClass.testKwantWrdMetKard": [{
            "imel:KwantWrdTest.waarde": 10.0
            },
            {
                "imel:KwantWrdTest.waarde": 20.0
            }
        ],
        "onderdeel:AllCasesTestClass.testUnionType": {
            "imel:DtuTestUnionType.unionString": "RWKofW"
        },
        "onderdeel:AllCasesTestClass.testUnionTypeMetKard": [
            {
                "imel:DtuTestUnionType.unionKwantWrd": {
                    "imel:KwantWrdTest.waarde": 10.0
                    }
            },
            {
                "imel:DtuTestUnionType.unionKwantWrd": {
                    "imel:KwantWrdTest.waarde": 20.0
                    }
            }
            ]
        }
    ]
}

    os.unlink(file_location)


def test_export_and_then_import_nested_attributes_level_2(caplog):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_nested_attributes_2_generated.json'
    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000-0000'

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
    instance.testComplexTypeMetKard[0].testComplexType2.testKwantWrd.waarde = 30.0
    instance.testComplexTypeMetKard[1].testComplexType2.testKwantWrd.waarde = 40.0
    instance.testComplexTypeMetKard[0].testComplexType2.testStringField = 'string3'
    instance.testComplexTypeMetKard[1].testComplexType2.testStringField = 'string4'

    caplog.records.clear()
    JsonLdExporter.from_objects(sequence_of_objects=[instance], filepath=file_location)
    assert len(caplog.records) == 0

    with open(file_location) as file:
        json_data = json.load(file)

    assert json_data == {'@context': {'asset': 'https://data.awvvlaanderen.be/id/asset/',
              'imel': 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#',
              'onderdeel': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#'},
    '@graph': [{'@id': 'asset:0000-0000',
             '@type': 'onderdeel:AllCasesTestClass',
             'imel:AIMObject.assetId': {'imel:DtcIdentificator.identificator': '0000-0000'},
             'imel:AIMObject.typeURI': 'onderdeel:AllCasesTestClass',
             'onderdeel:AllCasesTestClass.testComplexType':
                 {'imel:DtcTestComplexType.testComplexType2':
                      {'imel:DtcTestComplexType2.testKwantWrd':
                           {'imel:KwantWrdTest.waarde': 76.8},
                       'imel:DtcTestComplexType2.testStringField': 'GZBzgRhOrQvfZaN'},
                 'imel:DtcTestComplexType.testComplexType2MetKard': [
                      {'imel:DtcTestComplexType2.testKwantWrd':
                           {'imel:KwantWrdTest.waarde': 10.0},
                       'imel:DtcTestComplexType2.testStringField': 'string1'},
                      {'imel:DtcTestComplexType2.testKwantWrd': {'imel:KwantWrdTest.waarde': 20.0},
                       'imel:DtcTestComplexType2.testStringField': 'string2'}]},
             'onderdeel:AllCasesTestClass.testComplexTypeMetKard': [
                 {'imel:DtcTestComplexType.testComplexType2':
                      {'imel:DtcTestComplexType2.testKwantWrd': {'imel:KwantWrdTest.waarde': 30.0},
                       'imel:DtcTestComplexType2.testStringField': 'string3'}},
                 {'imel:DtcTestComplexType.testComplexType2':
                      {'imel:DtcTestComplexType2.testKwantWrd':
                           {'imel:KwantWrdTest.waarde': 40.0},
                       'imel:DtcTestComplexType2.testStringField': 'string4'}}]}]}

    os.unlink(file_location)

