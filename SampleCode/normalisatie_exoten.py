from pathlib import Path

from otlmow_model.Classes.Onderdeel.InvasieveExoten import InvasieveExoten

from otlmow_converter.AssetFactory import AssetFactory
from otlmow_converter.OtlmowConverter import OtlmowConverter


if __name__ == '__main__':
    converter = OtlmowConverter()
    list_exoten = converter.create_assets_from_file(Path('DA-2022-00004_export.json'))
    list_objects = []

    list_of_attributes_to_copy = [list_exoten[0]]

    for exoten in list_exoten:
        new_invasieve_exoten = AssetFactory.create_otl_object_using_other_otl_object_as_template(
            orig_aim_object=exoten, typeURI=InvasieveExoten.typeURI, fields_to_copy=list_of_attributes_to_copy)

        new_invasieve_exoten.assetId.identificator = f'normalized_{exoten.assetId.identificator}'
        list_objects.append(new_invasieve_exoten)

        exoten.isActief = False
        list_objects.append(exoten)

    converter.create_file_from_assets(list_of_objects=list_objects,
                                      filepath=Path('DA-2022-00004_exoten_normalisation_prd_import.json'))
