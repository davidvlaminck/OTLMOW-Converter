import json
import os
from datetime import datetime
from os.path import abspath
from pathlib import Path

from otlmow_converter.FileExporter import FileExporter
from otlmow_converter.FileImporter import FileImporter


def load_settings(settings_path):
    if settings_path == '':
        current_file_path = Path(__file__)
        directory = current_file_path.parents[0]
        settings_path = abspath(f'{directory}\\settings_sample.json')

    if not os.path.isfile(settings_path):
        raise FileNotFoundError(settings_path + " is not a valid path. File does not exist.")

    try:
        with open(settings_path) as settings_file:
            return json.load(settings_file)
    except OSError:
        raise ImportError(f'Could not open the settings file at {settings_file}')


if __name__ == '__main__':
    settings = load_settings(Path('/home/davidlinux/Documents/AWV/resources/settings_OTLMOW.json'))
    importer = FileImporter(settings=settings)
    exporter = FileExporter(settings=settings)

    assets = importer.create_assets_from_file(Path('/home/davidlinux/PycharmProjects/AwvGedeeldeFuncties/UploadAfschermendeConstructies/DAVIE_export_file_20221019_2.json'))

    # export
    file_path = Path(f'Output/{datetime.now().strftime("%Y%m%d%H%M%S")}_exporter.csv')
    exporter.create_file_from_assets(filepath=file_path, list_of_objects=assets)
