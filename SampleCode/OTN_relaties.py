import csv
from pathlib import Path

from otlmow_model.Classes.Onderdeel.Voedt import Voedt
from otlmow_model.Helpers.RelationCreator import create_relation

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    converter = OtlmowConverter()

    relaties = []

    # read csv OTN
    with open('202306052304_relaties_OTN.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:
            print(row)
            # create_relation
            relation = create_relation(source_uuid=row[2], source_typeURI=row[3], target_uuid=row[0],
                                       target_typeURI=row[1], relation_type=Voedt)
            relaties.append(relation)

    converter.create_file_from_assets(filepath=Path('OTN_missing_Voedt.json'), list_of_objects=relaties)
