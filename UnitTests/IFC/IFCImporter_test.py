import json
from dataclasses import fields
from pathlib import Path

from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import print_overview_assets

from otlmow_converter.FileFormats.IFCDomain import IfcRelContainedInSpatialStructure
from otlmow_converter.FileFormats.IFCImporter import IFCImporter

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_load_test_unnested_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'Output-IFC-metOTLdata.ifc'

    objects = list(IFCImporter.to_objects(filepath=file_location))
    assert len(recwarn.list) == 0

    assert len(objects) == 59

    print_overview_assets(objects)

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#StalenPlaat'
    assert instance.assetId.identificator == '3sfJ8pCUTF8gDx7PDAn4pS'
    assert instance.naam == 'LIGGER'
    assert instance.notitie == 'PL35*205'

def test_ifc_to_dict():
    file_location = Path(__file__).parent / 'Testfiles' / 'Output-IFC-metOTLdata.ifc'

    d = IFCImporter.parse_ifc_file_to_ifc_dict(filepath=file_location)

    type_dict = {}
    for k, v in d.items():
        if v['_type'] not in type_dict:
            type_dict[v['_type']] = 0
        type_dict[v['_type']] += 1

    print(type_dict)
    json.dump(d, open('ifc_dict.json', 'w'), indent=4)


def test_ifc_to_objects():
    file_location = Path(__file__).parent / 'Testfiles' / 'Output-IFC-metOTLdata.ifc'

    objects = IFCImporter.ifc_file_to_objects(filepath=file_location)

    for otl_ojbect in objects:
        print(otl_ojbect)


def test_structure():
    cls = IfcRelContainedInSpatialStructure
    for field in fields(cls):
        print(field)

def test_parse_nested_tuples():
    result = IFCImporter.parse_nested_tuples('(a,b,c)')
    assert result == ('a', 'b', 'c')

    result = IFCImporter.parse_nested_tuples('(a,b,c,)')
    assert result == ('a', 'b', 'c', '')

    result = IFCImporter.parse_nested_tuples('((a),b,c,d)')
    assert result == (tuple('a'), 'b', 'c', 'd')

    result = IFCImporter.parse_nested_tuples('(a,"b,c",)')
    assert result == ('a', '"b,c"', '')

    result = IFCImporter.parse_nested_tuples("'_UxOpdGmQT6xVz0y_eFnUw',#24,'OTL_voorbeeld',$,(#69,#70,#71,#72)")
    assert result == (
        "'_UxOpdGmQT6xVz0y_eFnUw'",
        '#24',
        "'OTL_voorbeeld'",
        '$',
        ('#69', '#70', '#71', '#72'),
    )


def test_geometry_extraction():
    file_location = Path(__file__).parent / 'Testfiles' / 'Output-IFC-metOTLdata.ifc'

    objects = list(IFCImporter.to_objects(filepath=file_location))
    assert len(objects) == 59

    # Get the first object (index 0) with assetId.identificator = 3sfJ8pCUTF8gDx7PDAn4pS
    instance = objects[0]
    assert instance.assetId.identificator == '3sfJ8pCUTF8gDx7PDAn4pS'

    assert instance.geometry == """POLYGON Z ((134985.102499 183515.252611 56.267761, 134984.897499 183515.252611 56.267761, 134984.897499 183515.281386 56.247836, 134985.102499 183515.281386 56.247836, 134985.102499 183515.252611 56.267761))"""


def test_geometry_extraction_2():
    file_location = Path(__file__).parent / 'Testfiles' / 'Output-IFC-metOTLdata.ifc'

    objects = list(IFCImporter.to_objects(filepath=file_location))
    assert len(objects) == 59

    # Get the second object (index 1) with assetId.identificator
    instance = objects[1]
    assert instance.assetId.identificator == '24fOKhM0zElBwReHfAF1QE'

    assert instance.geometry == """POLYGON Z ((134985.465276 183514.402926 54.43, 134985.49283 183514.397445 54.43, 134985.516188 183514.381838 54.43, 134985.531796 183514.358479 54.43, 134985.537276 183514.330926 54.43, 134985.531796 183514.303373 54.43, 134985.516188 183514.280014 54.43, 134985.49283 183514.264407 54.43, 134985.465276 183514.258926 54.43, 134985.437723 183514.264407 54.43, 134985.414365 183514.280014 54.43, 134985.398757 183514.303373 54.43, 134985.393276 183514.330926 54.43, 134985.398757 183514.358479 54.43, 134985.414365 183514.381838 54.43, 134985.437723 183514.397445 54.43, 134985.465276 183514.402926 54.43))"""
