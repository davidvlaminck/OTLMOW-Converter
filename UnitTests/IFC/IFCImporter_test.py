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
