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

REPEAT_TIMES = 5
logging.getLogger().setLevel(logging.ERROR)
csv_data = None


def read_assets(filepath: Path, results_dict: dict, read_data_key: str, **kwargs):
    results_dict[read_data_key] = OtlmowConverter.from_file_to_objects(filepath, **kwargs)


def write_assets(filepath: Path, results_dict: dict, read_data_key: str, **kwargs):
    return OtlmowConverter.from_objects_to_file(file_path=filepath, sequence_of_objects=results_dict[read_data_key], **kwargs)


def benchmark_write_read(data, file_path, write_args, repeat_times):
    filepaths_written = []
    write_times = []
    for _ in range(repeat_times):
        elapsed, filepaths = _timed_write(data, file_path, write_args)
        write_times.append(elapsed)
        filepaths_written = filepaths  # always use the latest written files

    write_result = _format_mean_stdev(write_times)
    size_result = _get_total_size(filepaths_written, file_path)

    read_times = []
    for _ in range(repeat_times):
        elapsed = _timed_read(filepaths_written, file_path, write_args)
        read_times.append(elapsed)
    read_result = _format_mean_stdev(read_times)

    return write_result, size_result, read_result

def _timed_write(data, file_path, write_args):
    start = timeit.default_timer()
    filepaths = OtlmowConverter.from_objects_to_file(
        file_path=file_path,
        sequence_of_objects=data,
        **write_args
    )
    elapsed = timeit.default_timer() - start
    # Always return a list for consistency
    if isinstance(filepaths, (list, tuple)):
        filepaths_list = list(filepaths)
    else:
        filepaths_list = [filepaths]
    return elapsed, filepaths_list

def _timed_read(filepaths_written, file_path, write_args):
    start = timeit.default_timer()
    if filepaths_written:
        for fp in filepaths_written:
            OtlmowConverter.from_file_to_objects(fp, **write_args)
    else:
        OtlmowConverter.from_file_to_objects(file_path, **write_args)
    return timeit.default_timer() - start

def _format_mean_stdev(times):
    m = round(mean(times), 3)
    s = round(stdev(times), 3) if len(times) > 1 else 0.0
    return f"{m} +/- {s}"

def _get_total_size(filepaths_written, fallback_path):
    total_size = sum(os.path.getsize(fp) for fp in filepaths_written if fp and os.path.exists(fp))
    if not total_size and os.path.exists(fallback_path):
        total_size = os.path.getsize(fallback_path)
    return f'{max(1, int(total_size / 1024)) if total_size else 0}'

def get_options_str(write_args):
    if write_args and isinstance(write_args, dict):
        return ",".join(f"{k}={v}" for k, v in write_args.items())
    return ""

def group_by_type_uri(data):
    from collections import defaultdict
    grouped = defaultdict(list)
    for obj in data:
        grouped[obj.typeURI].append(obj)
    return grouped

# Write to file in the new format using PrettyTable
def build_multiline_header(table):
    table_str = str(table)
    lines = table_str.splitlines()

    # Find the header (second row, index 1)
    header_idx = 1
    header_line = lines[header_idx]

    # Remove "All/" and "10/" from the header, but replace with spaces to keep alignment
    col_titles = list(header_line.strip('|').split('|'))
    new_header = []
    all_indices = []
    ten_indices = []
    for i, col in enumerate(col_titles):
        if col.strip().startswith("All/"):
            new_header.append(col.replace("All/", " " * 2) + '  ')
            all_indices.append(i)
        elif col.strip().startswith("10/"):
            new_header.append(col.replace("10/", " " * 1)  + '  ')
            ten_indices.append(i)
        else:
            new_header.append(col)

    # Calculate column widths from the border line
    border_line = lines[0]
    col_widths = [len(part) for part in border_line.split('+')[1:-1]]

    # "All" spans columns 2,3,4
    all_span = sum(col_widths[2:5]) + 2  # 2 separators between 3 columns
    # "10" spans columns 5,6,7,8
    ten_span = sum(col_widths[5:]) + 3  # 3 separators between 4 columns
    first_multi_header_cells = [
        " " * col_widths[0],
        " " * col_widths[1],
        "All".center(all_span),
        "10".center(ten_span),
    ]
    # Fill to match the number of columns
    while len(first_multi_header_cells) < len(col_widths):
        first_multi_header_cells.append(" " * col_widths[len(first_multi_header_cells)])

    # Now, build the line with | separators
    first_multi_header = "|"
    first_multi_header += f"{first_multi_header_cells[0]}|"
    first_multi_header += f"{first_multi_header_cells[1]}|"
    first_multi_header += f"{first_multi_header_cells[2]}|"
    first_multi_header += f"{first_multi_header_cells[3]}|"

    # Rebuild the header line with the new column names (without All/ and 10/)
    new_header_line = "|".join([col if col.startswith(" ") else col.strip() for col in new_header])
    new_header_line = f"|{new_header_line}|"

    return lines, first_multi_header, new_header_line


