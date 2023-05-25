import json
from pathlib import Path

if __name__ == '__main__':
    file_path = Path('DA-2023-00505_export.json')

    # open and read json file
    with open(file_path, 'r') as file:
        data = json.load(file)

    new_data = {'type': 'FeatureCollection',
                'features': []}

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

        if 'loc:Locatie.puntlocatie' in data_object and 'loc:3Dpunt.puntgeometrie' in data_object[
            'loc:Locatie.puntlocatie'] and 'loc:DtcCoord.lambert72' in data_object['loc:Locatie.puntlocatie'][
                'loc:3Dpunt.puntgeometrie']:
            coords = data_object['loc:Locatie.puntlocatie']['loc:3Dpunt.puntgeometrie']['loc:DtcCoord.lambert72']
            x = coords['loc:DtcCoordLambert72.xcoordinaat']
            y = coords['loc:DtcCoordLambert72.ycoordinaat']
            z = coords['loc:DtcCoordLambert72.zcoordinaat']

            data_object["geometry"] = {"type": "Point", "coordinates": [x, y, z],
                                       "bbox": [x, y, z, x, y, z],
                                       "crs": {"properties": {"name": "EPSG:31370"}, "type": "name"}}
            del data_object['loc:Locatie.puntlocatie']

        new_data['features'].append(data_object)

    with open(Path(str(file_path).replace('.json', '.geojson')), 'w') as file:
        json.dump(new_data, fp=file)
