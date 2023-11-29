import logging
import os
from pathlib import Path
from typing import Dict, List

import openpyxl
from otlmow_model.OtlmowModel.Helpers.AssetCreator import dynamic_create_instance_from_uri

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError
from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.Exceptions.InvalidColumnNamesInExcelTabError import InvalidColumnNamesInExcelTabError
from otlmow_converter.Exceptions.NoTypeUriInExcelTabError import NoTypeUriInExcelTabError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError


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

        return self.create_objects_from_data(filepath=filepath, **kwargs)

    def create_objects_from_data(self, filepath: Path = None, **kwargs):
        list_of_objects = []
        model_directory = None
        if kwargs is not None:
            if 'model_directory' in kwargs:
                model_directory = kwargs['model_directory']

        cardinality_indicator = self.settings['dotnotation']['cardinality_indicator']

        exception_group = ExceptionsGroup(message=f'Failed to create objects from Excel file {filepath}')
        for sheet, data in self.data.items():
            try:
                headers = data[0]
                type_uri_index = self.get_index_of_typeURI_column_in_sheet(
                    filepath=filepath, sheet=sheet, headers=headers, data=data)
                self.check_headers(headers=headers, sheet=sheet, filepath=filepath, type_uri=data[1][type_uri_index],
                                   model_directory=model_directory)

                for row in data[1:]:
                    instance = dynamic_create_instance_from_uri(row[type_uri_index], model_directory=model_directory)
                    list_of_objects.append(instance)
                    for index, row_value in enumerate(row):
                        if index == type_uri_index:
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
                                exception_group.add_exception(type_error)
                        except Exception as ex:
                            exception_group.add_exception(ex)
            except BaseException as ex:
                exception_group.add_exception(ex)

        if len(exception_group.exceptions) > 0:
            raise exception_group

        return list_of_objects

    @classmethod
    def get_index_of_typeURI_column_in_sheet(cls, data, filepath, headers, sheet):
        try:
            type_index = headers.index('typeURI')
        except ValueError:
            type_index = -1
        if type_index == -1:
            for row in data[1:5]:
                try:
                    type_index = row.index('typeURI')
                except ValueError:
                    type_index = -1
                if type_index != -1:
                    break
            sheet_name = str(sheet)[12:-2]
            if type_index == -1:
                raise NoTypeUriInExcelTabError(
                    message=f'Could not find typeURI within 5 rows in Excel tab {sheet_name} in file {filepath.name}',
                    file_path=filepath, tab=sheet_name)
            else:
                raise TypeUriNotInFirstRowError(
                    message=f'The typeURI is not in the first row in Excel tab {sheet_name} in file {filepath.name}.'
                            f' Please remove the excess rows', file_path=filepath, tab=sheet_name)
        return type_index

    def check_headers(self, headers, sheet, filepath, type_uri, model_directory):
        sheet_name = str(sheet)[12:-2]
        instance = dynamic_create_instance_from_uri(type_uri, model_directory=model_directory)
        error = InvalidColumnNamesInExcelTabError(
            message=f'There are invalid column names in Excel tab {sheet_name} in file {filepath.name}, see attribute '
                    f'bad_columns', file_path=filepath, tab=sheet_name)
        for header in headers:
            if header == 'typeURI':
                continue
            if header in ['bron.typeURI', 'doel.typeURI']:
                continue
            if header.startswith('[DEPRECATED] '):
                error.bad_columns.append(header)
                continue
            try:
                self.dotnotation_helper.get_attribute_by_dotnotation_instance(
                    instance_or_attribute=instance, dotnotation=header)
            except (AttributeError, DotnotationListOfListError):
                error.bad_columns.append(header)

        if len(error.bad_columns) > 0:
            raise error


