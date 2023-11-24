import csv
import logging
import os
from pathlib import Path

from otlmow_model.OtlmowModel.Helpers.AssetCreator import dynamic_create_instance_from_uri
from otlmow_converter.DotnotationHelper import DotnotationHelper

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

        try:
            with open(filepath, encoding='utf-8') as file:
                csv_reader = csv.reader(file, delimiter=delimiter, quotechar=quote_char)
                self.data = []
                for row_nr, row in enumerate(csv_reader):
                    if row_nr == 0:
                        self.headers = row
                    else:
                        self.data.append(row)

        except Exception as ex:
            raise ex

        return self.create_objects_from_data(**kwargs)

    def create_objects_from_data(self, **kwargs):
        list_of_objects = []
        model_directory = None

        if kwargs is not None:
            if 'model_directory' in kwargs:
                model_directory = kwargs['model_directory']

        try:
            type_index = self.headers.index('typeURI')
        except ValueError:
            raise ValueError('The data is missing essential typeURI data')

        for record in self.data:
            instance = dynamic_create_instance_from_uri(record[type_index], model_directory=model_directory)
            list_of_objects.append(instance)
            for index, row in enumerate(record):
                if index == type_index:
                    continue
                if row == '':
                    continue

                if self.headers[index] in ['bron.typeURI', 'doel.typeURI']:
                    continue  # TODO get bron and doel

                cardinality_indicator = self.settings['dotnotation']['cardinality_indicator']

                if cardinality_indicator in self.headers[index]:
                    if self.headers[index].count(cardinality_indicator) > 1:
                        logging.warning(
                            f'{self.headers[index]} is a list of lists. This is not allowed in the CSV format')
                        continue
                    value = row
                else:
                    value = row

                if self.headers[index] == 'geometry':
                    value = value
                    if value == '':
                        value = None
                    self.headers[index] = 'geometry'

                try:
                    self.dotnotation_helper.set_attribute_by_dotnotation_instance(
                        instance_or_attribute=instance, dotnotation=self.headers[index], value=value,
                        convert_warnings=False)
                except AttributeError as exc:
                    raise AttributeError(self.headers[index]) from exc

        return list_of_objects
