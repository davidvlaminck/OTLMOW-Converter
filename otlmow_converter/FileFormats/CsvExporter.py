import csv
from pathlib import Path
from typing import List, Iterator

from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter


class CsvExporter:
    def __init__(self, settings=None, model_directory: Path = None, ignore_empty_asset_id: bool = False):
        if settings is None:
            settings = {}

        self.settings = settings

        if 'file_formats' not in settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        csv_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'csv'), None)
        if csv_settings is None:
            raise ValueError("Unable to find csv in file formats settings")

        self.dotnotation_table_converter = DotnotationTableConverter(
            model_directory=model_directory, ignore_empty_asset_id=ignore_empty_asset_id)
        self.dotnotation_table_converter.load_settings(csv_settings['dotnotation'])

    def export_to_file(self, filepath: Path, list_of_objects: Iterator, **kwargs) -> None:
        delimiter = ';'
        split_per_type = True
        quote_char = '"'

        if kwargs is not None:
            if 'delimiter' in kwargs:
                delimiter = kwargs['delimiter']
            if 'split_per_type' in kwargs:
                split_per_type = kwargs['split_per_type']
            if 'quote_char' in kwargs:
                quote_char = kwargs['quote_char']

        if filepath is None:
            raise ValueError(f'Can not write a file to: {filepath}')

        if delimiter == '':
            delimiter = self.settings['delimiter']
            if delimiter == '':
                delimiter = ';'

        if not split_per_type:
            single_table = self.dotnotation_table_converter.get_single_table_from_data(
                list_of_objects=list_of_objects, values_as_string=True)
            data = self.dotnotation_table_converter.transform_list_of_dicts_to_2d_sequence(
                list_of_dicts=single_table, empty_string_equals_none=True)
            self._write_file(file_location=filepath, data=data, delimiter=delimiter, quote_char=quote_char)
            return

        multi_table_dict = self.dotnotation_table_converter.get_tables_per_type_from_data(
            list_of_objects=list_of_objects, values_as_string=True)
        for short_uri, table_data in multi_table_dict.items():
            data = self.dotnotation_table_converter.transform_list_of_dicts_to_2d_sequence(
                list_of_dicts=table_data, empty_string_equals_none=True)
            specific_filename = filepath.stem + '_' + short_uri.replace('#', '_') + filepath.suffix

            self._write_file(file_location=Path(filepath.parent / specific_filename), data=data,
                             delimiter=delimiter, quote_char=quote_char)

    @classmethod
    def _write_file(cls, file_location: Path, data: List[List], delimiter: str, quote_char: str) -> None:
        with open(file_location, "w") as file:
            csv_writer = csv.writer(file, delimiter=delimiter, quotechar=quote_char, quoting=csv.QUOTE_MINIMAL)
            for line in data:
                csv_writer.writerow(line)
