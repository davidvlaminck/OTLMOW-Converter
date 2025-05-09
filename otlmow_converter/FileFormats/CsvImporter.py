import ast
import csv
import math
#from line_profiler_pycharm import profile
import re
from asyncio import sleep
from pathlib import Path
from typing import Iterable
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from pyarrow._csv import read_csv, ParseOptions, ReadOptions, ConvertOptions

from otlmow_converter.AbstractImporter import AbstractImporter
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
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
CAST_LIST = csv_settings['cast_list']
CAST_DATETIME = csv_settings['cast_datetime']
ALLOW_NON_OTL_CONFORM_ATTRIBUTES = csv_settings['allow_non_otl_conform_attributes']
WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES = csv_settings['warn_for_non_otl_conform_attributes']
DELIMITER = csv_settings['delimiter']


class CsvImporter(AbstractImporter):
    @classmethod
    def to_objects(cls, filepath: Path, **kwargs) -> Iterable[OTLObject]:
        delimiter = DELIMITER
        quote_char = '"'

        if kwargs is not None:
            if 'delimiter' in kwargs:
                delimiter = kwargs['delimiter']
            if 'quote_char' in kwargs:
                quote_char = kwargs['quote_char']
        else:
            kwargs = {}

        separator = kwargs.get('separator', SEPARATOR)
        cardinality_separator = kwargs.get('cardinality_separator', CARDINALITY_SEPARATOR)
        cardinality_indicator = kwargs.get('cardinality_indicator', CARDINALITY_INDICATOR)
        waarde_shortcut = kwargs.get('waarde_shortcut', WAARDE_SHORTCUT)
        cast_list = kwargs.get('cast_list', CAST_LIST)
        cast_datetime = kwargs.get('cast_datetime', CAST_DATETIME)
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

        # try reading only the headers with csv:
        # with open('your_file.csv', mode='r') as file:
        #     reader = csv.reader(file)
        #     column_names = next(reader)

        # then set the schema with pyarrow using the headers
        # Define the schema with specific columns as strings and others to be inferred
        # schema = pa.schema([
        #     ('column1', pa.string()),  # Read 'column1' as string
        #     ('column2', pa.string()),  # Read 'column2' as string
        #     # Add more columns as needed, or leave them out to be inferred
        # ])

        # only works if all objects have the same typeURI

        import pyarrow as pa
        parse_options = ParseOptions(delimiter=delimiter, quote_char=quote_char)

        # Read the CSV file to infer the schema
        infer_table = read_csv(filepath, read_options=ReadOptions(autogenerate_column_names=False, use_threads=True,
                                                                  skip_rows_after_names=10000),
                               parse_options=parse_options)

        # Dynamically create a schema with all fields as strings
        schema = pa.schema([(name, pa.string()) for name in infer_table.column_names])

        # Read the CSV file again with the specified schema
        table = read_csv(filepath,
                         read_options=ReadOptions(column_names=schema.names, use_threads=True, skip_rows=1),
                         parse_options=parse_options,
                         convert_options=ConvertOptions(column_types=schema))


        list_of_dicts = [
            {col: row[col] for col in table.column_names
             if row[col] not in [None, '', float('nan')] and not (isinstance(row[col], float) and math.isnan(row[col]))}
            for row in table.to_pylist()
        ]
        #
        # list_of_dicts = [row._asdict() for row in df.itertuples(index=False)]
        #
        # # Convert the list of dictionaries to a list of OTLObjects
        # # and handle the conversion of empty strings to None
        # # exclude agents
        #
        # def filter_dict(d):
        #     return {k: v for k, v in d.items() if
        #                 v not in [None, '', float('nan')] and not (isinstance(v, float) and math.isnan(v))}

        return [DotnotationDictConverter.from_dict(
            input_dict=x, model_directory=model_directory, cast_list=cast_list,
            cast_datetime=cast_datetime,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes, waarde_shortcut=waarde_shortcut,
            separator=separator, cardinality_indicator=cardinality_indicator, cardinality_separator=cardinality_separator) for x in
                list_of_dicts if x['typeURI'] != 'http://purl.org/dc/terms/Agent']


        try:
            with open(filepath, encoding='utf-8') as file:
                csv_reader = csv.reader(file, delimiter=delimiter, quotechar=quote_char)
                data = [next(csv_reader)]
                for row in csv_reader:
                    r = []
                    for d in row:
                        if d is None:
                            r.append(None)
                        elif d == 'True':
                            r.append(True)
                        elif d == 'False':
                            r.append(False)
                        else:
                            r.append(d)
                    data.append(r)

                list_of_dicts = DotnotationTableConverter.transform_2d_sequence_to_list_of_dicts(
                    two_d_sequence=data, empty_string_equals_none=True)
                return DotnotationTableConverter.get_data_from_table(
                    table_data=list_of_dicts, model_directory=model_directory,
                    separator=separator, cardinality_indicator=cardinality_indicator,
                    waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
                    cast_datetime=cast_datetime, cast_list=cast_list,
                    allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                    warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
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

    @classmethod
    async def to_objects_async(cls, filepath: Path, **kwargs) -> Iterable[OTLObject]:
        delimiter = DELIMITER
        quote_char = '"'

        if kwargs is not None:
            if 'delimiter' in kwargs:
                delimiter = kwargs['delimiter']
            if 'quote_char' in kwargs:
                quote_char = kwargs['quote_char']
        else:
            kwargs = {}

        separator = kwargs.get('separator', SEPARATOR)
        cardinality_separator = kwargs.get('cardinality_separator', CARDINALITY_SEPARATOR)
        cardinality_indicator = kwargs.get('cardinality_indicator', CARDINALITY_INDICATOR)
        waarde_shortcut = kwargs.get('waarde_shortcut', WAARDE_SHORTCUT)
        cast_list = kwargs.get('cast_list', CAST_LIST)
        cast_datetime = kwargs.get('cast_datetime', CAST_DATETIME)
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
                data = [next(csv_reader)]
                for row in csv_reader:
                    await sleep(0)
                    r = []
                    for d in row:
                        try:
                            r.append(ast.literal_eval(d))
                        except (SyntaxError, ValueError):
                            r.append(str(d))
                    data.append(r)

                list_of_dicts = await DotnotationTableConverter.transform_2d_sequence_to_list_of_dicts_async(
                    two_d_sequence=data, empty_string_equals_none=True)
                return await DotnotationTableConverter.get_data_from_table_async(
                    table_data=list_of_dicts, model_directory=model_directory,
                    separator=separator, cardinality_indicator=cardinality_indicator,
                    waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
                    cast_datetime=cast_datetime, cast_list=cast_list,
                    allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                    warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
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
