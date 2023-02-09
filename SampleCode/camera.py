from pathlib import Path

from otlmow_model.Classes.Onderdeel.Bevestiging import Bevestiging
from shapely import wkt

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.RelationCreator import create_relation

if __name__ == '__main__':
    converter = OtlmowConverter()

    assets = converter.create_assets_from_file(Path('/home/davidlinux/Documents/AWV/Camera_RechteSteun_sample.csv'))
    cameras = list(
        filter(lambda a: a.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Camera', assets))
    bevestiging = list(
        filter(lambda a: a.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', assets))
    rechtesteunen = list(
        filter(lambda a: a.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#RechteSteun' and a.geometry is not None, assets))

    cameras_zonder_bevestiging = list(filter(
        lambda a: (next((b for b in bevestiging if a.assetId.identificator in
                        [b.bronAssetId.identificator, b.doelAssetId.identificator]), None)) is None, cameras))

    # add shapes
    for lijst in [cameras_zonder_bevestiging, rechtesteunen]:
        for asset in lijst:
            if asset.geometry is not None:
                asset.shape = wkt.loads(asset.geometry)

    created_relations = []
    for cam in cameras_zonder_bevestiging:
        if cam.geometry is not None:
            circle = cam.shape.buffer(2.0)
            steunen_in_range = [rechtesteun for rechtesteun in rechtesteunen
                                if rechtesteun.shape is not None and circle.covers(rechtesteun.shape)]
            if len(steunen_in_range) == 1:
                created_relations.append(create_relation(cam, steunen_in_range[0], Bevestiging))

    converter.create_file_from_assets(filepath=Path('/home/davidlinux/Documents/AWV/nieuwe_bevestigingen.csv'),
                                      list_of_objects=created_relations, class_directory='otlmow_model.Classes')
