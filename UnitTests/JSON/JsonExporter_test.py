import json
import os
from datetime import date, datetime, time
from pathlib import Path

import pytest

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.JsonExporter import JsonExporter

model_directory_path = Path(__file__).parent.parent / 'TestModel'

@pytest.mark.asyncio
async def test_export_and_then_import_unnested_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_unnested_attributes_generated.json'

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
    await JsonExporter.from_objects_async(sequence_of_objects=[instance], filepath=file_location)
    assert len(recwarn.list) == 0

    # read json file at file_location
    with open(file_location) as file:
        json_data = json.load(file)

    assert json_data == [{
        "assetId": {
            "identificator": "0000-0000"
        },
        "geometry": "POINT Z (200000 200000 0)",
        "testBooleanField": False,
        "testDateField": "2019-09-20",
        "testDateTimeField": "2001-12-15 22:22:15",
        "testDecimalField": 79.07,
        "testDecimalFieldMetKard": [
            10.0,
            20.0
        ],
        "testEenvoudigType": "string1",
        "testIntegerField": -55,
        "testIntegerFieldMetKard": [
            76,
            2
        ],
        "testKeuzelijst": "waarde-4",
        "testKeuzelijstMetKard": [
            "waarde-4",
            "waarde-3"
        ],
        "testKwantWrd": 98.21,
        "testStringField": "oFfeDLp",
        "testStringFieldMetKard": [
            "string1",
            "string2"
        ],
        "testTimeField": "11:05:26",
        "typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"
    }]

    os.unlink(file_location)


@pytest.mark.asyncio
async def test_export_and_then_import_nested_attributes_level_1(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_nested_attributes_1_generated.json'
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

    recwarn.list.clear()
    await JsonExporter.from_objects_async(sequence_of_objects=[instance], filepath=file_location)
    assert len(recwarn.list) == 0

    with open(file_location) as file:
        json_data = json.load(file)

    assert json_data == [{
        "assetId": {
            "identificator": "0000"
        },
        "testComplexType": {
            "testBooleanField": True,
            "testKwantWrd": 65.14,
            "testKwantWrdMetKard": [10.0, 20.0],
            "testStringField": "KmCtMXM",
            "testStringFieldMetKard": ["string1", "string2"]
        },
        "testComplexTypeMetKard": [{
            "testBooleanField": True,
            "testKwantWrd": 10.0,
            "testStringField": "string1"
        },
            {
                "testBooleanField": False,
                "testKwantWrd": 20.0,
                "testStringField": "string2"
            }],
        "testEenvoudigTypeMetKard": ["string1", "string2"],
        "testKwantWrdMetKard": [10.0, 20.0],
        "testUnionType": {"unionString": "RWKofW"},
        "testUnionTypeMetKard": [
            {"unionKwantWrd": 10.0},
            {"unionKwantWrd": 20.0}
        ],
        "typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"
    }]

    os.unlink(file_location)


@pytest.mark.asyncio()
async def test_export_and_then_import_nested_attributes_level_2(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_nested_attributes_2_generated.json'
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

    recwarn.list.clear()
    await JsonExporter.from_objects_async(sequence_of_objects=[instance], filepath=file_location)
    assert len(recwarn.list) == 0

    with open(file_location) as file:
        json_data = json.load(file)

    assert json_data == [{
        "assetId": {
            "identificator": "0000"
        },
        "testComplexType": {
            "testComplexType2": {
                "testKwantWrd": 76.8,
                "testStringField": "GZBzgRhOrQvfZaN"
            },
            "testComplexType2MetKard": [{
                "testKwantWrd": 10.0,
                "testStringField": "string1"
            }, {
                "testKwantWrd": 20.0,
                "testStringField": "string2"
            }
            ]
        },
        "testComplexTypeMetKard": [
            {
                "testComplexType2": {
                    "testKwantWrd": 10.0,
                    "testStringField": "string1"
                }
            },
            {
                "testComplexType2": {
                    "testKwantWrd": 20.0,
                    "testStringField": "string2"
                }
            }
        ],
        "typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"
    }]

    os.unlink(file_location)