if __name__ == '__main__':
    if not os.path.exists(Path(base_dir) / 'temp'):
        os.mkdir(Path(base_dir) / 'temp')

    FormatDetails = namedtuple('FormatDetails', ['Extension', 'Label', 'WriteArguments'])

    tb = PrettyTable()
    tb.field_names = ['Format', 'Read all classes', 'Write all classes', 'Size all classes',
                      'Read 10 random classes', 'Write 10 random classes', 'Size 10 random classes']

    formats = [
        FormatDetails(Extension='csv', Label='CSV', WriteArguments={'split_per_type': True, 'contains_exactly_one_type' : True}),
        FormatDetails(Extension='csv', Label='CSV', WriteArguments={'split_per_type': False}),
        FormatDetails(Extension='json', Label='JSON', WriteArguments={}),
        FormatDetails(Extension='xlsx', Label='Excel', WriteArguments={}),
        FormatDetails(Extension='jsonld', Label='JSON-LD', WriteArguments={}),
        FormatDetails(Extension='geojson', Label='GeoJSON', WriteArguments={}),
        # FormatDetails(Extension='ttl', Label='TTL', WriteArguments={'no_read': True})
    ]

    # Use PrettyTable for automatic formatting
    table = PrettyTable()
    table.field_names = [
        "Format", "Options",
        "All/Size (kB)", "All/Read (s)", "All/Write (s)",
        "n", "10/Size (kB)", "10/Read (s)", "10/Write (s)"
    ]


    rows = []
    filepath = ''

    for format_details in formats:
        print(f'format: {format_details.Extension}')
        results_dict = {}
        read_all_classes_file_name = Path(base_dir) / 'files/all_classes.json'
        ten_random_classes_file_name = Path(base_dir) / 'files/ten_random_classes.json'
        write_all_classes_file_name = Path(base_dir) / f'temp/all_classes.{format_details.Extension}'
        write_ten_random_classes_file_name = Path(base_dir) / f'temp/ten_random_classes.{format_details.Extension}'

        # Generate the data using OtlmowConverter.from_file_to_objects
        all_classes_data = OtlmowConverter.from_file_to_objects(read_all_classes_file_name)
        ten_random_classes_data = OtlmowConverter.from_file_to_objects(ten_random_classes_file_name)

        # Write and read for all_classes
        write_all, size_all, read_all = benchmark_write_read(
            all_classes_data, write_all_classes_file_name, format_details.WriteArguments, REPEAT_TIMES
        )

        # Group all ten_random_classes_data by typeURI once
        grouped = group_by_type_uri(ten_random_classes_data)

        ten_rows = []
        n_values = [10, 100, 1000]
        for n_per_assettype in n_values:
            # For each n, select up to n_per_assettype objects per assettype
            selected = [item for objs in grouped.values() for item in objs[:n_per_assettype]]

            write_ten, size_ten, read_ten = benchmark_write_read(
                selected, write_ten_random_classes_file_name, format_details.WriteArguments, REPEAT_TIMES
            )

            # Prepare row, but leave Format/All columns empty except for the middle row
            ten_rows.append([
                "",  # Format
                "",  # Options
                "",  # size_all
                "",  # read_all
                "",  # write_all
                n_per_assettype,
                size_ten,
                read_ten,
                write_ten
            ])

        # Set the middle row to have the Format/All columns and the options string
        mid = len(ten_rows) // 2
        ten_rows[mid][0] = format_details.Label
        ten_rows[mid][1] = get_options_str(format_details.WriteArguments)
        ten_rows[mid][2] = size_all
        ten_rows[mid][3] = read_all
        ten_rows[mid][4] = write_all

        for row in ten_rows:
            table.add_row(row)

    # Write the new table to file with horizontal dividers between file formats
    lines, first_multi_header, new_header_line = build_multiline_header(table)
    divider = lines[0]
    data_lines = lines[2:]  # skip top border and header

    with open(Path(base_dir) / 'benchmark_results.txt', "w") as file:
        file.write(divider + "\n")  # top border
        file.write(first_multi_header.rstrip() + "\n")
        file.write(divider + "\n")  # border
        file.write(new_header_line + "\n")
        for i, l in enumerate(data_lines):
            file.write(l + "\n")
            # Insert divider after every 3 lines (for n_values = [10, 100, 1000])
            if i % 3 == 0 and i != 0 and i+2 < len(data_lines):
                file.write(divider + "\n")

    shutil.rmtree(Path(base_dir) / 'temp')