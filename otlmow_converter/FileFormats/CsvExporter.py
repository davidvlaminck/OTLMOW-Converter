import csv
from pathlib import Path
from typing import Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from otlmow_converter.AbstractExporter import AbstractExporter
from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

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
    def from_objects(cls, sequence_of_objects: Iterable[OTLObject], filepath: Path, **kwargs) -> None:
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
            single_table = DotnotationTableConverter.get_single_table_from_data(
                list_of_objects=sequence_of_objects,
                separator=separator, cardinality_separator=cardinality_separator,
                cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cast_list=cast_list, cast_datetime=cast_datetime,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

            data = DotnotationTableConverter.transform_list_of_dicts_to_2d_sequence(
                list_of_dicts=single_table, empty_string_equals_none=True)
            cls._write_file(file_location=filepath, data=data, delimiter=delimiter, quote_char=quote_char)
            return

        multi_table_dict = DotnotationTableConverter.get_tables_per_type_from_data(
            sequence_of_objects=sequence_of_objects,
            separator=separator, cardinality_separator=cardinality_separator,
            cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
            cast_list=cast_list, cast_datetime=cast_datetime,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

        for short_uri, table_data in multi_table_dict.items():
            data = DotnotationTableConverter.transform_list_of_dicts_to_2d_sequence(
                list_of_dicts=table_data, empty_string_equals_none=True)
            specific_filename = (f'{filepath.stem}_' + short_uri.replace('#', '_') + filepath.suffix)

            cls._write_file(file_location=Path(filepath.parent / specific_filename), data=data,
                            delimiter=delimiter, quote_char=quote_char)

    @classmethod
    def _write_file(cls, file_location: Path, data: Iterable[Iterable], delimiter: str, quote_char: str) -> None:
        with open(file_location, "w", newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file, delimiter=delimiter, quotechar=quote_char, quoting=csv.QUOTE_MINIMAL)
            for line in data:
                csv_writer.writerow(line)
