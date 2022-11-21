from pathlib import Path
from typing import List

from otlmow_converter.FileFormats.TableExporter import TableExporter


class CsvExporter:
    def __init__(self, settings=None, class_directory: str = None, ignore_empty_asset_id: bool = False):
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
                                            class_directory=class_directory,
                                            ignore_empty_asset_id=ignore_empty_asset_id)

    def export_to_file(self, filepath: Path = None, list_of_objects: list = None, **kwargs) -> None:
        delimiter = ';'
        split_per_type = True

        if kwargs is not None:
            if 'delimiter' in kwargs:
                delimiter = kwargs['delimiter']
            if 'split_per_type' in kwargs:
                split_per_type = kwargs['split_per_type']

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
                                 delimiter=delimiter)
        else:
            data = self.table_exporter.get_data_as_table()
            self._write_file(file_location=filepath, data=data, delimiter=delimiter)

    @staticmethod
    def _write_file(file_location: Path, data: List[List], delimiter: str) -> None:
        try:
            with open(file_location, "w") as file:
                for line in data:
                    linestring = delimiter.join(line)
                    file.writelines(linestring + '\n')
        except Exception as ex:
            raise ex
