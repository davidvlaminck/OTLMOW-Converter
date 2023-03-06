import os
import sys
import timeit
from pathlib import Path
from statistics import mean, stdev
from collections import namedtuple
from typing import Dict

from prettytable import prettytable

# relative import
base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(str(Path(base_dir) / '../'))
from otlmow_converter.OtlmowConverter import OtlmowConverter

REPEAT_TIMES = 5


def read_assets(filepath: Path, results_dict: Dict, read_data_key: str, **kwargs):
    converter = OtlmowConverter()
    results_dict[read_data_key] = converter.create_assets_from_file(filepath, **kwargs)


def write_assets(filepath: Path, results_dict: Dict, read_data_key: str, **kwargs):
    converter = OtlmowConverter()
    converter.create_file_from_assets(filepath, list_of_objects=results_dict[read_data_key], **kwargs)


def time_read_assets(filepath: Path, results_dict: Dict, **kwargs) -> None:
    read_data_key = 'read_data_ten_classes'
    if 'all_classes' in str(filepath):
        read_data_key = 'read_data_all_classes'
    result_times = timeit.repeat(
        lambda: read_assets(filepath=filepath, results_dict=results_dict, read_data_key=read_data_key, **kwargs),
        repeat=REPEAT_TIMES + 1, number=1)[1:]
    st_dev = stdev(result_times)
    results_dict[read_data_key + '_row'] = f'{round(mean(result_times), 3)} +/- {round(st_dev, 3)}'


def time_write_assets(filepath: Path, results_dict: Dict, **kwargs) -> None:
    read_data_key = 'read_data_ten_classes'
    if 'all_classes' in str(filepath):
        read_data_key = 'read_data_all_classes'
    result_times = timeit.repeat(
        lambda: write_assets(filepath=filepath, results_dict=results_dict, read_data_key=read_data_key, **kwargs),
        repeat=REPEAT_TIMES + 1, number=1)[1:]
    st_dev = stdev(result_times)
    results_dict[read_data_key.replace('read', 'write') + '_row'] = \
        f'{round(mean(result_times), 3)} +/- {round(st_dev, 3)}'


if __name__ == '__main__':
    FormatDetails = namedtuple('FormatDetails', ['Extension', 'Label', 'WriteArguments'])

    tb = prettytable.PrettyTable()
    tb.field_names = ['Format', 'Read all classes', 'Read 10 random classes', 'Write all classes',
                      'Write 10 random classes']

    formats = [FormatDetails(Extension='csv', Label='CSV', WriteArguments={'split_per_type': False}),
               FormatDetails(Extension='json', Label='JSON', WriteArguments={}),
               FormatDetails(Extension='xlsx', Label='Excel', WriteArguments={}),
               FormatDetails(Extension='json-ld', Label='JSON-LD', WriteArguments={}),
               FormatDetails(Extension='ttl', Label='TTL', WriteArguments={})]
    for format_details in formats:
        results_dict = {}
        read_all_classes_file_name = Path(base_dir) / f'files/all_classes.{format_details.Extension}'
        ten_random_classes_file_name = Path(base_dir) / f'files/ten_random_classes.{format_details.Extension}'
        write_all_classes_file_name = Path(base_dir) / f'temp/all_classes.{format_details.Extension}'
        write_ten_random_classes_file_name = Path(base_dir) / f'temp/ten_random_classes.{format_details.Extension}'

        for filepath in [read_all_classes_file_name, ten_random_classes_file_name]:
            time_read_assets(filepath=filepath, results_dict=results_dict)

        for filepath in [write_all_classes_file_name, write_ten_random_classes_file_name]:
            time_write_assets(filepath=filepath, results_dict=results_dict, **format_details.WriteArguments)

        row = [format_details.Label, results_dict['read_data_all_classes_row'],
               results_dict['read_data_ten_classes_row'], results_dict['write_data_all_classes_row'],
               results_dict['write_data_ten_classes_row']]
        tb.add_row(row)

    with open(Path(base_dir) / 'benchmark_results.txt', "w") as file:
        file.writelines(['Benchmarking results\n'])
        file.writelines(str(tb))
