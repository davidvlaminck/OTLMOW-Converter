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


if __name__ == '__main__':
    if not os.path.exists(Path(base_dir) / 'temp'):
        os.mkdir(Path(base_dir) / 'temp')

    FormatDetails = namedtuple('FormatDetails', ['Extension', 'Label', 'WriteArguments'])

    tb = PrettyTable()
    tb.field_names = ['Format', 'Read all classes', 'Write all classes', 'Size all classes',
                      'Read 10 random classes', 'Write 10 random classes', 'Size 10 random classes']

    formats = [
        FormatDetails(Extension='csv', Label='CSV', WriteArguments={'split_per_type': True}),
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
        filepaths_written_all = []
        for _ in range(REPEAT_TIMES):
            start = timeit.default_timer()
            filepaths_all = OtlmowConverter.from_objects_to_file(
                file_path=write_all_classes_file_name,
                sequence_of_objects=all_classes_data, **format_details.WriteArguments)
            elapsed = timeit.default_timer() - start
            write_all_times.append(elapsed)
            filepaths_written_all = filepaths_all

        write_all_mean = round(mean(write_all_times), 3)
        write_all_stdev = round(stdev(write_all_times), 3) if len(write_all_times) > 1 else 0.0
        write_all = f"{write_all_mean} +/- {write_all_stdev}"

        # Sum the file sizes of all written files
        total_size = 0
        if isinstance(filepaths_written_all, (list, tuple)):
            for fp in filepaths_written_all:
                total_size += int(os.path.getsize(fp))
        elif filepaths_written_all:
            total_size = int(os.path.getsize(filepaths_written_all))
        else:
            total_size = int(os.path.getsize(filepath))
        size_all = f'{int(total_size / 1024)} kB'

        read_all_times = []
        for _ in range(REPEAT_TIMES):
            start = timeit.default_timer()
            # Read all files returned by from_objects_to_file
            if isinstance(filepaths_written_all, (list, tuple)):
                for fp in filepaths_written_all:
                    OtlmowConverter.from_file_to_objects(fp, **format_details.WriteArguments)
            else:
                OtlmowConverter.from_file_to_objects(write_all_classes_file_name, **format_details.WriteArguments)
            elapsed = timeit.default_timer() - start
            read_all_times.append(elapsed)
        read_all_mean = round(mean(read_all_times), 3)
        read_all_stdev = round(stdev(read_all_times), 3) if len(read_all_times) > 1 else 0.0
        read_all = f"{read_all_mean} +/- {read_all_stdev}"

        from collections import defaultdict

        # Group all ten_random_classes_data by typeURI once
        grouped = defaultdict(list)
        for obj in ten_random_classes_data:
            grouped[getattr(obj, 'typeURI', None)].append(obj)

        ten_rows = []
        n_values = [10, 100, 1000]

        for n_per_assettype in n_values:
            # For each n, select up to n_per_assettype objects per assettype
            selected = [item for objs in grouped.values() for item in objs[:n_per_assettype]]

            # Write
            write_ten_times = []
            filepaths_written = []
            for _ in range(REPEAT_TIMES):
                start = timeit.default_timer()
                filepaths = OtlmowConverter.from_objects_to_file(
                    file_path=write_ten_random_classes_file_name,
                    sequence_of_objects=selected,
                    **format_details.WriteArguments
                )
                elapsed = timeit.default_timer() - start
                write_ten_times.append(elapsed)
                # Save the filepaths returned (tuple)
                filepaths_written = filepaths

            write_ten_mean = round(mean(write_ten_times), 3)
            write_ten_stdev = round(stdev(write_ten_times), 3) if len(write_ten_times) > 1 else 0.0
            write_ten = f"{write_ten_mean} +/- {write_ten_stdev}"

            # Sum the file sizes of all written files
            total_size = 0
            if isinstance(filepaths_written, (list, tuple)):
                for fp in filepaths_written:
                    total_size += int(os.path.getsize(fp))
            elif filepaths_written:
                total_size = int(os.path.getsize(filepaths_written))
            else:
                total_size = int(os.path.getsize(filepath))
            size_ten = f'{int(total_size / 1024)} kB'

            # Read
            read_ten_times = []
            for _ in range(REPEAT_TIMES):
                start = timeit.default_timer()
                # Read all files returned by from_objects_to_file
                if isinstance(filepaths_written, (list, tuple)):
                    for fp in filepaths_written:
                        OtlmowConverter.from_file_to_objects(fp, **format_details.WriteArguments)
                else:
                    OtlmowConverter.from_file_to_objects(write_ten_random_classes_file_name, **format_details.WriteArguments)
                elapsed = timeit.default_timer() - start
                read_ten_times.append(elapsed)
            read_ten_mean = round(mean(read_ten_times), 3)
            read_ten_stdev = round(stdev(read_ten_times), 3) if len(read_ten_times) > 1 else 0.0
            read_ten = f"{read_ten_mean} +/- {read_ten_stdev}"

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

        # Format the options column
        if format_details.WriteArguments and isinstance(format_details.WriteArguments, dict):
            options_str = ",".join(f"{k}={v}" for k, v in format_details.WriteArguments.items())
        else:
            options_str = ""
        ten_rows[mid][1] = options_str

        ten_rows[mid][2] = size_all
        ten_rows[mid][3] = read_all
        ten_rows[mid][4] = write_all

        for row in ten_rows:
            table.add_row(row)

    # Write to file in the new format using PrettyTable
    table_str = str(table)
    lines = table_str.splitlines()

    # Find the header (second row, index 1)
    header_idx = 1
    header_line = lines[header_idx]

    # Remove "All/" and "10/" from the header, but replace with spaces to keep alignment
    col_titles = [col for col in header_line.strip('|').split('|')]
    new_header = []
    all_indices = []
    ten_indices = []
    for i, col in enumerate(col_titles):
        if col.strip().startswith("All/"):
            new_header.append(col.replace("All/", " " * 4))
            all_indices.append(i)
        elif col.strip().startswith("10/"):
            new_header.append(col.replace("10/", " " * 3))
            ten_indices.append(i)
        else:
            new_header.append(col)


        # Build the multi-line header
        # First line: empty for Format/Options, then "All" over the All columns, "10" over the 10 columns
        # Use the same width as the columns for the spaces
        def col_width(col):
            return len(col)


        # Calculate column widths from the border line
        border_line = lines[0]
        col_widths = [len(part) for part in border_line.split('+')[1:-1]]

        # Build the first multi-header line: two empty cells, then "All" spanning 3 columns, then "10" spanning 4 columns
        first_multi_header_cells = []
        first_multi_header_cells.append(" " * col_widths[0])
        first_multi_header_cells.append(" " * col_widths[1])
        # "All" spans columns 2,3,4
        all_span = sum(col_widths[2:5]) + 2  # 2 separators between 3 columns
        first_multi_header_cells.append("All".center(all_span))
        # "10" spans columns 5,6,7,8
        ten_span = sum(col_widths[5:]) + 3  # 3 separators between 4 columns
        first_multi_header_cells.append("10".center(ten_span))
        # Fill to match the number of columns
        while len(first_multi_header_cells) < len(col_widths):
            first_multi_header_cells.append(" " * col_widths[len(first_multi_header_cells)])

        # Now, build the line with | separators
        # The first two columns are empty, then "All" (spanning 3), then "10" (spanning 4)
        first_multi_header = "|"
        first_multi_header += first_multi_header_cells[0] + "|"
        first_multi_header += first_multi_header_cells[1] + "|"
        first_multi_header += first_multi_header_cells[2] + "|"
        first_multi_header += first_multi_header_cells[3] + "|"

        # Rebuild the header line with the new column names (without All/ and 10/)
        new_header_line = "|".join([col if col.startswith(" ") else col.strip() for col in new_header])
        new_header_line = "|" + new_header_line + "|"

    # Write the new table to file
    with open(Path(base_dir) / 'benchmark_results.txt', "w") as file:
        file.write(lines[0] + "\n")  # top border
        file.write(first_multi_header.rstrip() + "\n")
        file.write(lines[0] + "\n")  # border
        file.write(new_header_line + "\n")
        for l in lines[2:]:
            file.write(l + "\n")

    shutil.rmtree(Path(base_dir) / 'temp')