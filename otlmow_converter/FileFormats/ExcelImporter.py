import os
import warnings
from pathlib import Path

import openpyxl
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.Exceptions.NonStandardAttributeWarning import NonStandardAttributeWarning

from otlmow_converter.AbstractImporter import AbstractImporter
from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError
from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.Exceptions.InvalidColumnNamesInExcelTabError import InvalidColumnNamesInExcelTabError
from otlmow_converter.Exceptions.NoTypeUriInExcelTabError import NoTypeUriInExcelTabError
from otlmow_converter.Exceptions.NoTypeUriInTableError import NoTypeUriInTableError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError
from otlmow_converter.Exceptions.UnknownExcelError import UnknownExcelError
from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter
from otlmow_converter.SettingsManager import GlobalVariables, load_settings

load_settings()

xlsx_settings = GlobalVariables.settings['formats']['xlsx']
xlsx_dotnotation_settings = xlsx_settings['dotnotation']
SEPARATOR = xlsx_dotnotation_settings['separator']
CARDINALITY_SEPARATOR = xlsx_dotnotation_settings['cardinality_separator']
CARDINALITY_INDICATOR = xlsx_dotnotation_settings['cardinality_indicator']
WAARDE_SHORTCUT = xlsx_dotnotation_settings['waarde_shortcut']
CAST_LIST = xlsx_settings['cast_list']
CAST_DATETIME = xlsx_settings['cast_datetime']
ALLOW_NON_OTL_CONFORM_ATTRIBUTES = xlsx_settings['allow_non_otl_conform_attributes']
WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES = xlsx_settings['warn_for_non_otl_conform_attributes']


class ExcelImporter(AbstractImporter):
    @classmethod
    def to_objects(cls, filepath: Path = None, **kwargs) -> list:
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f'Could not load the file at: {filepath}')

        separator = kwargs.get('separator', SEPARATOR)
        cardinality_indicator = kwargs.get('cardinality_indicator', CARDINALITY_INDICATOR)
        cardinality_separator = kwargs.get('cardinality_separator', CARDINALITY_SEPARATOR)
        waarde_shortcut = kwargs.get('waarde_shortcut', WAARDE_SHORTCUT)
        cast_list = kwargs.get('cast_list', CAST_LIST)
        cast_datetime = kwargs.get('cast_datetime', CAST_DATETIME)
        allow_non_otl_conform_attributes = kwargs.get('allow_non_otl_conform_attributes',
                                                      ALLOW_NON_OTL_CONFORM_ATTRIBUTES)
        warn_for_non_otl_conform_attributes = kwargs.get('warn_for_non_otl_conform_attributes',
                                                         WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES)

        model_directory = None
        if kwargs is not None and 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']

        data = cls.get_data_dict_from_file_path(filepath=filepath)

        list_of_objects = []
        exception_group = ExceptionsGroup(message=f'Failed to create objects from Excel file {filepath}')
        for sheet, sheet_data in data.items():
            try:
                if len(sheet_data) == 0:
                    if sheet_data == []:
                        continue
                    raise NoTypeUriInExcelTabError(
                        message=f'Could not find typeURI within 5 rows in Excel tab {sheet} in file {filepath.name}',
                        file_path=filepath, tab=sheet)
                headers = sheet_data[0]
                type_uri_index = cls.get_index_of_typeURI_column_in_sheet(
                    filepath=filepath, sheet=sheet, headers=headers, data=sheet_data)
                cls.check_headers(headers=headers, sheet=sheet, filepath=filepath,
                                  type_uri=sheet_data[1][type_uri_index], model_directory=model_directory,
                                  cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                                  separator=separator,
                                  allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                  warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

                list_of_dicts = DotnotationTableConverter.transform_2d_sequence_to_list_of_dicts(
                    two_d_sequence=sheet_data, empty_string_equals_none=True)
                list_of_objects.extend(DotnotationTableConverter.get_data_from_table(
                    table_data=list_of_dicts, model_directory=model_directory,
                    separator=separator, cardinality_indicator=cardinality_indicator,
                    waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
                    cast_datetime=cast_datetime, cast_list=cast_list,
                    allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                    warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes))
            except TypeUriNotInFirstRowError:
                exception_group.add_exception(TypeUriNotInFirstRowError(
                    message=f'The typeURI is not in the first row in file {filepath.name}.'
                            f' Please remove the excess rows',
                    file_path=filepath, tab=sheet
                ))
            except NoTypeUriInTableError:
                exception_group.add_exception(NoTypeUriInExcelTabError(
                    message=f'Could not find typeURI within 5 rows in the file {filepath.name}',
                    file_path=filepath, tab=sheet
                ))
            except BaseException as ex:
                exception_group.add_exception(UnknownExcelError(original_exception=ex, tab=sheet))

        if len(exception_group.exceptions) > 0:
            raise exception_group

        return list_of_objects

    @classmethod
    def get_data_dict_from_file_path(cls, filepath) -> dict[str, list[list]]:
        data = {}
        book = openpyxl.load_workbook(filepath, data_only=True, read_only=True)

        for sheet in book.worksheets:
            sheet_name = sheet.title
            data[sheet_name] = []
            for row in sheet.rows:
                row_data = []
                for cell in row:
                    if cell.value in {'True', 'TRUE', 'False', 'FALSE'}:
                        row_data.append(cell.value.lower() == 'true')
                    else:
                        row_data.append(cell.value)
                data[sheet_name].append(row_data)

        book.close()
        return data

    @classmethod
    def get_index_of_typeURI_column_in_sheet(cls, filepath: Path, sheet: str,  headers: list[str],
                                             data: list[list[str]]) -> int:
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

    @staticmethod
    def check_headers(headers: list[str], sheet: str, filepath: Path, type_uri: str, model_directory: Path,
                      cardinality_indicator: str = CARDINALITY_INDICATOR, waarde_shortcut: bool = WAARDE_SHORTCUT,
                      separator: str = SEPARATOR,
                      allow_non_otl_conform_attributes: bool = ALLOW_NON_OTL_CONFORM_ATTRIBUTES,
                      warn_for_non_otl_conform_attributes: bool = WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES) -> None:
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
                DotnotationHelper.get_attribute_by_dotnotation(
                    instance_or_attribute=instance, dotnotation=header, separator=separator,
                    cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut)
            except DotnotationListOfListError:
                error.bad_columns.append(header)
            except AttributeError:
                if not allow_non_otl_conform_attributes:
                    error.bad_columns.append(header)
                elif warn_for_non_otl_conform_attributes:
                    warnings.warn(
                        message=f'{header} is a non standardized attribute of {type_uri}. '
                                f'The attribute will be added on the instance.',
                        stacklevel=2,
                        category=NonStandardAttributeWarning)

        if len(error.bad_columns) > 0:
            raise error
