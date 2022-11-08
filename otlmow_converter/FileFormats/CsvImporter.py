import logging
import os
from pathlib import Path

from otlmow_converter.AssetFactory import AssetFactory
from otlmow_converter.DotnotationHelper import DotnotationHelper


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
        self.headers = []
        self.data = [[]]
        self.objects = []

    def import_file(self, filepath: Path = None, **kwargs):
        delimiter = ';'
        if kwargs is not None:
            if 'delimiter' in kwargs:
                delimiter = kwargs['delimiter']

        if filepath == '' or not os.path.isfile(filepath):
            raise FileNotFoundError(f'Could not load the file at: {filepath}')

        try:
            with open(filepath, 'r') as file:
                self.headers = file.readline()[:-1].split(delimiter)
                data = []
                for line in file:
                    data.append(line[:-1].split(delimiter))
                self.data = data

        except Exception as ex:
            raise ex

        return self.create_objects_from_data(**kwargs)

    def create_objects_from_data(self, **kwargs):
        list_of_objects = []
        class_directory = None

        if kwargs is not None:
            if 'class_directory' in kwargs:
                class_directory = kwargs['class_directory']

        try:
            type_index = self.headers.index('typeURI')
        except ValueError:
            raise ValueError('The data is missing essential typeURI data')

        for record in self.data:
            instance = AssetFactory().dynamic_create_instance_from_uri(record[type_index], directory=class_directory)
            list_of_objects.append(instance)
            for index, row in enumerate(record):
                if index == type_index:
                    continue
                if row == '':
                    continue

                if self.headers[index] in ['bron.typeURI', 'doel.typeURI']:
                    continue  # TODO get bron and doel

                cardinality_indicator = self.settings['dotnotation']['cardinality indicator']

                if cardinality_indicator in self.headers[index]:
                    if self.headers[index].count(cardinality_indicator) > 1:
                        logging.warning(f'{self.headers[index]} is a list of lists. This is not allowed in the CSV format')
                        continue
                    value = row.split(self.settings['dotnotation']['cardinality separator'])
                else:
                    value = row

                if self.headers[index] == 'geometry':
                    value = value
                    if value == '':
                        value = None
                    self.headers[index] = 'geometry'

                try:
                    DotnotationHelper.set_attribute_by_dotnotation(instanceOrAttribute=instance,
                                                                   dotnotation=self.headers[index],
                                                                   value=value,
                                                                   convert_warnings=False,
                                                                   separator=self.settings['dotnotation']['separator'],
                                                                   cardinality_indicator=cardinality_indicator,
                                                                   waarde_shortcut_applicable=self.settings['dotnotation'][
                                                                       'waarde_shortcut_applicable'])
                except AttributeError as exc:
                    raise AttributeError(self.headers[index]) from exc

        return list_of_objects
