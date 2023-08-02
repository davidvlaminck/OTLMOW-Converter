import base64
from pathlib import Path

from otlmow_model.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.Helpers.AssetCreator import dynamic_create_instance_from_ns_and_name, dynamic_create_instance_from_uri

from otlmow_converter.OtlmowConverter import OtlmowConverter


def get_uuid_and_typeURI_from_aim_id(aim_id: str) -> (str, str):
    uuid = aim_id[0:36]
    encoded_uri = aim_id[37:]
    while len(encoded_uri) % 4 != 0:
        encoded_uri = encoded_uri + '='
    short_uri = base64.b64decode(encoded_uri).decode('ascii')
    if short_uri.startswith('purl:'):
        if short_uri == 'purl:Agent':
            uri = 'http://purl.org/dc/terms/Agent'
    elif '#' in short_uri:
        splitted = short_uri.split('#')
        ns = splitted[0]
        name = splitted[1]
        if ns in ('installatie', 'onderdeel'):
            try:
                instance = dynamic_create_instance_from_ns_and_name(namespace=ns, class_name=name)
                uri = instance.typeURI
            except:
                # likely a legacy asset
                uri = f'https://lgc.data.wegenenverkeer.be/ns/{short_uri}'

    return uuid, uri


if __name__ == '__main__':
    converter = OtlmowConverter()
    file_path = Path('aimids_to_delete.csv')

    # read file contents
    with open(file_path, 'r') as file:
        lines = file.readlines()

    assets = []
    for line in lines:
        aim_id = line.strip()
        uuid, type_uri = get_uuid_and_typeURI_from_aim_id(aim_id)
        asset = dynamic_create_instance_from_uri(type_uri)

        if isinstance(asset, RelatieObject):
            continue

        asset.assetId.identificator = aim_id
        asset.assetId.toegekendDoor = 'AWV'
        asset.isActief = False

        assets.append(asset)

    converter.create_file_from_assets(filepath=Path('aimids_to_delete.json'), list_of_objects=assets)
