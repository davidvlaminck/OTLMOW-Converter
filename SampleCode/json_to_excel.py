from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    otlmow_converter = OtlmowConverter()

    assets = otlmow_converter.create_assets_from_file(Path('../benchmark/files/all_classes.csv'))
    otlmow_converter.create_file_from_assets(list_of_objects=assets,
                                             filepath=Path('../benchmark/files/all_classes.jsonld'))
