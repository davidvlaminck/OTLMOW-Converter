from datetime import datetime
from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter


if __name__ == '__main__':
    otlmow_converter = OtlmowConverter()

    assets = otlmow_converter.create_assets_from_file(Path('/home/davidlinux/Documents/AWV/cameras_open_data.json'))

    # export
    file_path = Path(f'Output/{datetime.now().strftime("%Y%m%d%H%M%S")}_export.xlsx')
    otlmow_converter.create_file_from_assets(filepath=file_path, list_of_objects=assets)
