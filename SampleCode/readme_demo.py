from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    from otlmow_model.Classes.Onderdeel.Camera import Camera
    created_assets = []
    for nr in range(1, 100):
        d = {'toestand': 'in-gebruik', 'isPtz': (nr <= 50),
            'assetId': {'identificator': f'camera_{nr}'}}
        created_assets.append(Camera.from_dict(d))

    converter = OtlmowConverter()
    converter.create_file_from_assets(filepath=Path('new_cameras.csv'), list_of_objects=created_assets)
