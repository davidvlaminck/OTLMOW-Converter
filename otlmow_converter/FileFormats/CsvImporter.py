import csv
import logging
import os
from pathlib import Path

from otlmow_model.OtlmowModel.Helpers.AssetCreator import dynamic_create_instance_from_uri
from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter

csv.field_size_limit(2147483647)


class CsvImporter:
    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        csv_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'csv'), None)
        if csv_settings is None:
            raise ValueError("Unable to find csv in file formats settings")

        self.settings = csv_settings
        self.dotnotation_helper = DotnotationHelper(**self.settings['dotnotation'])
        self.headers = []
        self.data = [[]]
        self.objects = []

        self.dotnotation_table_converter = DotnotationTableConverter()
        self.dotnotation_table_converter.load_settings(self.settings['dotnotation'])

    def import_file(self, filepath: Path = None, **kwargs):
        delimiter = ';'
        quote_char = '"'
        if kwargs is not None:
            if 'delimiter' in kwargs:
                delimiter = kwargs['delimiter']
            if 'quote_char' in kwargs:
                quote_char = kwargs['quote_char']

        if filepath == '' or not os.path.isfile(filepath):
            raise FileNotFoundError(f'Could not load the file at: {filepath}')

        model_directory = None
        if kwargs is not None:
            if 'model_directory' in kwargs:
                model_directory = kwargs['model_directory']
        self.dotnotation_table_converter.model_directory = model_directory

        try:
            with open(filepath, encoding='utf-8') as file:
                csv_reader = csv.reader(file, delimiter=delimiter, quotechar=quote_char)

                data = list(csv_reader)
                list_of_dicts = self.dotnotation_table_converter.transform_2d_sequence_to_list_of_dicts(
                    two_d_sequence=data, empty_string_equals_none=True)
                return self.dotnotation_table_converter.get_data_from_table(list_of_dicts)

        except Exception as ex:
            raise ex
