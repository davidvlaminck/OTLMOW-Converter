import time
from pathlib import Path

from otlmow_model.Classes.Onderdeel.Bevestiging import Bevestiging
from otlmow_model.Classes.Onderdeel.Bevestigingsbeugel import Bevestigingsbeugel
from otlmow_model.Classes.Onderdeel.Camera import Camera
from otlmow_model.Classes.Onderdeel.Lichtmast import Lichtmast
from otlmow_model.Classes.Onderdeel.RechteSteun import RechteSteun
from otlmow_model.Classes.Onderdeel.Seinbrug import Seinbrug
from otlmow_model.Classes.Onderdeel.WVLichtmast import WVLichtmast

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    converter = OtlmowConverter()

    assets = converter.create_assets_from_file(Path('DA-2023-00435_export_dev.json'))
    beugel_dict = {a.assetId.identificator: a for a in assets if isinstance(a, Bevestigingsbeugel)}

    steun_types = [Seinbrug.typeURI, WVLichtmast.typeURI, Lichtmast.typeURI, RechteSteun.typeURI]

    for asset in assets:
        if not isinstance(asset, Bevestiging):
            continue

        if asset.bron.typeURI == Bevestigingsbeugel.typeURI:
            if asset.doel.typeURI == Camera.typeURI:
                beugel_dict[asset.bronAssetId.identificator].camera_relatie = asset
                beugel_dict[asset.bronAssetId.identificator].camera_id = asset.doelAssetId
            elif asset.doel.typeURI in steun_types:
                beugel_dict[asset.bronAssetId.identificator].steun_relatie = asset
                beugel_dict[asset.bronAssetId.identificator].steun_id = asset.doelAssetId
        elif asset.doel.typeURI == Bevestigingsbeugel.typeURI:
            if asset.bron.typeURI == Camera.typeURI:
                beugel_dict[asset.doelAssetId.identificator].camera_relatie = asset
                beugel_dict[asset.doelAssetId.identificator].camera_id = asset.bronAssetId
            elif asset.bron.typeURI in steun_types:
                beugel_dict[asset.doelAssetId.identificator].steun_relatie = asset
                beugel_dict[asset.doelAssetId.identificator].steun_id = asset.bronAssetId

    aan_te_leveren = []
    for index, beugel in enumerate(beugel_dict.values()):
        if hasattr(beugel, 'steun_relatie') and hasattr(beugel, 'camera_relatie'):
            beugel_copy = Bevestigingsbeugel()
            beugel_copy.assetId = beugel.assetId
            beugel_copy.isActief = False
            aan_te_leveren.append(beugel_copy)

            beugel.camera_relatie.isActief = False
            aan_te_leveren.append(beugel.camera_relatie)

            beugel.steun_relatie.isActief = False
            aan_te_leveren.append(beugel.steun_relatie)

            bypass_relatie = Bevestiging()
            bypass_relatie.assetId.identificator = str(index)
            bypass_relatie.bronAssetId = beugel.steun_id
            bypass_relatie.doelAssetId = beugel.camera_id
            aan_te_leveren.append(bypass_relatie)

    converter.create_file_from_assets(filepath=Path('nieuwe_bevestigingen_dev.json'), list_of_objects=aan_te_leveren)
