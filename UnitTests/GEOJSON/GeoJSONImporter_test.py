from datetime import time, datetime, date
from pathlib import Path

import pytest

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.GeoJSONImporter import GeoJSONImporter

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def set_up_importer():
    return GeoJSONImporter(
        settings={'file_formats': [{"name": "geojson", "dotnotation": {
            "waarde_shortcut": True,
            "separator": '.',
            'cardinality_indicator': '[]'
        }}]})


def test_load_test_unnested_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes.geojson'

    importer = set_up_importer()
    objects = importer.import_file(filepath=file_location, model_directory=model_directory_path)
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


def test_load_test_nested_attributes_level_1(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_1.geojson'

    importer = set_up_importer()
    objects = importer.import_file(filepath=file_location, model_directory=model_directory_path)
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


def test_load_test_nested_attributes_level_2(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_2.geojson'

    importer = set_up_importer()
    objects = importer.import_file(filepath=file_location, model_directory=model_directory_path)
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
            model_directory=model_directory_path, data=
            {"type": "FeatureCollection", "features": [{
                "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
                "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                               "invalid_attribute": "some value"}}]})


def test_decode_empty_value():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "toestand": None}}]})

    assert AllCasesTestClass.typeURI == lijst_objecten[0].typeURI
    assert lijst_objecten[0].is_instance_of(AllCasesTestClass, model_directory=model_directory_path, dynamic_created=True)
    assert lijst_objecten[0].toestand is None


def test_decode_Stringfield():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testStringField": "string"}}]})

    assert AllCasesTestClass.typeURI == lijst_objecten[0].typeURI
    assert lijst_objecten[0].testStringField == 'string'


def test_decode_StringfieldMetKard():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testStringFieldMetKard[]": "string|string2"}}]})

    assert lijst_objecten[0].testStringFieldMetKard == ["string", "string2"]


def test_decode_DecimalNumberField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testDecimalField": 2.5}}]})

    assert lijst_objecten[0].testDecimalField == 2.5


def test_decode_TimeField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testTimeField": "22:22:22"}}]})

    assert lijst_objecten[0].testTimeField == time(hour=22, minute=22, second=22)


def test_decode_DateTimeField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testDateTimeField": "2022-2-2 22:22:22"}}]})

    assert lijst_objecten[0].testDateTimeField == datetime(year=2022, month=2, day=2, hour=22, minute=22, second=22)


def test_decode_DateField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testDateField": "2022-2-2"}}]})

    assert lijst_objecten[0].testDateField == date(year=2022, month=2, day=2)


def test_decode_testKwantWrd():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testKwantWrd": 3.5}}]})

    assert lijst_objecten[0].testKwantWrd.waarde == 3.5


def test_decode_testKwantWrd_waarde_shortcut_false():
    importer = set_up_importer()
    importer.settings['dotnotation']['waarde_shortcut_applicable'] = False
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testKwantWrd.waarde": 3.5}}]})

    assert lijst_objecten[0].testKwantWrd.waarde == 3.5


def test_decode_testKwantWrdMetKard():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                           'testKwantWrdMetKard[]': '4.5|6.5'}}]})

    assert lijst_objecten[0].testKwantWrdMetKard[0].waarde == 4.5
    assert lijst_objecten[0].testKwantWrdMetKard[1].waarde == 6.5


def test_decode_UnionType():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testUnionType.unionString": "string"}}]})

    assert lijst_objecten[0].testUnionType.unionString == 'string'


def test_decode_ComplexType():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testComplexType.testStringField": "string"}}]})

    assert lijst_objecten[0].testComplexType.testStringField == 'string'


def test_decode_ComplexTypeMetKard():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        model_directory=model_directory_path, data=
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
        model_directory=model_directory_path, data=
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
