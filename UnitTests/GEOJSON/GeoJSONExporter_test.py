import json
import os
from datetime import time, date, datetime
from pathlib import Path

import pytest

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.FileFormats.GeoJSONExporter import GeoJSONExporter

base_dir = Path(__file__).parent
model_directory_path = Path(__file__).parent.parent / 'TestModel'


@pytest.mark.asyncio(scope="module")
async def test_export_and_then_import_unnested_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_unnested_attributes_generated.geojson'

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
    await GeoJSONExporter.from_objects_async(sequence_of_objects=[instance], filepath=file_location)
    assert len(recwarn.list) == 0

    # read json file at file_location
    with open(file_location) as file:
        json_data = json.load(file)

    assert json_data == {
        "type": "FeatureCollection",
        "features": [
            {
                "id": "0000-0000",
                "properties": {
                    "assetId.identificator": "0000-0000",
                    "testBooleanField": False,
                    "testDateField": "2019-09-20",
                    "testDateTimeField": "2001-12-15 22:22:15",
                    "testDecimalField": 79.07,
                    "testDecimalFieldMetKard[]": "10.0|20.0",
                    "testEenvoudigType": "string1",
                    "testIntegerField": -55,
                    "testIntegerFieldMetKard[]": "76|2",
                    "testKeuzelijst": "waarde-4",
                    "testKeuzelijstMetKard[]": "waarde-4|waarde-3",
                    "testKwantWrd": 98.21,
                    "testStringField": "oFfeDLp",
                    "testStringFieldMetKard[]": "string1|string2",
                    "testTimeField": "11:05:26",
                    "typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"
                },
                "type": "Feature",
                "geometry": {
                    "bbox": [
                        200000.0,
                        200000.0,
                        0.0,
                        200000.0,
                        200000.0,
                        0.0
                    ],
                    "type": "Point",
                    "coordinates": [
                        200000.0,
                        200000.0,
                        0.0
                    ],
                    "crs": {
                        "properties": {
                            "name": "EPSG:31370"
                        },
                        "type": "name"
                    }
                }
            }
        ]
    }

    os.unlink(file_location)


