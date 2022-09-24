import os
from pathlib import Path
from typing import Dict

import pandas as pandas
from otlmow_model.Helpers.DotnotationHelper import DotnotationHelper
from pandas import DataFrame

from otlmow_converter.AssetFactory import AssetFactory


class ExcelImporter:
    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        xls_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'xls'), None)
        if xls_settings is None:
            raise ValueError("Unable to find xls in file formats settings")

        self.settings = xls_settings
        self.data: Dict[str, DataFrame] = {}
        self.objects = []

    def import_file(self, filepath: Path = None, **kwargs):
        if filepath == '' or not os.path.isfile(filepath):
            raise FileNotFoundError(f'Could not load the file at: {filepath}')

        try:
            df_dict = pandas.read_excel(filepath, sheet_name=None)
            self.data = df_dict
        except Exception as ex:
            raise ex

        return self.create_objects_from_data()

    def create_objects_from_data(self):
        list_of_objects = []
        cardinality_indicator = self.settings['dotnotation']['cardinality indicator']

        for sheet, dataframe in self.data.items():
            for index, record in dataframe.iterrows():
                object = AssetFactory().dynamic_create_instance_from_uri(record['typeURI'])
                list_of_objects.append(object)
                for header, value in record.items():
                    if header in ['typeURI']:
                        continue

                    if cardinality_indicator in header:
                        value = value.split(self.settings['dotnotation']['cardinality separator'])

                    if header == 'geometry':
                        if value == '':
                            value = None

                    try:
                        DotnotationHelper.set_attribute_by_dotnotation(
                            instanceOrAttribute=object, dotnotation=header, value=value, convert_warnings=False,
                            separator=self.settings['dotnotation']['separator'],
                            cardinality_indicator=cardinality_indicator,
                            waarde_shortcut_applicable=self.settings['dotnotation']['waarde_shortcut_applicable'])
                    except TypeError as type_error:
                        if 'Expecting a string' in type_error.args[0]:
                            DotnotationHelper.set_attribute_by_dotnotation(
                                instanceOrAttribute=object, dotnotation=header, value=str(value), convert_warnings=False,
                                separator=self.settings['dotnotation']['separator'],
                                cardinality_indicator=cardinality_indicator,
                                waarde_shortcut_applicable=self.settings['dotnotation']['waarde_shortcut_applicable'])
                        else:
                            raise type_error

        return list_of_objects
