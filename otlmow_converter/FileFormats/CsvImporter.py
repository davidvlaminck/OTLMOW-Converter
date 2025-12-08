import ast
import csv
import logging
from asyncio import sleep
from datetime import datetime, date, time
from pathlib import Path
from typing import Iterable, Optional

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pa_csv
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, dynamic_create_instance_from_uri
from pyarrow._csv import read_csv, ParseOptions, ReadOptions, ConvertOptions

from otlmow_converter.AbstractImporter import AbstractImporter
from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.Exceptions.NoTypeUriInTableError import NoTypeUriInTableError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError
from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter
from otlmow_converter.FileFormats.PyArrowConverter import PyArrowConverter
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
    def to_objects(cls, filepath: Path, **kwargs: dict[str, object]) -> Iterable[OTLObject]:
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
        # Settings and defaults
        delimiter, quote_char = cls._get_delimiter_and_quote(kwargs)
        separator, cardinality_separator, cardinality_indicator, waarde_shortcut, \
            cast_list, cast_datetime, allow_non_otl_conform_attributes, \
            warn_for_non_otl_conform_attributes, contains_exactly_one_type = cls._get_options(kwargs)

        # Validation and normalization
        cls._validate_filepath(filepath)
        delimiter = cls._normalize_delimiter(delimiter)
        model_directory = kwargs.get('model_directory', None)

        # Single-type fast path
        if contains_exactly_one_type:
            return cls._convert_single_type_path(
                filepath=filepath,
                kwargs=kwargs,
                delimiter=delimiter,
                quote_char=quote_char,
                separator=separator,
                cardinality_indicator=cardinality_indicator,
                waarde_shortcut=waarde_shortcut,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
                model_directory=model_directory,
                cardinality_separator=cardinality_separator)

        # Multi-type detection
        try:
            type_uris = cls._read_unique_typeuris(filepath, delimiter, quote_char)
        except pa.lib.ArrowKeyError as e:
            cls.check_for_type_uri_in_first_five_rows_using_csv(delimiter, e, filepath, quote_char)
            raise

        if len(type_uris) == 1:
            return cls.to_objects(
                filepath=filepath, model_directory=model_directory, delimiter=delimiter, quote_char=quote_char,
                separator=separator, cardinality_indicator=cardinality_indicator,
                cardinality_separator=cardinality_separator, waarde_shortcut=waarde_shortcut,
                cast_datetime=cast_datetime, cast_list=cast_list, contains_exactly_one_type=True,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

        # Python fallback path
        return cls._python_fallback_to_objects(
            filepath=filepath,
            delimiter=delimiter,
            quote_char=quote_char,
            model_directory=model_directory,  # type: ignore[arg-type]
            separator=separator,
            cardinality_indicator=cardinality_indicator,
            waarde_shortcut=waarde_shortcut,
            cardinality_separator=cardinality_separator,
            cast_datetime=cast_datetime,
            cast_list=cast_list,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes
        )

    # ---------- helper methods ----------

    @classmethod
    def _get_delimiter_and_quote(cls, kwargs: Optional[dict[str, object]]) -> tuple[str, str]:
        delimiter = DELIMITER
        quote_char = '"'
        if kwargs is not None:
            if 'delimiter' in kwargs:
                delimiter = kwargs['delimiter']  # type: ignore[assignment]
            if 'quote_char' in kwargs:
                quote_char = kwargs['quote_char']  # type: ignore[assignment]
        return str(delimiter), str(quote_char)

    @classmethod
    def _get_options(cls, kwargs: dict[str, object] | None) -> tuple[str, str, str, bool, bool, bool, bool, bool, bool]:
        if kwargs is None:
            kwargs = {}
        separator = str(kwargs.get('separator', SEPARATOR))
        cardinality_separator = str(kwargs.get('cardinality_separator', CARDINALITY_SEPARATOR))
        cardinality_indicator = str(kwargs.get('cardinality_indicator', CARDINALITY_INDICATOR))
        waarde_shortcut = bool(kwargs.get('waarde_shortcut', WAARDE_SHORTCUT))
        cast_list = bool(kwargs.get('cast_list', CAST_LIST))
        cast_datetime = bool(kwargs.get('cast_datetime', CAST_DATETIME))
        allow_non_otl_conform_attributes = bool(kwargs.get('allow_non_otl_conform_attributes',
                                                           ALLOW_NON_OTL_CONFORM_ATTRIBUTES))
        warn_for_non_otl_conform_attributes = bool(kwargs.get('warn_for_non_otl_conform_attributes',
                                                              WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES))
        contains_exactly_one_type = bool(kwargs.get('contains_exactly_one_type', False))
        return (separator, cardinality_separator, cardinality_indicator, waarde_shortcut,
                cast_list, cast_datetime, allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes, contains_exactly_one_type)

    @classmethod
    def _validate_filepath(cls, filepath: Path) -> None:
        if filepath is None:
            raise ValueError(f'Can not write a file to: {filepath}')

    @classmethod
    def _normalize_delimiter(cls, delimiter: str) -> str:
        return ';' if delimiter == '' else delimiter

    @classmethod
    def _convert_single_type_path(cls, filepath: Path, kwargs: dict[str, object], delimiter: str, quote_char: str,
        separator: str, cardinality_indicator: str, waarde_shortcut: bool, allow_non_otl_conform_attributes: bool,
        warn_for_non_otl_conform_attributes: bool, model_directory: Path | None, cardinality_separator: str
                                  ) -> Iterable[OTLObject]:
        # Prevent double casting downstream
        if 'cast_list' in kwargs:
            kwargs['cast_list'] = False
        if 'cast_datetime' in kwargs:
            kwargs['cast_datetime'] = False

        first_row, headers = cls._read_first_row_and_headers(filepath, delimiter, quote_char)
        instance = dynamic_create_instance_from_uri(first_row['typeURI'], model_directory=model_directory)

        schema, headers_with_cardinality = cls._build_schema_for_headers(
            instance=instance,
            headers=headers,
            separator=separator,
            cardinality_indicator=cardinality_indicator,
            waarde_shortcut=waarde_shortcut,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
            filepath=filepath
        )
        missing_columns = cls._compute_missing_columns(first_row['typeURI'], headers)

        table = cls._read_csv_table_with_schema(filepath, delimiter, quote_char, schema)
        table = cls._apply_cardinality_splitting(table, headers_with_cardinality, cardinality_separator)
        table = cls._append_missing_columns_to_table(table, missing_columns)

        return PyArrowConverter.convert_table_to_objects(table=table, **kwargs)

    @classmethod
    def _read_first_row_and_headers(cls, filepath: Path, delimiter: str, quote_char: str
                                    ) -> tuple[dict[str, str], list[str]]:
        with open(filepath, encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=delimiter, quotechar=quote_char)
            first_row: dict[str, str] = next(reader)

        headers = list(first_row.keys())
        if 'typeURI' in headers:
            headers.remove('typeURI')
        else:
            cls.check_for_type_uri_in_first_five_rows_using_csv(delimiter, None, filepath, quote_char)
        return first_row, headers

    @classmethod
    def _build_schema_for_headers(
        cls, instance: OTLObject, headers: list[str], separator: str, cardinality_indicator: str,
        waarde_shortcut: bool, allow_non_otl_conform_attributes: bool, warn_for_non_otl_conform_attributes: bool,
        filepath: Path) -> tuple[pa.Schema, list[tuple[str, pa.DataType]]]:
        schema_list: list[tuple[str, pa.DataType]] = [('typeURI', pa.string())]
        headers_with_cardinality: list[tuple[str, pa.DataType]] = []

        for header in headers:
            try:
                attribute = DotnotationHelper.get_attribute_by_dotnotation(
                    instance, dotnotation=header, separator=separator,
                    cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut)
            except AttributeError as e:
                if e.args and e.args[0] == "'NoneType' object has no attribute 'field'":
                    if allow_non_otl_conform_attributes:
                        if warn_for_non_otl_conform_attributes:
                            logging.warning(
                                f'Warning: {e.args[0]}: {header} in file {filepath.name}, this is not OTL conform but will be loaded as string.'
                            )
                        schema_list.append((header, pa.string()))
                        if cardinality_indicator in header:
                            headers_with_cardinality.append((header, pa.list_(pa.string())))
                        continue
                    raise
                logging.error(f'Error while processing header {header} in file {filepath.name}: {e}')
                raise

            nt = attribute.field.native_type
            if cardinality_indicator in header:
                schema_list.append((header, pa.string()))
                if nt == str:
                    headers_with_cardinality.append((header, pa.list_(pa.string())))
                elif nt == int:
                    headers_with_cardinality.append((header, pa.list_(pa.int64())))
                elif nt == float:
                    headers_with_cardinality.append((header, pa.list_(pa.float64())))
                elif nt == bool:
                    headers_with_cardinality.append((header, pa.list_(pa.bool_())))
                elif nt == datetime:
                    headers_with_cardinality.append((header, pa.list_(pa.timestamp('ns'))))
                elif nt == time:
                    headers_with_cardinality.append((header, pa.list_(pa.time64('ns'))))
                elif nt == date:
                    headers_with_cardinality.append((header, pa.list_(pa.date32())))
                else:
                    raise NotImplementedError(
                        f'Unsupported native type for cardinality > 1: {nt} from {attribute.field.__class__.__name__} for header {header}'
                    )
            else:
                if nt == str:
                    schema_list.append((header, pa.string()))
                elif nt == int:
                    schema_list.append((header, pa.int64()))
                elif nt == float:
                    schema_list.append((header, pa.float64()))
                elif nt == bool:
                    schema_list.append((header, pa.bool_()))
                elif nt == datetime:
                    schema_list.append((header, pa.timestamp('ns')))
                elif nt == time:
                    schema_list.append((header, pa.time64('ns')))
                elif nt == date:
                    schema_list.append((header, pa.date32()))
                else:
                    raise NotImplementedError(
                        f'Unsupported native type: {nt} from {attribute.field.__class__.__name__} for header {header}'
                    )

        return pa.schema(schema_list), headers_with_cardinality

    @classmethod
    def _compute_missing_columns(cls, type_uri: str, headers: list[str]) -> list[str]:
        if type_uri == 'http://purl.org/dc/terms/Agent':
            needed = ['agentId.identificator', 'agentId.toegekendDoor']
        else:
            needed = ['assetId.identificator', 'assetId.toegekendDoor']
        return [c for c in needed if c not in headers]

    @classmethod
    def _read_csv_table_with_schema(
        cls, filepath: Path, delimiter: str, quote_char: str, schema: pa.Schema) -> pa.Table:
        include_columns = list(schema.names)  # projection pushdown
        parse_options = ParseOptions(delimiter=delimiter, quote_char=quote_char)
        convert_options = ConvertOptions(
            column_types=schema,
            include_columns=include_columns,
            null_values=["", "NULL", "null"],
            strings_can_be_null=True,
            # normalize boolean parsing to common variants
            true_values=["true", "True", "1", "Y", "Yes"],
            false_values=["false", "False", "0", "N", "No"]
        )
        table = read_csv(
            filepath,
            read_options=ReadOptions(use_threads=True, block_size=(8 << 20)),  # larger blocks for throughput
            parse_options=parse_options,
            convert_options=convert_options,
        )
        # Fewer chunks -> faster downstream ops
        return table.combine_chunks()

    @classmethod
    def _apply_cardinality_splitting(
        cls, table: pa.Table, headers_with_cardinality: list[tuple[str, pa.DataType]],
            cardinality_separator: str) -> pa.Table:
        if not headers_with_cardinality:
            return table
        for header, list_type in headers_with_cardinality:
            split_column = pa.compute.split_pattern(table[header], cardinality_separator)
            converted_data = split_column.cast(list_type)
            table = table.set_column(table.schema.get_field_index(header), header, converted_data)
        return table

    @classmethod
    def _append_missing_columns_to_table(cls, table: pa.Table, missing_columns: list[str]) -> pa.Table:
        if not missing_columns:
            return table
        for col in missing_columns:
            null_array = pa.nulls(len(table), type=pa.string())
            table = table.append_column(col, null_array)
        return table

    @classmethod
    def _read_unique_typeuris(cls, filepath: Path, delimiter: str, quote_char: str) -> set[str]:
        table_typeuri = pa_csv.read_csv(
            filepath,
            read_options=pa_csv.ReadOptions(),
            parse_options=pa_csv.ParseOptions(delimiter=delimiter, quote_char=quote_char),
            convert_options=pa_csv.ConvertOptions(include_columns=['typeURI'])
        )
        arr = table_typeuri["typeURI"].combine_chunks()
        uniques = pc.unique(arr).to_pylist()
        return {v for v in uniques if isinstance(v, str)}

    @classmethod
    def _python_fallback_to_objects(
        cls, filepath: Path, delimiter: str, quote_char: str, model_directory: Path | None, separator: str,
        cardinality_indicator: str, waarde_shortcut: bool, cardinality_separator: str, cast_datetime: bool,
        cast_list: bool,  allow_non_otl_conform_attributes: bool, warn_for_non_otl_conform_attributes: bool
    ) -> Iterable[OTLObject]:
        try:
            with open(filepath, encoding='utf-8') as file:
                csv_reader = csv.reader(file, delimiter=delimiter, quotechar=quote_char)
                data: list[list[object]] = [next(csv_reader)]
                for row in csv_reader:
                    r: list[object] = []
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
                message=f'The typeURI is not in the first row in file {filepath.name}. Please remove the excess rows',
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
                    message=f'The typeURI is not in the first row in file {filepath.name}. Please remove the excess rows',
                    file_path=filepath) from e
            raise TypeUriNotInFirstRowError(
                message=f'The typeURI is not in the first row in file {filepath.name}. Please remove the excess rows',
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
