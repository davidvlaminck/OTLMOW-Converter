import json
import unittest
from pathlib import Path

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.FileFormats.GeoJSONExporter import GeoJSONExporter
from otlmow_converter.FileFormats.GeoJSONImporter import GeoJSONImporter

base_dir = Path(__file__).parent
model_directory_path = Path(__file__).parent.parent / 'TestModel'


def set_up_importer():
    return GeoJSONImporter(
        settings={'file_formats': [{"name": "geojson", "dotnotation": {
            "waarde_shortcut": True,
            "separator": '.',
            'cardinality_indicator': '[]'
        }}]})


def set_up_exporter():
    return GeoJSONExporter(
        settings={'file_formats': [{"name": "geojson", "dotnotation": {
            "waarde_shortcut": True,
            "separator": '.',
            'cardinality_indicator': '[]',
            'cardinality_separator': '|'
        }}]}, model_directory=model_directory_path)


@ unittest.skip('takes too long to run')
def test_import_then_export():
    importer = set_up_importer()
    exporter = set_up_exporter()

    import_file_path = base_dir.parent.parent / 'benchmark/files/all_classes.geojson'
    export_file_path = base_dir / 'after_export.geojson'
    objects = importer.import_file(import_file_path)
    assert len(objects) == 608

    exporter.export_to_file(export_file_path, objects)

    # assert two files are equal when read with json
    with open(import_file_path, 'r') as file1:
        with open(export_file_path, 'r') as file2:
            json_file1 = json.load(file1)
            json_file2 = json.load(file2)
            assert sorted(json_file1) == sorted(json_file2)


def test_convert_list_of_objects_to_list_of_geodicts_minimal():
    exporter = set_up_exporter()

    test_object = AllCasesTestClass()
    test_object.assetId.identificator = '00000000-0000-0000-0000-000000000000-b25kZXJkZWVsI0hlZWZ0QWFudnVsbGVuZGVHZW9tZXRyaWU'
    test_object.assetId.toegekendDoor = 'AWV'
    test_object.testIntegerField = 5

    expected_dict = {
        "id": "00000000-0000-0000-0000-000000000000-b25kZXJkZWVsI0hlZWZ0QWFudnVsbGVuZGVHZW9tZXRyaWU",
        "properties":
            {
                "assetId.toegekendDoor": "AWV",
                "assetId.identificator": "00000000-0000-0000-0000-000000000000-b25kZXJkZWVsI0hlZWZ0QWFudnVsbGVuZGVHZW9tZXRyaWU",
                "typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                "testIntegerField": "5",
            },
        "type": "Feature"
    }

    assert exporter.convert_list_of_objects_to_list_of_geodicts([test_object])[0] == expected_dict


def test_convert_list_of_objects_to_list_of_geodicts_bool():
    exporter = set_up_exporter()

    test_object = AllCasesTestClass()
    test_object.assetId.identificator = '00000000-0000-0000-0000-000000000000-b25kZXJkZWVsI0hlZWZ0QWFudnVsbGVuZGVHZW9tZXRyaWU'
    test_object.assetId.toegekendDoor = 'AWV'
    test_object.isActief = True

    expected_dict = {
        "id": "00000000-0000-0000-0000-000000000000-b25kZXJkZWVsI0hlZWZ0QWFudnVsbGVuZGVHZW9tZXRyaWU",
        "properties":
            {
                "assetId.toegekendDoor": "AWV",
                "assetId.identificator": "00000000-0000-0000-0000-000000000000-b25kZXJkZWVsI0hlZWZ0QWFudnVsbGVuZGVHZW9tZXRyaWU",
                "typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass",
                "isActief": "true",
            },
        "type": "Feature"
    }

    assert exporter.convert_list_of_objects_to_list_of_geodicts([test_object])[0] == expected_dict


