import csv
import os
from pathlib import Path
from typing import Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from otlmow_converter.Exceptions.NoTypeUriInTableError import NoTypeUriInTableError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError
from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

csv.field_size_limit(2147483647)


load_settings()

csv_settings = GlobalVariables.settings['formats']['csv']
csv_dotnotation_settings = csv_settings['dotnotation']
SEPARATOR = csv_dotnotation_settings['separator']
CARDINALITY_SEPARATOR = csv_dotnotation_settings['cardinality_separator']
CARDINALITY_INDICATOR = csv_dotnotation_settings['cardinality_indicator']
WAARDE_SHORTCUT = csv_dotnotation_settings['waarde_shortcut']
LIST_AS_STRING = csv_settings['list_as_string']
DATETIME_AS_STRING = csv_settings['datetime_as_string']
ALLOW_NON_OTL_CONFORM_ATTRIBUTES = csv_settings['allow_non_otl_conform_attributes']
WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES = csv_settings['warn_for_non_otl_conform_attributes']
DELIMITER = csv_settings['delimiter']


class CsvImporter:
    @classmethod
    def to_objects(cls, filepath: Path, **kwargs) -> Iterable[OTLObject]:
        delimiter = DELIMITER
        split_per_type = True
        quote_char = '"'

        if kwargs is not None:
            if 'delimiter' in kwargs:
                delimiter = kwargs['delimiter']
            if 'split_per_type' in kwargs:
                split_per_type = kwargs['split_per_type']
            if 'quote_char' in kwargs:
                quote_char = kwargs['quote_char']
        else:
            kwargs = {}

        separator = kwargs.get('separator', SEPARATOR)
        cardinality_separator = kwargs.get('cardinality_separator', CARDINALITY_SEPARATOR)
        cardinality_indicator = kwargs.get('cardinality_indicator', CARDINALITY_INDICATOR)
        waarde_shortcut = kwargs.get('waarde_shortcut', WAARDE_SHORTCUT)
        list_as_string = kwargs.get('list_as_string', LIST_AS_STRING)
        datetime_as_string = kwargs.get('datetime_as_string', DATETIME_AS_STRING)
        allow_non_otl_conform_attributes = kwargs.get('allow_non_otl_conform_attributes',
                                                      ALLOW_NON_OTL_CONFORM_ATTRIBUTES)
        warn_for_non_otl_conform_attributes = kwargs.get('warn_for_non_otl_conform_attributes',
                                                         WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES)

        if filepath is None:
            raise ValueError(f'Can not write a file to: {filepath}')

        if delimiter == '':
            delimiter = ';'

        model_directory = None
        if kwargs is not None and 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']

        try:
            with open(filepath, encoding='utf-8') as file:
                csv_reader = csv.reader(file, delimiter=delimiter, quotechar=quote_char)
                data = list(csv_reader)

                list_of_dicts = DotnotationTableConverter.transform_2d_sequence_to_list_of_dicts(
                    two_d_sequence=data, empty_string_equals_none=True)
                return DotnotationTableConverter.get_data_from_table(
                    table_data=list_of_dicts, convert_strings_to_types=True, model_directory=model_directory)
        except TypeUriNotInFirstRowError as e:
            raise TypeUriNotInFirstRowError(
                message=f'The typeURI is not in the first row in file {filepath.name}.'
                f' Please remove the excess rows',
                file_path=filepath,
            ) from e
        except NoTypeUriInTableError as e:
            raise NoTypeUriInTableError(
                message=f'Could not find typeURI within 5 rows in the csv file {filepath.name}',
                file_path=filepath,
            ) from e
