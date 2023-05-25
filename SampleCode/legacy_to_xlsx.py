import json
from pathlib import Path

from pandas import DataFrame

if __name__ == '__main__':
    file_path = Path('DA-2023-00505_export.json')

    # open and read json file
    with open(file_path, 'r') as file:
        data = json.load(file)

    new_data = []
    for data_object in data['@graph']:
        if not data_object['@id'].startswith('https://data.awvvlaanderen.be/id/asset/'):
            continue

        data_object['id'] = data_object['@id'][39:]
        del data_object['@id']
        data_object['type'] = 'Feature'
        data_object['typeURI'] = data_object['@type']
        data_object['assetId.toegekendDoor'] = data_object['AIMObject.assetId']['DtcIdentificator.toegekendDoor']
        data_object['assetId.identificator'] = data_object['AIMObject.assetId']['DtcIdentificator.identificator']
        del data_object['AIMObject.assetId']
        data_object['typeURI'] = data_object['@type']
        del data_object['@type']
        del data_object['type']

        if 'loc:Locatie.puntlocatie' in data_object and 'loc:3Dpunt.puntgeometrie' in data_object[
            'loc:Locatie.puntlocatie'] and 'loc:DtcCoord.lambert72' in data_object['loc:Locatie.puntlocatie'][
                'loc:3Dpunt.puntgeometrie']:
            coords = data_object['loc:Locatie.puntlocatie']['loc:3Dpunt.puntgeometrie']['loc:DtcCoord.lambert72']
            x = coords['loc:DtcCoordLambert72.xcoordinaat']
            y = coords['loc:DtcCoordLambert72.ycoordinaat']
            z = coords['loc:DtcCoordLambert72.zcoordinaat']

            data_object["loc.x"] = x
            data_object["loc.y"] = y
            data_object["loc.z"] = z

            data_object["geometry"] = f'POINT Z({x} {y} {z})'
            del data_object['loc:Locatie.puntlocatie']

        new_data.append(data_object)

    data_as_table = DataFrame(new_data)
    data_as_table.to_excel(Path(str(file_path).replace('.json', '.xlsx')))
