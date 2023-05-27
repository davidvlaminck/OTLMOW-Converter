from datetime import time, datetime, date

import pytest

from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.GeoJSONImporter import GeoJSONImporter


def set_up_importer():
    return GeoJSONImporter(
        settings={'file_formats': [{"name": "geojson", "dotnotation": {
            "waarde_shortcut": True,
            "separator": '.',
            'cardinality indicator': '[]'
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
            class_directory='UnitTests.TestClasses.Classes', data=
            {"type": "FeatureCollection", "features": [{
                "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
                "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                               "invalid_attribute": "some value"}}]})


def test_decode_empty_value():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
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
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testStringField": "string"}}]})

    assert AllCasesTestClass.typeURI == lijst_objecten[0].typeURI
    assert lijst_objecten[0].testStringField == 'string'


def test_decode_StringfieldMetKard():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testStringFieldMetKard[]": "string|string2"}}]})

    assert lijst_objecten[0].testStringFieldMetKard == ["string", "string2"]


def test_decode_DecimalNumberField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testDecimalField": 2.5}}]})

    assert lijst_objecten[0].testDecimalField == 2.5


def test_decode_TimeField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testTimeField": "22:22:22"}}]})

    assert lijst_objecten[0].testTimeField == time(hour=22, minute=22, second=22)


def test_decode_DateTimeField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testDateTimeField": "2022-2-2 22:22:22"}}]})

    assert lijst_objecten[0].testDateTimeField == datetime(year=2022, month=2, day=2, hour=22, minute=22, second=22)


def test_decode_DateField():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testDateField": "2022-2-2"}}]})

    assert lijst_objecten[0].testDateField == date(year=2022, month=2, day=2)


def test_decode_testKwantWrd():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testKwantWrd": 3.5}}]})

    assert lijst_objecten[0].testKwantWrd.waarde == 3.5


def test_decode_testKwantWrd_waarde_shortcut_false():
    importer = set_up_importer()
    importer.settings['dotnotation']['waarde_shortcut_applicable'] = False
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testKwantWrd.waarde": 3.5}}]})

    assert lijst_objecten[0].testKwantWrd.waarde == 3.5


def test_decode_testKwantWrdMetKard():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {'typeURI': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                           'testKwantWrdMetKard[]': '4.5|6.5'}}]})

    assert lijst_objecten[0].testKwantWrdMetKard[0].waarde == 4.5
    assert lijst_objecten[0].testKwantWrdMetKard[1].waarde == 6.5


def test_decode_UnionType():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testUnionType.unionString": "string"}}]})

    assert lijst_objecten[0].testUnionType.unionString == 'string'


def test_decode_ComplexType():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testComplexType.testStringField": "string"}}]})

    assert lijst_objecten[0].testComplexType.testStringField == 'string'


def test_decode_ComplexTypeMetKard():
    importer = set_up_importer()
    lijst_objecten = importer.decode_objects(
        class_directory='UnitTests.TestClasses.Classes', data=
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
        class_directory='UnitTests.TestClasses.Classes', data=
        {"type": "FeatureCollection", "features": [{
            "id": "3c221106-2dc6-4bdc-b567-3cfc964e4d64-aW1wbGVtZW50YXRpZWVsZW1lbnQjRWxlY3RyaWNpdHlDYWJsZQ",
            "properties": {"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                           "testComplexType.testComplexType2.testStringField": "string"}}]})

    assert lijst_objecten[0].testComplexType.testComplexType2.testStringField == 'string'
