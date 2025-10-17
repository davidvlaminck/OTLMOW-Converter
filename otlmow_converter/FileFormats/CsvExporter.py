
import csv
from asyncio import sleep
from pathlib import Path
from typing import Iterable
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_converter.AbstractExporter import AbstractExporter
from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter
from otlmow_converter.FileFormats.PyArrowConverter import PyArrowConverter
from otlmow_converter.SettingsManager import load_settings, GlobalVariables
from pyarrow import Table
import pyarrow as pa
import pyarrow.csv as pacsv

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


class CsvExporter(AbstractExporter):
    @classmethod
    def from_objects(cls, sequence_of_objects: Iterable[OTLObject], filepath: Path, **kwargs) -> tuple[Path]:
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

        if not split_per_type:
            table = PyArrowConverter.convert_objects_to_single_table(
                list_of_objects=sequence_of_objects,
                separator=separator, cardinality_separator=cardinality_separator,
                cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cast_list=cast_list, cast_datetime=cast_datetime,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
                avoid_multiple_types_in_single_column=True)
            CsvExporter.from_pyarrow_table_to_file(table, Path(filepath), delimiter=delimiter)
            return (filepath,)
        else:
            multi_table_dict = PyArrowConverter.convert_objects_to_multiple_tables(
                list_of_objects=sequence_of_objects,
                separator=separator, cardinality_separator=cardinality_separator,
                cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cast_list=cast_list, cast_datetime=cast_datetime,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

            created_filepaths = []
            for short_uri, table_data in multi_table_dict.items():
                specific_filename = (f'{filepath.stem}_' + short_uri.replace('#', '_') + filepath.suffix)
                created_filepath = Path(filepath.parent / specific_filename)

                cls.from_pyarrow_table_to_file(
                    table=table_data, filepath=created_filepath, delimiter=delimiter)
                created_filepath.touch()
                created_filepaths.append(created_filepath)
        return tuple(created_filepaths)

    @classmethod
    async def from_objects_async(cls, sequence_of_objects: Iterable[OTLObject], filepath: Path, **kwargs) -> tuple[Path]:
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

        if not split_per_type:
            single_table = await DotnotationTableConverter.get_single_table_from_data_async(
                list_of_objects=sequence_of_objects,
                separator=separator, cardinality_separator=cardinality_separator,
                cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cast_list=cast_list, cast_datetime=cast_datetime,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

            data = await DotnotationTableConverter.transform_list_of_dicts_to_2d_sequence_async(
                list_of_dicts=single_table, empty_string_equals_none=True, separator=separator)
            cls._write_file(file_location=filepath, data=data, delimiter=delimiter, quote_char=quote_char)
            filepath.touch()
            return (filepath,)

        multi_table_dict = await DotnotationTableConverter.get_tables_per_type_from_data_async(
            sequence_of_objects=sequence_of_objects,
            separator=separator, cardinality_separator=cardinality_separator,
            cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
            cast_list=cast_list, cast_datetime=cast_datetime,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

        created_filepaths = []
        for short_uri, table_data in multi_table_dict.items():
            data = await DotnotationTableConverter.transform_list_of_dicts_to_2d_sequence_async(
                list_of_dicts=table_data, empty_string_equals_none=True, separator=separator)
            specific_filename = (f'{filepath.stem}_' + short_uri.replace('#', '_') + filepath.suffix)
            created_filepath = Path(filepath.parent / specific_filename)
            await sleep(0)

            cls._write_file(file_location=created_filepath, data=data,
                            delimiter=delimiter, quote_char=quote_char)
            created_filepath.touch()
            created_filepaths.append(created_filepath)
        return tuple(created_filepaths)

    @classmethod
    def from_pyarrow_table_to_file(cls, table: Table, filepath: Path, delimiter: str = None) -> Path:
        """
        Write a pyarrow.Table to a CSV file.
        Ensures 'typeURI', 'assetId.identificator', and 'assetId.toegekendDoor' are the first columns,
        adding them as empty columns if missing.
        """
        if delimiter is None:
            delimiter = DELIMITER or ';'

        required_first = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor']
        table_colnames = table.schema.names
        if 'agentId.identificator' in table_colnames:
            required_first = ['typeURI', 'agentId.identificator', 'agentId.toegekendDoor']
        num_rows = table.num_rows

        # Add missing required columns as empty string columns
        new_fields = list(table.schema)
        new_columns = list(table.itercolumns())
        for col in required_first:
            if col not in table_colnames:
                new_fields.append(pa.field(col, pa.string()))
                new_columns.append(pa.array([None] * num_rows))

        # Build a new table with all columns (original + missing)
        full_table = pa.table(new_columns, names=[f.name for f in new_fields])

        # Reorder columns: required_first, then the rest (excluding duplicates)
        all_names = full_table.schema.names
        rest = sorted(name for name in all_names if name not in required_first)
        final_order = required_first + rest
        reordered_columns = [full_table.column(name) for name in final_order]

        final_table = pa.table(reordered_columns, names=final_order)

        write_options = pacsv.WriteOptions(delimiter=delimiter)
        with open(filepath, "wb") as f:
            pacsv.write_csv(final_table, f, write_options=write_options)
        filepath.touch()
        return filepath

    @classmethod
    def _write_file(cls, file_location: Path, data: Iterable[Iterable], delimiter: str, quote_char: str) -> None:
        with open(file_location, "w", newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file, delimiter=delimiter, quotechar=quote_char, quoting=csv.QUOTE_MINIMAL)
            for line in data:
                csv_writer.writerow(line)