import logging
import os
from pathlib import Path
from typing import Dict, List

import openpyxl
from otlmow_model.OtlmowModel.Helpers.AssetCreator import dynamic_create_instance_from_uri

from otlmow_converter.DotnotationHelper import DotnotationHelper


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
        self.dotnotation_helper = DotnotationHelper(**self.settings['dotnotation'])
        self.data: Dict[str, List] = {}
        self.objects = []

    def import_file(self, filepath: Path = None, **kwargs):
        if filepath == '' or not os.path.isfile(filepath):
            raise FileNotFoundError(f'Could not load the file at: {filepath}')

        try:

            book = openpyxl.load_workbook(filepath, data_only=True)
            for sheet in book.worksheets:
                self.data[sheet] = []
                for i in range(1, sheet.max_row + 1):
                    row = []
                    for j in range(1, sheet.max_column + 1):
                        cell_obj = sheet.cell(row=i, column=j)
                        row.append(cell_obj.value)
                    self.data[sheet].append(row)

        except Exception as ex:
            raise ex

        return self.create_objects_from_data(**kwargs)

    def create_objects_from_data(self, **kwargs):
        list_of_objects = []
        model_directory = None
        if kwargs is not None:
            if 'model_directory' in kwargs:
                model_directory = kwargs['model_directory']

        cardinality_indicator = self.settings['dotnotation']['cardinality_indicator']

        for sheet, data in self.data.items():
            headers = data[0]
            type_index = headers.index('typeURI')
            for row in data[1:]:
                instance = dynamic_create_instance_from_uri(row[type_index], model_directory=model_directory)
                list_of_objects.append(instance)
                for index, row_value in enumerate(row):
                    if index == type_index:
                        continue

                    header = headers[index]

                    # make lists
                    if cardinality_indicator in header:
                        if header.count(cardinality_indicator) > 1:
                            logging.warning(f'{header} is a list of lists. This is not allowed in the Excel format')
                            continue

                    # clear geom
                    if header == 'geometry':
                        if row_value == '':
                            row_value = None

                    try:
                        self.dotnotation_helper.set_attribute_by_dotnotation_instance(
                            instance_or_attribute=instance, dotnotation=header, value=row_value,
                            convert_warnings=False)
                    except TypeError as type_error:
                        if 'Expecting a string' in type_error.args[0]:
                            self.dotnotation_helper.set_attribute_by_dotnotation_instance(
                                instance_or_attribute=instance, dotnotation=header, value=str(row_value),
                                convert_warnings=False)
                        else:
                            raise type_error

        return list_of_objects
