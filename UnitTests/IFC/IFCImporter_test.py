from pathlib import Path

from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import print_overview_assets

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

