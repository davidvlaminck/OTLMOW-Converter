from pathlib import Path
from typing import List

from otlmow_converter.FileFormats.TableExporter import TableExporter


class CsvExporter:
    def __init__(self, settings=None, model_directory: str = None, ignore_empty_asset_id: bool = False):
        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        csv_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'csv'), None)
        if csv_settings is None:
            raise ValueError("Unable to find csv in file formats settings")

        self.settings = csv_settings
        self.table_exporter = TableExporter(dotnotation_settings=csv_settings['dotnotation'],
                                            model_directory=model_directory,
                                            ignore_empty_asset_id=ignore_empty_asset_id)

    def export_to_file(self, filepath: Path = None, list_of_objects: list = None, **kwargs) -> None:
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

        self.table_exporter.fill_master_dict(list_of_objects=list_of_objects, split_per_type=split_per_type)
        if split_per_type:
            for type_name in self.table_exporter.master:
                data = self.table_exporter.get_data_as_table(type_name=type_name)
                specific_filename = filepath.stem + '_' + type_name.replace('#', '_') + filepath.suffix

                self._write_file(file_location=Path(filepath.parent / specific_filename), data=data,
                                 delimiter=delimiter, quote_char=quote_char)
        else:
            data = self.table_exporter.get_data_as_table()
            self._write_file(file_location=filepath, data=data, delimiter=delimiter, quote_char=quote_char)

    @staticmethod
    def _write_file(file_location: Path, data: List[List], delimiter: str, quote_char: str) -> None:
        try:
            with open(file_location, "w") as file:
                for line in data:
                    line = list(map(lambda x: CsvExporter._wrap_field_in_quote_chars(field=x,
                                                                                     delimiter=delimiter,
                                                                                     quote_char=quote_char), line))
                    linestring = delimiter.join(line)
                    file.writelines(linestring + '\n')
        except Exception as ex:
            raise ex

    @staticmethod
    def _wrap_field_in_quote_chars(field: str, delimiter: str, quote_char: str) -> str:
        if delimiter in field and quote_char not in field:
            return f'{quote_char}{field}{quote_char}'
        return field
