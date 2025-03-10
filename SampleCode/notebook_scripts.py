from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.Classes.Onderdeel.Camera import Camera
from pathlib import Path
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import print_overview_assets

if __name__ == "__main__":
    created_assets = []
    for nr in range(100):
        d = {'toestand': 'in-gebruik', 'isPtz': (nr <= 50),
            'assetId': {'identificator': f'camera_{nr}'}}
        created_assets.append(Camera.from_dict(d))

    OtlmowConverter.from_objects_to_file(file_path=Path('new_cameras.xlsx'), sequence_of_objects=created_assets)

    created_assets = OtlmowConverter.from_file_to_objects(file_path=Path('new_cameras.xlsx'))
    OtlmowConverter.from_objects_to_file(file_path=Path('new_cameras.json'), sequence_of_objects=created_assets)



    loaded_assets = OtlmowConverter.from_file_to_objects(file_path=Path('new_cameras.json'))
    print_overview_assets(loaded_assets)