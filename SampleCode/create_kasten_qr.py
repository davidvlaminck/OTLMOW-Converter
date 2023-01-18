import csv
from datetime import datetime
from pathlib import Path

from otlmow_model.Classes.Onderdeel.HoortBij import HoortBij
from otlmow_model.Classes.Onderdeel.Wegkantkast import Wegkantkast

from otlmow_converter.OtlmowConverter import OtlmowConverter


if __name__ == '__main__':
    otlmow_converter = OtlmowConverter()

    input_file_path = Path('/home/davidlinux/Documents/AWV/202301181602_qr_kasten.csv')

    assets_to_create = []

    with open(input_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        for row in csv_reader:
            if row[6] != '':
                continue
            naam = row[1].split('/')[-1]
            kast = Wegkantkast()
            kast.naam = naam
            kast.isActief = True
            kast.assetId.identificator = row[0]
            kast.toestand = row[2]
            if row[3] != '' and row[4] != '':
                kast.geometry = f'POINT Z ({row[3]} {row[4]} 0)'
            assets_to_create.append(kast)

            relatie = HoortBij()
            relatie.isActief = True
            relatie.bronAssetId.identificator = kast.assetId.identificator
            relatie.doelAssetId.identificator = f'{kast.assetId.identificator}-bGdjOmluc3RhbGxhdGllI0thc3Q'
            relatie.assetId.identificator = f'hoortbij_van_{kast.assetId.identificator}'
            assets_to_create.append(relatie)

    # export
    file_path = Path(f'/home/davidlinux/Documents/AWV/{datetime.now().strftime("%Y%m%d%H%M%S")}_export.xlsx')
    otlmow_converter.create_file_from_assets(filepath=file_path, list_of_objects=assets_to_create)
