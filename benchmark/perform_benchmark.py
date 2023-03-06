import importlib
import os
import sys
import timeit
from pathlib import Path
from statistics import mean, stdev

from prettytable import prettytable



base_dir = os.path.dirname(os.path.realpath(__file__))

spec = importlib.util.spec_from_file_location('OtlmowConverter', Path(base_dir) / '../otlmow_converter/OtlmowConverter.py')
module = importlib.util.module_from_spec(spec)
sys.modules['OtlmowConverter'] = module
spec.loader.exec_module(module)


def load_assets():
    converter = module.OtlmowConverter()
    converter.create_assets_from_file(Path(base_dir) / 'files/all_classes.csv')


def load_assets2():
    converter = module.OtlmowConverter()
    converter.create_assets_from_file(Path(base_dir) / 'files/ten_random_classes.csv')


if __name__ == '__main__':
    result = timeit.repeat(load_assets, repeat=6, number=1)[1:]
    stdev1 = stdev(result)
    result2 = timeit.repeat(load_assets2, repeat=3, number=1)[1:]
    stdev2 = stdev(result2)

    with open("benchmark_results.txt", "w") as file:
        file.writelines(['Benchmarking results\n'])

        tb = prettytable.PrettyTable()
        tb.field_names = ["Format", "Read all classes", "Read 10 random classes"]
        tb.add_row(['CSV', f'{round(mean(result), 3)} +/- {round(stdev1, 3)}',
                    f'{round(mean(result2), 3)} +/- {round(stdev2, 3)}'])
        file.writelines(str(tb))
