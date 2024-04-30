import csv
from pathlib import Path

from otlmow_model.OtlmowModel.Classes.Onderdeel.HoortBij import HoortBij
from otlmow_model.OtlmowModel.Helpers.RelationCreator import create_relation

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    # read in legacy csv
    csv_path = 'export_20240430101623.csv'  # legacy export file
    legacy_dict = {}
    with open(csv_path, newline='') as csvfile:
        reader2 = csv.reader(csvfile, delimiter='\t', quotechar='"')
        header_row = next(reader2)
        for row in reader2:
            legacy_dict[row[1]] = {'uuid': row[0], 'type': row[2]}

    type_dict = {'lgc:installatie#VPLMast': 'https://lgc.data.wegenenverkeer.be/ns/installatie#VPLMast'}

    # read in otl data
    json_path = Path('WVLichtmast-WW0056.json')  # otl data
    masten = OtlmowConverter.from_file_to_objects(json_path)
    installatienummer = 'WW0056'

    relaties = []
    for mast in masten:
        nummer = mast.naam.split('.')[1]
        constructed_naampad = f'{installatienummer}/{installatienummer}.WV/{nummer}'
        if constructed_naampad not in legacy_dict:
            print(f'{constructed_naampad} not found in legacy data')
            continue
        legacy_uuid = legacy_dict[constructed_naampad]['uuid']
        legacy_uri = type_dict[legacy_dict[constructed_naampad]['type']]

        hoortbij_relatie = create_relation(relation_type=HoortBij,
                                           source=mast,
                                           target_uuid=legacy_uuid,
                                           target_typeURI=legacy_uri)
        relaties.append(hoortbij_relatie)

    print(relaties)

    relaties_path = Path('Output/relaties.json')
    OtlmowConverter.from_objects_to_file(file_path=relaties_path, sequence_of_objects=relaties)