def test_convert_list_of_objects_to_list_of_geodicts_with_geom():
    exporter = set_up_exporter()

    test_object = AnotherTestClass()
    test_object.assetId.identificator = '00000000-0000-0000-0000-000000000000-b25kZXJkZWVsI0hlZWZ0QWFudnVsbGVuZGVHZW9tZXRyaWU'
    test_object.assetId.toegekendDoor = 'AWV'
    test_object.geometry = 'LINESTRING Z (200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.6 0, 200000.7 200000.8 0)'

    expected_dict = {
        "id": "00000000-0000-0000-0000-000000000000-b25kZXJkZWVsI0hlZWZ0QWFudnVsbGVuZGVHZW9tZXRyaWU",
        "properties":
            {
                "assetId.toegekendDoor": "AWV",
                "assetId.identificator": "00000000-0000-0000-0000-000000000000-b25kZXJkZWVsI0hlZWZ0QWFudnVsbGVuZGVHZW9tZXRyaWU",
                "typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass",
            },
        "type": "Feature",
        "geometry":
            {
                "type": "LineString",
                "coordinates":
                    [
                        [
                            200000.1,
                            200000.2,
                            0
                        ],
                        [
                            200000.3,
                            200000.4,
                            0
                        ],
                        [
                            200000.5,
                            200000.6,
                            0
                        ],
                        [
                            200000.7,
                            200000.8,
                            0
                        ]
                    ],
                "bbox":
                    [
                        200000.1,
                        200000.2,
                        0,
                        200000.7,
                        200000.8,
                        0
                    ],
                "crs":
                    {
                        "properties":
                            {
                                "name": "EPSG:31370"
                            },
                        "type": "name"
                    }
            }
    }

    assert exporter.convert_list_of_objects_to_list_of_geodicts([test_object])[0] == expected_dict


def test_convert_wkt_string_to_geojson_line():
    exporter = set_up_exporter()
    line = exporter.convert_wkt_string_to_geojson(
        'LINESTRING Z (200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.6 0, 200000.7 200000.8 0)')
    assert line == {
        "type": "LineString",
        "coordinates": [[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.6, 0],
                        [200000.7, 200000.8, 0]],
        "bbox": [200000.1, 200000.2, 0, 200000.7, 200000.8, 0],
        "crs": {"properties": {"name": "EPSG:31370"}, "type": "name"}}


def test_convert_wkt_string_to_geojson_point():
    exporter = set_up_exporter()
    point = exporter.convert_wkt_string_to_geojson(
        'POINT Z (200000.1 200000.2 0)')
    assert point == {
        "type": "Point",
        "coordinates": [[200000.1, 200000.2, 0]],
        "bbox": [200000.1, 200000.2, 0, 200000.1, 200000.2, 0],
        "crs": {"properties": {"name": "EPSG:31370"}, "type": "name"}}


def test_convert_wkt_string_to_geojson_polygon():
    exporter = set_up_exporter()
    polygon = exporter.convert_wkt_string_to_geojson(
        'POLYGON Z ((200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.8 0, 200000.1 200000.2 0))')
    assert polygon == {
        "type": "Polygon",
        "coordinates": [[[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.8, 0], [200000.1, 200000.2, 0]]],
        "bbox": [200000.1, 200000.2, 0, 200000.5, 200000.8, 0],
        "crs": {"properties": {"name": "EPSG:31370"}, "type": "name"}}


def test_convert_wkt_string_to_geojson_multipolygon():
    exporter = set_up_exporter()
    multipolygon = exporter.convert_wkt_string_to_geojson(
        'MULTIPOLYGON Z (((200000.1 200000.2 0, 200000.3 200000.4 0, 200000.5 200000.8 0, 200000.1 200000.2 0)), ((200002.1 200002.2 0, 200002.3 200002.4 0, 200002.5 200002.8 0, 200002.1 200002.2 0)))')
    assert multipolygon == {
        "type": "MultiPolygon",
        "coordinates": [[[[200000.1, 200000.2, 0], [200000.3, 200000.4, 0], [200000.5, 200000.8, 0],
                          [200000.1, 200000.2, 0]]],
                        [[[200002.1, 200002.2, 0], [200002.3, 200002.4, 0], [200002.5, 200002.8, 0],
                          [200002.1, 200002.2, 0]]]],
        "bbox": [200000.1, 200000.2, 0, 200002.5, 200002.8, 0],
        "crs": {"properties": {"name": "EPSG:31370"}, "type": "name"}}

