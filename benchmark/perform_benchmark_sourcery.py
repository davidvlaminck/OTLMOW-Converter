import logging
import os
import shutil
import sys
import timeit
from collections import namedtuple
from pathlib import Path
from statistics import mean, stdev

from prettytable import PrettyTable

# allow relative import of otlmow_converter
base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(str(Path(base_dir) / '../'))
from otlmow_converter.OtlmowConverter import OtlmowConverter

REPEAT_TIMES = 2
logging.getLogger().setLevel(logging.ERROR)
csv_data = None


def read_assets(filepath: Path, results_dict: dict, read_data_key: str, **kwargs):
    results_dict[read_data_key] = OtlmowConverter.from_file_to_objects(filepath, **kwargs)


def write_assets(filepath: Path, results_dict: dict, read_data_key: str, **kwargs):
    OtlmowConverter.from_objects_to_file(file_path=filepath, sequence_of_objects=results_dict[read_data_key], **kwargs)


def time_read_assets(filepath: Path, results_dict: dict, **kwargs) -> None:
    read_data_key = 'read_data_ten_classes'
    if 'all_classes' in str(filepath):
        read_data_key = 'read_data_all_classes'
    print(f'reading {filepath}')
    result_times = timeit.repeat(
        lambda: read_assets(filepath=filepath, results_dict=results_dict, read_data_key=read_data_key, **kwargs),
        repeat=REPEAT_TIMES + 1, number=1)[1:]
    st_dev = stdev(result_times)
    results_dict[f'{read_data_key}_row'] = f'{round(mean(result_times), 3)} +/- {round(st_dev, 3)}'


def time_write_assets(filepath: Path, results_dict: dict, **kwargs) -> None:
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

    file_size = int(os.path.getsize(filepath) / 1024)
    results_dict[read_data_key.replace('read', 'write') + '_size'] = f'{file_size} kB'


