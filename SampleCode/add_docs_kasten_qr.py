import csv
from pathlib import Path

from otlmow_model.Classes.Onderdeel.Wegkantkast import Wegkantkast
from otlmow_model.Helpers.GenericHelper import get_aim_id_from_uuid_and_typeURI

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    csv_path = '/home/davidlinux/Documents/AWV/202307042049_vmhs_kasten_document_name.csv'
    with open(csv_path, newline='') as csvfile:
        reader2 = csv.reader(csvfile, delimiter='\t', quotechar='"')
        header_row = next(reader2)
        data = [row for row in reader2]

    kast_list = []

    for data_row in data[0:1]:
        kast = Wegkantkast()
        kast.assetId.identificator = get_aim_id_from_uuid_and_typeURI(data_row[1], Wegkantkast.typeURI)
        kast.elektrischSchema.bestandsnaam = data_row[3]
        kast.elektrischSchema.mimeType = 'application/pdf'
        kast.elektrischSchema.omschrijving.waarde = 'Elektrisch schema in pdf formaat'
        kast_list.append(kast)

    converter = OtlmowConverter()
    converter.create_file_from_assets(list_of_objects=kast_list,
                                      filepath=Path('/home/davidlinux/Documents/AWV/vmhs_kasten.json'))
