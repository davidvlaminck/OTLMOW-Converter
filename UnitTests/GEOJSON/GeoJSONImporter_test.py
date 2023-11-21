from datetime import time, datetime, date

import pytest

from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.GeoJSONImporter import GeoJSONImporter


def set_up_importer():
    return GeoJSONImporter(
        settings={'file_formats': [{"name": "geojson", "dotnotation": {
            "waarde_shortcut": True,
            "separator": '.',
            'cardinality_indicator': '[]'
        }}]})


def test_invalid_typeURI():
    importer = set_up_importer()
    with pytest.raises(ValueError):
        importer.decode_objects({"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {}}]})


def test_decode_invalid_attribute():
    importer = set_up_importer()
    with pytest.raises(AttributeError):
        importer.decode_objects(
            model_directory='UnitTests.TestClasses', data=
            {"type": "FeatureCollection", "features": [{
                "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
                "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                               "invalid_attribute": "some value"}}]})


def test_decode_empty_value():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "toestand": None}}]})

    assert AllCasesTestClass.typeURI == lijst_objecten[0].typeURI
    assert isinstance(lijst_objecten[0], AllCasesTestClass)
    assert lijst_objecten[0].toestand is None


def test_decode_Stringfield():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testStringField": "string"}}]})

    assert AllCasesTestClass.typeURI == lijst_objecten[0].typeURI
    assert lijst_objecten[0].testStringField == 'string'


def test_decode_StringfieldMetKard():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testStringFieldMetKard[]": "string|string2"}}]})

    assert lijst_objecten[0].testStringFieldMetKard == ["string", "string2"]


def test_decode_DecimalNumberField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testDecimalField": 2.5}}]})

    assert lijst_objecten[0].testDecimalField == 2.5


def test_decode_TimeField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testTimeField": "22:22:22"}}]})

    assert lijst_objecten[0].testTimeField == time(hour=22, minute=22, second=22)


def test_decode_DateTimeField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testDateTimeField": "2022-2-2 22:22:22"}}]})

    assert lijst_objecten[0].testDateTimeField == datetime(year=2022, month=2, day=2, hour=22, minute=22, second=22)


def test_decode_DateField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testDateField": "2022-2-2"}}]})

    assert lijst_objecten[0].testDateField == date(year=2022, month=2, day=2)


def test_decode_testKwantWrd():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testKwantWrd": 3.5}}]})

    assert lijst_objecten[0].testKwantWrd.waarde == 3.5


def test_decode_testKwantWrd_waarde_shortcut_false():
    importer = set_up_importer()
    importer.settings['dotnotation']['waarde_shortcut_applicable'] = False
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testKwantWrd.waarde": 3.5}}]})

    assert lijst_objecten[0].testKwantWrd.waarde == 3.5


def test_decode_testKwantWrdMetKard():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                           'testKwantWrdMetKard[]': '4.5|6.5'}}]})

    assert lijst_objecten[0].testKwantWrdMetKard[0].waarde == 4.5
    assert lijst_objecten[0].testKwantWrdMetKard[1].waarde == 6.5


def test_decode_UnionType():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testUnionType.unionString": "string"}}]})

    assert lijst_objecten[0].testUnionType.unionString == 'string'


def test_decode_ComplexType():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testComplexType.testStringField": "string"}}]})

    assert lijst_objecten[0].testComplexType.testStringField == 'string'


def test_decode_ComplexTypeMetKard():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testComplexTypeMetKard[].testStringField": "string",
                           "testComplexTypeMetKard[].testBooleanField": 'true'}}]})

    assert lijst_objecten[0].testComplexTypeMetKard[0].testStringField == 'string'
    assert lijst_objecten[0].testComplexTypeMetKard[0].testBooleanField


def test_decode_ComplexType2():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory='UnitTests.TestClasses', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testComplexType.testComplexType2.testStringField": "string"}}]})

    assert lijst_objecten[0].testComplexType.testComplexType2.testStringField == 'string'


def test_construct_wkt_string_from_geojson_point():
    importer = set_up_importer()

    point = importer.construct_wkt_string_from_geojson(
        {"type": "Point", "coordinates": [200000.1, 200000.2, 0]})
    assert point == 'POINT Z (200000.1 200000.2 0)'


def test_construct_wkt_string_from_geojson_line():
    importer = set_up_importer()

    line = importer.construct_wkt_string_from_geojson(
        {"type": "LineString", "coordinates": [[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.6, 0],
                                               [200000.7, 200000.8, 0]]})
    assert line == 'LINESTRING Z (200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.6 0, 200000.7 200000.8 0)'


def test_construct_wkt_string_from_geojson_polygon():
    importer = set_up_importer()

    polygon = importer.construct_wkt_string_from_geojson(
        {"type": "Polygon", "coordinates": [[[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.8, 0],
                                                [200000.1, 200000.2, 0]]]})
    assert polygon == 'POLYGON Z ((200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.8 0, 200000.1 200000.2 0))'


def test_construct_wkt_string_from_geojson_multipolygon():
    importer = set_up_importer()

    multipolygon = importer.construct_wkt_string_from_geojson(
        {"type": "MultiPolygon", "coordinates": [[[[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.8, 0],
                                                [200000.1, 200000.2, 0]]],
                                                [[[200002.1, 200002.2, 0], [200002.3, 200002.4, 0], [200002.5, 200002.8, 0],
                                                [200002.1, 200002.2, 0]]]]})
    assert multipolygon == 'MULTIPOLYGON Z (((200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.8 0, 200000.1 200000.2 0)), ((200002.1 200002.2 0, 200002.3 200002.4 0, 200002.5 200002.8 0, 200002.1 200002.2 0)))'