if __name__ == '__main__':
    if not os.path.exists(Path(base_dir) / 'temp'):
        os.mkdir(Path(base_dir) / 'temp')

    FormatDetails = namedtuple('FormatDetails', ['Extension', 'Label', 'WriteArguments'])

    tb = PrettyTable()
    tb.field_names = ['Format', 'Read all classes', 'Write all classes', 'Size all classes',
                      'Read 10 random classes', 'Write 10 random classes', 'Size 10 random classes']

    formats = [
        FormatDetails(Extension='csv', Label='CSV', WriteArguments={'split_per_type': False}),
        # FormatDetails(Extension='json', Label='JSON', WriteArguments={}),
        # FormatDetails(Extension='xlsx', Label='Excel', WriteArguments={}),
        # FormatDetails(Extension='jsonld', Label='JSON-LD', WriteArguments={}),
        # FormatDetails(Extension='geojson', Label='GeoJSON', WriteArguments={}),
        # FormatDetails(Extension='ttl', Label='TTL', WriteArguments={'no_read': True})
    ]

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
               results_dict['write_data_all_classes_row'],
               results_dict['write_data_all_classes_size'],
               results_dict['read_data_ten_classes_row'],
               results_dict['write_data_ten_classes_row'],
               results_dict['write_data_ten_classes_size']]
        tb.add_row(row)

        if format_details.Extension == 'csv':
            csv_data = {'read_data_all_classes': results_dict['read_data_all_classes'],
                        'read_data_ten_classes': results_dict['read_data_ten_classes']}

        # Use PrettyTable for automatic formatting
        table = PrettyTable()
        table.field_names = [
            "Format", "Options",
            "All Size (kB)", "All Read (s)", "All Write (s)",
            "n", "10 Size (kB)", "10 Read (s)", "10 Write (s)"
        ]
        table.align = "r"
        table.align["Format"] = "l"
        table.align["Options"] = "l"
        table.align["n"] = "c"
        table.align["All Size (kB)"] = "r"
        table.align["10 Size (kB)"] = "r"
        table.align["All Read (s)"] = "r"
        table.align["All Write (s)"] = "r"
        table.align["10 Read (s)"] = "r"
        table.align["10 Write (s)"] = "r"
        rows = []

    for format_details in formats:
        results_dict = {}
        read_all_classes_file_name = Path(base_dir) / 'files/all_classes.json'
        ten_random_classes_file_name = Path(base_dir) / 'files/ten_random_classes.json'
        write_all_classes_file_name = Path(base_dir) / f'temp/all_classes.{format_details.Extension}'
        write_ten_random_classes_file_name = Path(base_dir) / f'temp/ten_random_classes.{format_details.Extension}'

        # Generate the data using OtlmowConverter.from_file_to_objects
        all_classes_data = OtlmowConverter.from_file_to_objects(read_all_classes_file_name)
        ten_random_classes_data = OtlmowConverter.from_file_to_objects(ten_random_classes_file_name)

        # Write and read for all_classes
        write_all_times = []
        for _ in range(REPEAT_TIMES):
            start = timeit.default_timer()
            OtlmowConverter.from_objects_to_file(file_path=write_all_classes_file_name,
                                                 sequence_of_objects=all_classes_data, **format_details.WriteArguments)
            elapsed = timeit.default_timer() - start
            write_all_times.append(elapsed)
        write_all_mean = round(mean(write_all_times), 3)
        write_all_stdev = round(stdev(write_all_times), 3) if len(write_all_times) > 1 else 0.0
        write_all = f"{write_all_mean} +/- {write_all_stdev}"
        size_all = f"{int(os.path.getsize(write_all_classes_file_name) / 1024)} kB"

        read_all_times = []
        for _ in range(REPEAT_TIMES):
            start = timeit.default_timer()
            OtlmowConverter.from_file_to_objects(write_all_classes_file_name, **format_details.WriteArguments)
            elapsed = timeit.default_timer() - start
            read_all_times.append(elapsed)
        read_all_mean = round(mean(read_all_times), 3)
        read_all_stdev = round(stdev(read_all_times), 3) if len(read_all_times) > 1 else 0.0
        read_all = f"{read_all_mean} +/- {read_all_stdev}"

        # Write and read for ten_random_classes, for 10, 100, 1000 objects per assettype
        for n_per_assettype in [10, 100, 1000]:
            from collections import defaultdict

            grouped = defaultdict(list)
            for obj in ten_random_classes_data:
                grouped[getattr(obj, 'typeURI', None)].append(obj)
            # Take n_per_assettype for each assettype
            selected = []
            for objs in grouped.values():
                selected.extend(objs[:n_per_assettype])
            # Write
            write_ten_times = []
            for _ in range(REPEAT_TIMES):
                start = timeit.default_timer()
                OtlmowConverter.from_objects_to_file(
                    file_path=write_ten_random_classes_file_name,
                    sequence_of_objects=selected,
                    **format_details.WriteArguments
                )
                elapsed = timeit.default_timer() - start
                write_ten_times.append(elapsed)
            write_ten_mean = round(mean(write_ten_times), 3)
            write_ten_stdev = round(stdev(write_ten_times), 3) if len(write_ten_times) > 1 else 0.0
            write_ten = f"{write_ten_mean} +/- {write_ten_stdev}"
            size_ten = f"{int(os.path.getsize(write_ten_random_classes_file_name) / 1024)} kB"

            # Read
            read_ten_times = []
            for _ in range(REPEAT_TIMES):
                start = timeit.default_timer()
                OtlmowConverter.from_file_to_objects(write_ten_random_classes_file_name,
                                                     **format_details.WriteArguments)
                elapsed = timeit.default_timer() - start
                read_ten_times.append(elapsed)
            read_ten_mean = round(mean(read_ten_times), 3)
            read_ten_stdev = round(stdev(read_ten_times), 3) if len(read_ten_times) > 1 else 0.0
            read_ten = f"{read_ten_mean} +/- {read_ten_stdev}"

            # Add row to PrettyTable
            table.add_row([
                format_details.Label,
                "",  # Options column
                size_all,
                read_all,
                write_all,
                n_per_assettype,
                size_ten,
                read_ten,
                write_ten
            ])

        # Write to file in the new format using PrettyTable
    with open(Path(base_dir) / 'benchmark_results.txt', "w") as file:
        file.write(str(table) + "\n")

    shutil.rmtree(Path(base_dir) / 'temp')