@pytest.mark.asyncio(scope="module")
async def test_export_and_then_read_unnested_attributes_using_dotnotaton_dicts(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_unnested_attributes_generated.geojson'

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
    dotnotation_dicts = [await DotnotationDictConverter.to_dict_async(instance, cast_list=True, cast_datetime=True)]

    await GeoJSONExporter.from_dotnotation_dicts_async(sequence_of_dotnotation_dicts=dotnotation_dicts,
                                                 filepath=file_location)
    assert len(recwarn.list) == 0

    # read json file at file_location
    with open(file_location) as file:
        json_data = json.load(file)

    assert json_data == {
        "type": "FeatureCollection",
        "features": [
            {
                "id": "0000-0000",
                "properties": {
                    "assetId.identificator": "0000-0000",
                    "testBooleanField": False,
                    "testDateField": "2019-09-20",
                    "testDateTimeField": "2001-12-15 22:22:15",
                    "testDecimalField": 79.07,
                    "testDecimalFieldMetKard[]": "10.0|20.0",
                    "testEenvoudigType": "string1",
                    "testIntegerField": -55,
                    "testIntegerFieldMetKard[]": "76|2",
                    "testKeuzelijst": "waarde-4",
                    "testKeuzelijstMetKard[]": "waarde-4|waarde-3",
                    "testKwantWrd": 98.21,
                    "testStringField": "oFfeDLp",
                    "testStringFieldMetKard[]": "string1|string2",
                    "testTimeField": "11:05:26",
                    "typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass"
                },
                "type": "Feature",
                "geometry": {
                    "bbox": [
                        200000.0,
                        200000.0,
                        0.0,
                        200000.0,
                        200000.0,
                        0.0
                    ],
                    "type": "Point",
                    "coordinates": [
                        200000.0,
                        200000.0,
                        0.0
                    ],
                    "crs": {
                        "properties": {
                            "name": "EPSG:31370"
                        },
                        "type": "name"
                    }
                }
            }
        ]
    }

    os.unlink(file_location)


@pytest.mark.asyncio(scope="module")
async def test_export_and_then_import_nested_attributes_level_1(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_nested_attributes_1_generated.geojson'

    instance = AllCasesTestClass()
    instance.geometry = 'POINT Z (200000 200000 0)'
    instance.assetId.identificator = '0000'

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

    recwarn.clear()
    await GeoJSONExporter.from_objects_async(sequence_of_objects=[instance], filepath=file_location)
    assert len(recwarn.list) == 0

    # read json file at file_location
    with open(file_location) as file:
        json_data = json.load(file)

    assert json_data == {'features': [{'geometry': {'bbox': [200000.0,
                                     200000.0,
                                     0.0,
                                     200000.0,
                                     200000.0,
                                     0.0],
                            'coordinates': [200000.0, 200000.0, 0.0],
                            'crs': {'properties': {'name': 'EPSG:31370'},
                                    'type': 'name'},
                            'type': 'Point'},
               'id': '0000',
               'properties': {'assetId.identificator': '0000',
                              'testComplexType.testBooleanField': True,
                              'testComplexType.testKwantWrd': 65.14,
                              'testComplexType.testKwantWrdMetKard[]': '10.0|20.0',
                              'testComplexType.testStringField': 'KmCtMXM',
                              'testComplexType.testStringFieldMetKard[]': 'string1|string2',
                              'testComplexTypeMetKard[].testBooleanField': 'True|False',
                              'testComplexTypeMetKard[].testKwantWrd': '10.0|20.0',
                              'testComplexTypeMetKard[].testStringField': 'string1|string2',
                              'testUnionType.unionString': 'RWKofW',
                              'testUnionTypeMetKard[].unionKwantWrd': '10.0|20.0',
                              'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'},
               'type': 'Feature'}],
    'type': 'FeatureCollection'}

    os.unlink(file_location)


def test_export_and_then_import_nested_attributes_level_2(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'export_nested_attributes_2_generated.geojson'

    instance = AllCasesTestClass()
    instance.geometry = 'POINT Z (200000 200000 0)'
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

    recwarn.clear()
    GeoJSONExporter.from_objects(sequence_of_objects=[instance], filepath=file_location)
    assert len(recwarn.list) == 0

    # read json file at file_location
    with open(file_location) as file:
        json_data = json.load(file)

    assert json_data == {'features': [{'geometry': {'bbox': [200000.0,
                                     200000.0,
                                     0.0,
                                     200000.0,
                                     200000.0,
                                     0.0],
                            'coordinates': [200000.0, 200000.0, 0.0],
                            'crs': {'properties': {'name': 'EPSG:31370'},
                                    'type': 'name'},
                            'type': 'Point'},
               'id': '0000',
               'properties': {'assetId.identificator': '0000',
                              'testComplexType.testComplexType2.testKwantWrd': 76.8,
                              'testComplexType.testComplexType2.testStringField': 'GZBzgRhOrQvfZaN',
                              'testComplexType.testComplexType2MetKard[].testKwantWrd': '10.0|20.0',
                              'testComplexType.testComplexType2MetKard[].testStringField': 'string1|string2',
                              'testComplexTypeMetKard[].testComplexType2.testKwantWrd': '10.0|20.0',
                              'testComplexTypeMetKard[].testComplexType2.testStringField': 'string1|string2',
                              'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'},
               'type': 'Feature'}],
    'type': 'FeatureCollection'}

    os.unlink(file_location)


def test_convert_wkt_string_to_geojson_line():
    line = GeoJSONExporter.convert_wkt_string_to_geojson(
        'LINESTRING Z (200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.6 0, 200000.7 200000.8 0)')
    assert line == {
        "type": "LineString",
        "coordinates": [[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.6, 0],
                        [200000.7, 200000.8, 0]],
        "bbox": [200000.1, 200000.2, 0, 200000.7, 200000.8, 0],
        "crs": {"properties": {"name": "EPSG:31370"}, "type": "name"}}


def test_convert_wkt_string_to_geojson_point():
    point = GeoJSONExporter.convert_wkt_string_to_geojson(
        'POINT Z (200000.1 200000.2 0)')
    assert point == {
        "type": "Point",
        "coordinates": [200000.1, 200000.2, 0.0],
        "bbox": [200000.1, 200000.2, 0.0, 200000.1, 200000.2, 0.0],
        "crs": {"properties": {"name": "EPSG:31370"}, "type": "name"}}


def test_convert_wkt_string_to_geojson_polygon():
    polygon = GeoJSONExporter.convert_wkt_string_to_geojson(
        'POLYGON Z ((200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.8 0, 200000.1 200000.2 0))')
    assert polygon == {
        "type": "Polygon",
        "coordinates": [[[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.8, 0], [200000.1, 200000.2, 0]]],
        "bbox": [200000.1, 200000.2, 0, 200000.5, 200000.8, 0],
        "crs": {"properties": {"name": "EPSG:31370"}, "type": "name"}}


def test_convert_wkt_string_to_geojson_multipolygon():
    multipolygon = GeoJSONExporter.convert_wkt_string_to_geojson(
        'MULTIPOLYGON Z (((200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.8 0, 200000.1 200000.2 0)), ((200002.1 200002.2 0, 200002.3 200002.4 0, 200002.5 200002.8 0, 200002.1 200002.2 0)))')
    assert multipolygon == {
        "type": "MultiPolygon",
        "coordinates": [[[[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.8, 0],
                          [200000.1, 200000.2, 0]]],
                        [[[200002.1, 200002.2, 0], [200002.3, 200002.4, 0], [200002.5, 200002.8, 0],
                          [200002.1, 200002.2, 0]]]],
        "bbox": [200000.1, 200000.2, 0, 200002.5, 200002.8, 0],
        "crs": {"properties": {"name": "EPSG:31370"}, "type": "name"}}

