from pathlib import Path

from otlmow_model.Classes.Onderdeel.WVLichtmast import WVLichtmast

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    converter = OtlmowConverter()

    file_path = Path('202305161526_masten_namen.csv')
    with open(file_path, 'r') as file:
        lines = file.readlines()

    objecten = [WVLichtmast.from_dict({'naam': line.split('\t')[1].replace('\n', ''), 'assetId':
        {'identificator': line.split('\t')[0].replace('"', '') + '-b25kZXJkZWVsI1dWTGljaHRtYXN0', 'toegekendDoor': 'AWV'}}) for line in lines[1:]]

    converter.create_file_from_assets(filepath=Path('mast_namen.json'), list_of_objects=objecten)
