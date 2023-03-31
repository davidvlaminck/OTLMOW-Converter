import logging
import os
import shutil
import sys
import timeit
from pathlib import Path
from statistics import mean, stdev
from collections import namedtuple
from typing import Dict
import logging
from prettytable import prettytable

# allow relative import of otlmow_converter
base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(str(Path(base_dir) / '../'))
from otlmow_converter.OtlmowConverter import OtlmowConverter

REPEAT_TIMES = 5
logging.getLogger().setLevel(logging.ERROR)
csv_data = None


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
    print(f'reading {filepath}')
    result_times = timeit.repeat(
        lambda: read_assets(filepath=filepath, results_dict=results_dict, read_data_key=read_data_key, **kwargs),
        repeat=REPEAT_TIMES + 1, number=1)[1:]
    st_dev = stdev(result_times)
    results_dict[read_data_key + '_row'] = f'{round(mean(result_times), 3)} +/- {round(st_dev, 3)}'


def time_write_assets(filepath: Path, results_dict: Dict, **kwargs) -> None:
    read_data_key = 'read_data_ten_classes'
    if 'all_classes' in str(filepath):
        read_data_key = 'read_data_all_classes'
    if 'no_read' in kwargs and kwargs['no_read']:
        kwargs.pop('no_read')
        results_dict.update(csv_data)

    print(f'writing to {filepath}')
    result_times = timeit.repeat(
        lambda: write_assets(filepath=filepath, results_dict=results_dict, read_data_key=read_data_key, **kwargs),
        repeat=REPEAT_TIMES + 1, number=1)[1:]
    st_dev = stdev(result_times)
    results_dict[read_data_key.replace('read', 'write') + '_row'] = \
        f'{round(mean(result_times), 3)} +/- {round(st_dev, 3)}'


if __name__ == '__main__':
    if not os.path.exists(Path(base_dir) / 'temp'):
        os.mkdir(Path(base_dir) / 'temp')

    FormatDetails = namedtuple('FormatDetails', ['Extension', 'Label', 'WriteArguments'])

    tb = prettytable.PrettyTable()
    tb.field_names = ['Format', 'Read all classes', 'Read 10 random classes', 'Write all classes',
                      'Write 10 random classes']

    formats = [
        FormatDetails(Extension='csv', Label='CSV', WriteArguments={'split_per_type': False}),
        FormatDetails(Extension='json', Label='JSON', WriteArguments={}),
        FormatDetails(Extension='xlsx', Label='Excel', WriteArguments={}),
        FormatDetails(Extension='jsonld', Label='JSON-LD', WriteArguments={}),
        FormatDetails(Extension='ttl', Label='TTL', WriteArguments={'no_read': True})]

    for format_details in formats:
        results_dict = {}
        read_all_classes_file_name = Path(base_dir) / f'files/all_classes.{format_details.Extension}'
        ten_random_classes_file_name = Path(base_dir) / f'files/ten_random_classes.{format_details.Extension}'
        write_all_classes_file_name = Path(base_dir) / f'temp/all_classes.{format_details.Extension}'
        write_ten_random_classes_file_name = Path(base_dir) / f'temp/ten_random_classes.{format_details.Extension}'

        if 'no_read' in format_details.WriteArguments:
            results_dict['read_data_all_classes_row'] = 'N/A'
            results_dict['read_data_ten_classes_row'] = 'N/A'
        else:
            for filepath in [read_all_classes_file_name, ten_random_classes_file_name]:
                time_read_assets(filepath=filepath, results_dict=results_dict)

        for filepath in [write_all_classes_file_name, write_ten_random_classes_file_name]:
            time_write_assets(filepath=filepath, results_dict=results_dict, **format_details.WriteArguments)

        row = [format_details.Label, results_dict['read_data_all_classes_row'],
               results_dict['read_data_ten_classes_row'], results_dict['write_data_all_classes_row'],
               results_dict['write_data_ten_classes_row']]
        tb.add_row(row)

        if format_details.Extension == 'csv':
            csv_data = {'read_data_all_classes': results_dict['read_data_all_classes'],
                        'read_data_ten_classes': results_dict['read_data_ten_classes']}

    with open(Path(base_dir) / 'benchmark_results.txt', "w") as file:
        file.writelines(['Benchmarking results\n'])
        file.writelines(str(tb))

    shutil.rmtree(Path(base_dir) / 'temp')
