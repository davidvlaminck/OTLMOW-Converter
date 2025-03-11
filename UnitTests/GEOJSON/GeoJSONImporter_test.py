from datetime import time, datetime, date
from pathlib import Path

import pytest

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.GeoJSONImporter import GeoJSONImporter

model_directory_path = Path(__file__).parent.parent / 'TestModel'


@pytest.mark.asyncio(scope="module")
async def test_load_test_unnested_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes.geojson'

    objects = await GeoJSONImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)
    assert len(recwarn.list) == 0

    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == '0000-0000'
    assert not instance.testBooleanField
    assert instance.testDateField == date(2019, 9, 20)
    assert instance.testDateTimeField == datetime(2001, 12, 15, 22, 22, 15)
    assert instance.testDecimalField == 79.07
    assert instance.testDecimalFieldMetKard == [10.0, 20.0]
    assert instance.testEenvoudigType.waarde == 'string1'
    assert instance.testIntegerField == -55
    assert instance.testIntegerFieldMetKard == [76, 2]
    assert instance.testKeuzelijst == 'waarde-4'
    assert instance.testKeuzelijstMetKard == ['waarde-4', 'waarde-3']
    assert instance.testKwantWrd.waarde == 98.21
    assert instance.testStringField == 'oFfeDLp'
    assert instance.testStringFieldMetKard[0] == 'string1'
    assert instance.testStringFieldMetKard[1] == 'string2'
    assert instance.testTimeField == time(11, 5, 26)
    assert instance.geometry == 'POINT Z (200000.0 200000.0 0.0)'


@pytest.mark.asyncio(scope="module")
async def test_load_test_nested_attributes_level_1(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_1.geojson'


    objects = await GeoJSONImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)
    assert len(recwarn.list) == 0

    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == '0000'
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
    assert instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde is None
    assert instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde is None
    assert instance.testComplexTypeMetKard[0].testStringField == 'string1'
    assert instance.testComplexTypeMetKard[1].testStringField == 'string2'
    assert instance.testUnionType.unionString == 'RWKofW'
    assert instance.testUnionType.unionKwantWrd.waarde is None
    assert instance.testUnionTypeMetKard[0].unionKwantWrd.waarde == 10.0
    assert instance.testUnionTypeMetKard[1].unionKwantWrd.waarde == 20.0
    assert instance.geometry == 'POINT Z (200000.0 200000.0 0.0)'


@pytest.mark.asyncio(scope="module")
async def test_load_test_nested_attributes_level_2(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_2.geojson'


    objects = await GeoJSONImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)
    assert len(recwarn.list) == 0

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
    assert instance.testComplexTypeMetKard[0].testComplexType2MetKard[0].testKwantWrd.waarde is None
    assert instance.testComplexTypeMetKard[0].testComplexType2MetKard[0].testStringField is None
    assert instance.geometry == 'POINT Z (200000.0 200000.0 0.0)'


@pytest.mark.asyncio(scope="module")
async def test_invalid_typeURI():
    with pytest.raises(ValueError):
        await GeoJSONImporter.decode_objects_async({"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {}}]})


@pytest.mark.asyncio(scope="module")
async def test_load_test_non_conform(recwarn, subtests):
    file_location = Path(__file__).parent / 'Testfiles' / 'non_conform_attributes.geojson'

    with subtests.test(msg="default behaviour"):
        recwarn.clear()
        objects = await GeoJSONImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)
        assert len(recwarn.list) == 1

        assert len(objects) == 1

        instance = objects[0]
        assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
        assert instance.assetId.identificator == '0000'
        assert not instance.testBooleanField
        assert instance.non_conform_attribute == 'non_conform_value'

    with subtests.test(msg='non conform not allowed'):
        with pytest.raises(ValueError):
            await GeoJSONImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path,
                                    allow_non_otl_conform_attributes=False)

    with subtests.test(msg="allowed, no warnings"):
        recwarn.clear()
        objects = await GeoJSONImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path,
                                          warn_for_non_otl_conform_attributes=False)
        assert len(recwarn.list) == 0

        assert len(objects) == 1

        instance = objects[0]
        assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
        assert instance.assetId.identificator == '0000'
        assert not instance.testBooleanField
        assert instance.non_conform_attribute == 'non_conform_value'


def test_construct_wkt_string_from_geojson_point():


    point = GeoJSONImporter.construct_wkt_string_from_geojson(
        {"type": "Point", "coordinates": [200000.1, 200000.2, 0]})
    assert point == 'POINT Z (200000.1 200000.2 0)'


def test_construct_wkt_string_from_geojson_line():


    line = GeoJSONImporter.construct_wkt_string_from_geojson(
        {"type": "LineString", "coordinates": [[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.6, 0],
                                               [200000.7, 200000.8, 0]]})
    assert line == 'LINESTRING Z (200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.6 0, 200000.7 200000.8 0)'


def test_construct_wkt_string_from_geojson_polygon():


    polygon = GeoJSONImporter.construct_wkt_string_from_geojson(
        {"type": "Polygon", "coordinates": [[[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.8, 0],
                                                [200000.1, 200000.2, 0]]]})
    assert polygon == 'POLYGON Z ((200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.8 0, 200000.1 200000.2 0))'


def test_construct_wkt_string_from_geojson_multipolygon():


    multipolygon = GeoJSONImporter.construct_wkt_string_from_geojson(
        {"type": "MultiPolygon", "coordinates": [[[[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.8, 0],
                                                [200000.1, 200000.2, 0]]],
                                                [[[200002.1, 200002.2, 0], [200002.3, 200002.4, 0], [200002.5, 200002.8, 0],
                                                [200002.1, 200002.2, 0]]]]})
    assert multipolygon == 'MULTIPOLYGON Z (((200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.8 0, 200000.1 200000.2 0)), ((200002.1 200002.2 0, 200002.3 200002.4 0, 200002.5 200002.8 0, 200002.1 200002.2 0)))'
