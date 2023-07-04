import csv
from pathlib import Path

from otlmow_model.Helpers.AssetCreator import dynamic_create_instance_from_uri
from otlmow_model.Helpers.GenericHelper import get_aim_id_from_uuid_and_typeURI

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    converter = OtlmowConverter()
    assets = []
    with open(Path('202306191351_multipoints.csv')) as csv_file:
        # example:
        # "uuid"	"wkt_string"	"uri"
        # "0005ab2a-a42d-4066-8580-41f01ce1bee0"	MULTIPOINT Z ((61989.18 209072.41 0),(61989.18 209072.41 0))	https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#WVLichtmast
        csv_reader = csv.reader(csv_file, delimiter='\t')
        next(csv_reader, None)  # skip headers
        for row in csv_reader:
            wkt = row[1]
            wkt = wkt[:-1].replace('MULTIPOINT Z (', '')
            parts = set(wkt.split(','))
            if len(parts) == 1:
                asset = dynamic_create_instance_from_uri(row[2])
                asset.assetId.identificator = get_aim_id_from_uuid_and_typeURI(row[0], row[2])
                asset.geometry = 'POINT Z ' + parts.pop()
                assets.append(asset)

    converter.create_file_from_assets(filepath=Path('multipoints_fix.json'), list_of_objects=assets)
