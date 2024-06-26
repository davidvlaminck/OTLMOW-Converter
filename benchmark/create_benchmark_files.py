import itertools
import os
import random
import time
from os.path import isfile
from pathlib import Path

import pytest
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import dynamic_create_instance_from_ns_and_name

from otlmow_converter.OtlmowConverter import OtlmowConverter

base_dir = os.path.dirname(os.path.realpath(__file__))


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def instantiate_all():
    classes_to_instantiate = {}
    start = time.time()

    class_location = Path('../venv2/lib/python3.11/site-packages/otlmow_model/OtlmowModel/Classes/')
    installatie_location = class_location / 'Installatie'
    onderdeel_location = class_location / 'Onderdeel'
    levenscyclus_location = class_location / 'Levenscyclus'
    proefenmeting_location = class_location / 'ProefEnMeting'

    for dir_location in [installatie_location, onderdeel_location, levenscyclus_location, proefenmeting_location]:
        for f in os.listdir(dir_location):
            if not isfile(dir_location / f):
                continue
            class_name = f[:-3]
            classes_to_instantiate[class_name] = (dir_location.stem, class_name)

    classes_to_instantiate['ActivityComplex'] = ('ImplementatieElement', 'ActivityComplex')
    classes_to_instantiate['ElectricityAppurtenance'] = ('ImplementatieElement', 'ElectricityAppurtenance')
    classes_to_instantiate['Derdenobject'] = ('ImplementatieElement', 'Derdenobject')
    classes_to_instantiate['ElectricityCable'] = ('ImplementatieElement', 'ElectricityCable')
    classes_to_instantiate['Pipe'] = ('ImplementatieElement', 'Pipe')
    classes_to_instantiate['TelecommunicationsAppurtenance'] = ('ImplementatieElement', 'TelecommunicationsAppurtenance')
    classes_to_instantiate['TelecommunicationsCable'] = ('ImplementatieElement', 'TelecommunicationsCable')

    all_instances_list = []
    for class_name, class_tuple in classes_to_instantiate.items():
        if class_name == 'HeeftBetrokkene':
            continue
        instance = create_dummy_instance(class_tuple[0], class_tuple[1])
        all_instances_list.append(instance)

    random_10_class_names = []
    while len(random_10_class_names) < 10:
        class_tuple = random.choice(list(classes_to_instantiate.values()))
        if class_tuple[1] == 'HeeftBetrokkene':
            continue
        random_10_class_names.append(class_tuple)

    random_10_class = []
    for class_tuple, _ in itertools.product(random_10_class_names, range(1000)):
        instance = create_dummy_instance(class_tuple[0], class_tuple[1])
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


def create_dummy_instance(namespace: str, class_name: str):
    instance = dynamic_create_instance_from_ns_and_name(namespace, class_name)
    instance.fill_with_dummy_data()
    return instance


if __name__ == '__main__':
    instantiate_all()
