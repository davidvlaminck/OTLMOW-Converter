import ast
import csv
import logging
from asyncio import sleep
from datetime import datetime, date, time
from pathlib import Path
from typing import Iterable

import pyarrow
import pyarrow.csv as pa_csv
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, dynamic_create_instance_from_uri
from pyarrow._csv import read_csv, ParseOptions, ReadOptions, ConvertOptions

from otlmow_converter.AbstractImporter import AbstractImporter
from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.Exceptions.NoTypeUriInTableError import NoTypeUriInTableError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError
from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter
from otlmow_converter.OtlmowConverter import to_objects
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
        """
        Reads a CSV file and converts it to a list of OTLObjects.
        :param filepath: The path to the CSV file.
        :param kwargs: Optional keyword arguments to customize the import process.
        - delimiter: The character used to separate values in the CSV file (default is ';').
        - quote_char: The character used to quote fields in the CSV file (default is '"').
        - separator: The character used to separate attributes in dot notation (default is '.').
        - cardinality_separator: The character used to separate values in a list (default is '|').
        - cardinality_indicator: The character used to indicate a list (default is '[]').
        - waarde_shortcut: Whether to use the waarde shortcut for simple types (default is True).
        - cast_list: Whether to cast list attributes to a list type (default is False).
        - cast_datetime: Whether to cast datetime attributes to a datetime type (default is False).
        - allow_non_otl_conform_attributes: Whether to allow attributes that are not OTL conform (default is True).
        - warn_for_non_otl_conform_attributes: Whether to warn for non-OTL conform attributes (default is True).
        - contains_exactly_one_type: If True, the CSV file is expected to contain only one type of OTLObject.
        :return: An iterable of OTLObjects.
        :raises ValueError: If the filepath is None or empty.
        :raises TypeUriNotInFirstRowError: If the typeURI is not found in the first row of the CSV file.
        :raises NoTypeUriInTableError: If the typeURI is not found within the first five rows of the CSV file.
        """
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
        contains_exactly_one_type = kwargs.get('contains_exactly_one_type', False)

        if filepath is None:
            raise ValueError(f'Can not write a file to: {filepath}')

        if delimiter == '':
            delimiter = ';'

        model_directory = None
        if kwargs is not None and 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']

        if contains_exactly_one_type:
            import pyarrow as pa
            import pyarrow.compute as pc

            # use pyarrow to read the csv file and infer the schema

            # try reading only the headers with csv:
            with open(filepath, encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=delimiter, quotechar=quote_char)
                first_row = next(reader)

            instance = dynamic_create_instance_from_uri(first_row['typeURI'], model_directory=model_directory)
            # get the headers from the first row
            headers = list(first_row.keys())
            if 'typeURI' in headers:
                headers.remove('typeURI')
            else:
                cls.check_for_type_uri_in_first_five_rows_using_csv(delimiter, None, filepath, quote_char)


            schema_list = [('typeURI', pa.string())]
            headers_with_cardinality = []
            for header in headers:
                try:
                    attribute = DotnotationHelper.get_attribute_by_dotnotation(
                        instance, dotnotation=header, separator=separator,
                        cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut)
                except AttributeError as e:
                    if e.args[0] == "'NoneType' object has no attribute 'field'":
                        if allow_non_otl_conform_attributes:
                            if warn_for_non_otl_conform_attributes:
                                logging.warning(f'Warning: {e.args[0]}: {header} in file {filepath.name}, this is not OTL conform but will be loaded as string.')
                            schema_list.append((header, pa.string()))
                            if cardinality_indicator in header:
                                headers_with_cardinality.append((header, pa.list_(pa.string())))
                            continue
                        else:
                            raise e

                if cardinality_indicator in header:
                    schema_list.append((header, pa.string()))
                    if attribute.field.native_type == str:
                        headers_with_cardinality.append((header, pa.list_(pa.string())))
                    elif attribute.field.native_type == int:
                        headers_with_cardinality.append((header, pa.list_(pa.int64())))
                    elif attribute.field.native_type == float:
                        headers_with_cardinality.append((header, pa.list_(pa.float64())))
                    elif attribute.field.native_type == bool:
                        headers_with_cardinality.append((header, pa.list_(pa.bool_())))
                    elif attribute.field.native_type == datetime:
                        headers_with_cardinality.append((header, pa.list_(pa.timestamp('ns'))))
                    elif attribute.field.native_type == time:
                        headers_with_cardinality.append((header, pa.list_(pa.time64('ns'))))
                    elif attribute.field.native_type == date:
                        headers_with_cardinality.append((header, pa.list_(pa.date32())))
                    else:
                        raise NotImplementedError(f'Unsupported native type for cardinality > 1: {attribute.field.native_type} from {attribute.field.__class__.__name__} for header {header}')
                elif attribute.field.native_type == str:
                    schema_list.append((header, pa.string()))
                elif attribute.field.native_type == int:
                    schema_list.append((header, pa.int64()))
                elif attribute.field.native_type == float:
                    schema_list.append((header, pa.float64()))
                elif attribute.field.native_type == bool:
                    schema_list.append((header, pa.bool_()))
                elif attribute.field.native_type == datetime:
                    schema_list.append((header, pa.timestamp('ns')))
                elif attribute.field.native_type == time:
                    schema_list.append((header, pa.time64('ns')))
                elif attribute.field.native_type == date:
                    schema_list.append((header, pa.date32()))
                else:
                    raise NotImplementedError(f'Unsupported native type: {attribute.field.native_type} from {attribute.field.__class__.__name__} for header {header}')

            missing_columns = []
            if 'assetId.identificator' not in headers:
                missing_columns.append('assetId.identificator')
            if 'assetId.toegekendDoor' not in headers:
                missing_columns.append('assetId.toegekendDoor')

            schema = pa.schema(schema_list)

            parse_options = ParseOptions(delimiter=delimiter, quote_char=quote_char)

            # Read the CSV file again with the specified schema
            # To ensure empty fields are read as nulls for string columns, also set strings_can_be_null=True
            table = read_csv(filepath,
                             read_options=ReadOptions(use_threads=True),
                             parse_options=parse_options,
                             convert_options=ConvertOptions(
                                 column_types=schema, null_values=[""], strings_can_be_null=True))


            for header_with_cardinality in headers_with_cardinality:
                split_column = pyarrow.compute.split_pattern(table[header_with_cardinality[0]], '|')
                converted_data = split_column.cast(header_with_cardinality[1])
                table = table.set_column(
                    table.schema.get_field_index(header_with_cardinality[0]),
                    header_with_cardinality[0], converted_data)

            if missing_columns:
                for col in missing_columns:
                    null_array = pa.array([None] * len(table), type=pa.string())
                    table = table.append_column(col, null_array)

            # Convert the table to a DataFrame
            df = table.to_pandas()
            return to_objects(df, model_directory=model_directory,
                              allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                              warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

        try:
            table_typeuri = pa_csv.read_csv(
                filepath,
                read_options=pa_csv.ReadOptions(),  # default, reads header
                parse_options=pa_csv.ParseOptions(
                    delimiter=delimiter,
                    quote_char=quote_char
                ),
                convert_options=pa_csv.ConvertOptions(include_columns=['typeURI'])
            )
        except pyarrow.lib.ArrowKeyError as e:
            cls.check_for_type_uri_in_first_five_rows_using_csv(delimiter, e, filepath, quote_char)
        type_uri_column = set(table_typeuri['typeURI'])

        if len(type_uri_column) == 1:
            return cls.to_objects(
                filepath=filepath, model_directory=model_directory, delimiter=delimiter, quote_char=quote_char,
                separator=separator, cardinality_indicator=cardinality_indicator,
                cardinality_separator=cardinality_separator, waarde_shortcut=waarde_shortcut,
                cast_datetime=cast_datetime, cast_list=cast_list, contains_exactly_one_type=True,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

        #
        # list_of_dicts = [
        #     {col: row[col] for col in table.column_names
        #      if row[col] not in [None, '', float('nan')] and not (isinstance(row[col], float) and math.isnan(row[col]))}
        #     for row in table.to_pylist()
        # ]
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
        #
        # return [DotnotationDictConverter.from_dict(
        #     input_dict=x, model_directory=model_directory, cast_list=cast_list,
        #     cast_datetime=cast_datetime,
        #     allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
        #     warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes, waarde_shortcut=waarde_shortcut,
        #     separator=separator, cardinality_indicator=cardinality_indicator, cardinality_separator=cardinality_separator) for x in
        #         list_of_dicts if x['typeURI'] != 'http://purl.org/dc/terms/Agent']

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
    def check_for_type_uri_in_first_five_rows_using_csv(cls, delimiter, e, filepath, quote_char):
        with open(filepath, encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=delimiter, quotechar=quote_char)
            for _ in range(5):
                try:
                    first_row = next(reader)
                    if 'typeURI' in first_row:
                        break
                except StopIteration:
                    if e is not None:
                        raise NoTypeUriInTableError(
                            message=f'Could not find typeURI within 5 rows in the csv file {filepath.name}',
                            file_path=filepath,) from e
                    raise NoTypeUriInTableError(
                        message=f'Could not find typeURI within 5 rows in the csv file {filepath.name}',
                        file_path=filepath)
            if e is not None:
                raise TypeUriNotInFirstRowError(
                    message=f'The typeURI is not in the first row in file {filepath.name}.'
                            f' Please remove the excess rows',
                    file_path=filepath) from e
            raise TypeUriNotInFirstRowError(
                message=f'The typeURI is not in the first row in file {filepath.name}.'
                        f' Please remove the excess rows',
                file_path=filepath)

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
