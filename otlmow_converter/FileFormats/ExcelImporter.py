import os
from pathlib import Path
from typing import Dict, List, Sequence

import openpyxl
from otlmow_model.OtlmowModel.Helpers.AssetCreator import dynamic_create_instance_from_uri

from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError
from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.Exceptions.InvalidColumnNamesInExcelTabError import InvalidColumnNamesInExcelTabError
from otlmow_converter.Exceptions.NoTypeUriInExcelTabError import NoTypeUriInExcelTabError
from otlmow_converter.Exceptions.NoTypeUriInTableError import NoTypeUriInTableError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError
from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter


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

        self.dotnotation_table_converter = DotnotationTableConverter()
        self.dotnotation_table_converter.load_settings(xls_settings['dotnotation'])

    def import_file(self, filepath: Path = None, **kwargs) -> List:
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f'Could not load the file at: {filepath}')

        model_directory = None
        if kwargs is not None and 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']
        self.dotnotation_table_converter.model_directory = model_directory

        data = self.get_data_dict_from_file_path(filepath=filepath)

        list_of_objects = []
        exception_group = ExceptionsGroup(message=f'Failed to create objects from Excel file {filepath}')
        for sheet, sheet_data in data.items():
            try:
                if len(sheet_data) == 0:
                    raise NoTypeUriInExcelTabError(
                        message=f'Could not find typeURI within 5 rows in Excel tab {sheet} in file {filepath.name}',
                        file_path=filepath, tab=sheet)
                headers = sheet_data[0]
                type_uri_index = self.get_index_of_typeURI_column_in_sheet(
                    filepath=filepath, sheet=sheet, headers=headers, data=sheet_data)
                self.check_headers(headers=headers, sheet=sheet, filepath=filepath,
                                   type_uri=sheet_data[1][type_uri_index], model_directory=model_directory)

                list_of_dicts = self.dotnotation_table_converter.transform_2d_sequence_to_list_of_dicts(
                    two_d_sequence=sheet_data, empty_string_equals_none=True)
                list_of_objects.extend(self.dotnotation_table_converter.get_data_from_table(
                    table_data=list_of_dicts, convert_strings_to_types=True))
            except TypeUriNotInFirstRowError :
                exception_group.add_exception(TypeUriNotInFirstRowError(
                    message=f'The typeURI is not in the first row in file {filepath.name}.'
                            f' Please remove the excess rows',
                    file_path=filepath, tab=sheet
                ))
            except NoTypeUriInTableError:
                exception_group.add_exception(NoTypeUriInTableError(
                    message=f'Could not find typeURI within 5 rows in the csv file {filepath.name}',
                    file_path=filepath, tab=sheet
                ))
            except BaseException as ex:
                exception_group.add_exception(ex)

        if len(exception_group.exceptions) > 0:
            raise exception_group

        return list_of_objects

    @classmethod
    def get_data_dict_from_file_path(cls, filepath) -> Dict[str, List[List]]:
        data = {}
        book = openpyxl.load_workbook(filepath, data_only=True, read_only=True)

        for sheet in book.worksheets:
            sheet_name = str(sheet)[12:-2]
            data[sheet_name] = [[cell.value for cell in row] for row in sheet.rows]

        book.close()
        return data

    @classmethod
    def get_index_of_typeURI_column_in_sheet(cls, filepath: Path, sheet: str,  headers: List[str],
                                             data: List[List[str]]) -> int:
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
            if type_index == -1:
                raise NoTypeUriInExcelTabError(
                    message=f'Could not find typeURI within 5 rows in Excel tab {sheet} in file {filepath.name}',
                    file_path=filepath, tab=sheet)
            else:
                raise TypeUriNotInFirstRowError(
                    message=f'The typeURI is not in the first row in Excel tab {sheet} in file {filepath.name}.'
                            f' Please remove the excess rows', file_path=filepath, tab=sheet)
        return type_index

    def check_headers(self, headers: List[str], sheet: str, filepath: Path, type_uri: str, model_directory: Path):
        instance = dynamic_create_instance_from_uri(type_uri, model_directory=model_directory)
        error = InvalidColumnNamesInExcelTabError(
            message=f'There are invalid column names in Excel tab {sheet} in file {filepath.name}, see attribute '
                    f'bad_columns', file_path=filepath, tab=sheet)
        for header in headers:
            if header == 'typeURI':
                continue
            if header in ['bron.typeURI', 'doel.typeURI']:
                continue
            if header.startswith('[DEPRECATED] '):
                error.bad_columns.append(header)
                continue
            try:
                self.dotnotation_table_converter.dotnotation_helper.get_attribute_by_dotnotation_instance(
                    instance_or_attribute=instance, dotnotation=header)
            except (AttributeError, DotnotationListOfListError):
                error.bad_columns.append(header)

        if len(error.bad_columns) > 0:
            raise error


