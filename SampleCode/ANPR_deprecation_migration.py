from pathlib import Path

from otlmow_model.BaseClasses.OTLObject import create_dict_from_asset, OTLObject
from otlmow_model.Helpers.OTLObjectHelper import print_overview_assets

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    converter = OtlmowConverter()

    assets = converter.create_assets_from_file(Path('DA-2023-02081_export_ANPR_prd.json'))
    print_overview_assets(assets)

    anprs = [a for a in assets if a.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#ANPRCamera']
    relations = [a for a in assets if a.typeURI != 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#ANPRCamera']

    actief = [a for a in anprs if a.isActief]
    niet_actief = [a for a in anprs if not a.isActief]

    print(len(actief))
    print(len(niet_actief))

    assets_to_deliver = []
    for index, anpr in enumerate(anprs):
        # deactivate asset
        anpr.isActief = False
        assets_to_deliver.append(anpr)

        # create a copy camera asset
        dict_camera = create_dict_from_asset(anpr)
        dict_camera['typeURI'] = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Camera'
        dict_camera['isActief'] = True
        # dict_camera['ANPR'] = True  # TODO does not exist
        if dict_camera.get('modelnaam') == 'i-car-cam5':
            dict_camera['modelnaam'] = 'icar-cam5'

        local_id = f'camera_{index}'
        dict_camera['assetId']['identificator'] = local_id
        dict_camera['assetId']['toegekendDoor'] = None

        camera_object = OTLObject.from_dict(dict_camera)
        camera_object.beeldverwerkingsinstelling[0].typeBeeldverwerking = 'anpr'
        assets_to_deliver.append(camera_object)

        # create a copy camera relation
        for relation in relations:
            dict_relation = create_dict_from_asset(relation)
            dict_relation['isActief'] = True
            if relation.bronAssetId.identificator == anpr.assetId.identificator:
                dict_relation['bronAssetId']['identificator'] = local_id
                dict_relation['bronAssetId']['toegekendDoor'] = None
                dict_relation['assetId']['identificator'] = f'{local_id}_-_{relation.doelAssetId.identificator}'
                dict_relation['assetId']['toegekendDoor'] = None
                assets_to_deliver.append(OTLObject.from_dict(dict_relation))
            elif relation.doelAssetId.identificator == anpr.assetId.identificator:
                dict_relation['doelAssetId']['identificator'] = local_id
                dict_relation['doelAssetId']['toegekendDoor'] = None
                dict_relation['assetId']['identificator'] = f'{relation.bronAssetId.identificator}_-_{local_id}'
                dict_relation['assetId']['toegekendDoor'] = None
                assets_to_deliver.append(OTLObject.from_dict(dict_relation))

    # deactivate existing asset relations
    for relatie in relations:
        relatie.isActief = False
        assets_to_deliver.append(relatie)

    print_overview_assets(assets_to_deliver)

    converter.create_file_from_assets(Path('export_ANPR_prd_deliver.json'), assets_to_deliver)
