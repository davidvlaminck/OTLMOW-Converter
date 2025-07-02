import itertools
import os
import random
import time
from pathlib import Path

import pytest
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_class_dict, get_hardcoded_relation_dict

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.OtlmowConverter import OtlmowConverter

base_dir = os.path.dirname(os.path.realpath(__file__))


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def instantiate_all():
    start = time.time()

    class_dict = get_hardcoded_class_dict()

    all_instances_list = []
    for class_uri, class_info in class_dict.items():
        if class_uri == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBetrokkene':
            continue
        if class_uri.startswith('https://lgc.'):
            continue
        if class_info['abstract']:
            continue
        instance = dynamic_create_instance_from_uri(class_uri)
        instance.fill_with_dummy_data()
        DotnotationHelper.clear_list_of_list_attributes(instance)
        all_instances_list.append(instance)

    classes_to_instantiate = []
    while len(classes_to_instantiate) < 10:
        class_uri = random.choice(list(class_dict.keys()))
        if class_uri in get_hardcoded_relation_dict():
            continue
        if class_uri.startswith('https://lgc.'):
            continue
        class_info = class_dict[class_uri]
        if class_info['abstract']:
            continue

        classes_to_instantiate.append(class_uri)

    random_10_class = []
    for class_uri, _ in itertools.product(classes_to_instantiate, range(1000)):
        instance = dynamic_create_instance_from_uri(class_uri)
        instance.fill_with_dummy_data()
        DotnotationHelper.clear_list_of_list_attributes(instance)
        random_10_class.append(instance)

    OtlmowConverter.from_objects_to_file(sequence_of_objects=all_instances_list,
                                         file_path=(Path(base_dir) / 'files/all_classes.csv'), split_per_type=False)
    OtlmowConverter.from_objects_to_file(sequence_of_objects=all_instances_list,
                                         file_path=(Path(base_dir) / 'files/all_classes.json'))
    OtlmowConverter.from_objects_to_file(sequence_of_objects=all_instances_list,
                                         file_path=(Path(base_dir) / 'files/all_classes.xlsx'))
    OtlmowConverter.from_objects_to_file(sequence_of_objects=all_instances_list,
                                         file_path=(Path(base_dir) / 'files/all_classes.geojson'))
    OtlmowConverter.from_objects_to_file(sequence_of_objects=all_instances_list,
                                         file_path=(Path(base_dir) / 'files/all_classes.jsonld'))
    # ttl
    OtlmowConverter.from_objects_to_file(sequence_of_objects=random_10_class,
                                         file_path=(Path(base_dir) / 'files/ten_random_classes.csv'), split_per_type=False)
    OtlmowConverter.from_objects_to_file(sequence_of_objects=random_10_class,
                                         file_path=(Path(base_dir) / 'files/ten_random_classes.json'))
    OtlmowConverter.from_objects_to_file(sequence_of_objects=random_10_class,
                                         file_path=(Path(base_dir) / 'files/ten_random_classes.xlsx'))
    OtlmowConverter.from_objects_to_file(sequence_of_objects=random_10_class,
                                         file_path=(Path(base_dir) / 'files/ten_random_classes.geojson'))
    OtlmowConverter.from_objects_to_file(sequence_of_objects=random_10_class,
                                         file_path=(Path(base_dir) / 'files/ten_random_classes.jsonld'))

    end = time.time()
    print(f'Time: {round(end - start, 2)}')


def return_all_benchmark_file_paths():
    """Reads all files in the benchmark/files directory and returns a list of Path objects."""
    files_dir = Path(base_dir) / 'files'
    return [f for f in files_dir.iterdir() if f.is_file()]


def read_all_files():
    for file_path in return_all_benchmark_file_paths():
        try:
            OtlmowConverter.from_file_to_objects(file_path)
        except Exception as ex:
            print(f'Error reading file {file_path}: {ex}')
            continue


if __name__ == '__main__':
    instantiate_all()
    read_all_files()
