import os
import random
import time
from os.path import isfile
from pathlib import Path

import cachetools

from otlmow_converter.OtlmowConverter import OtlmowConverter


def instantiate_all():
    start = time.time()
    classes_to_instantiate = {}
    class_location = Path('../venv/lib/python3.10/site-packages/otlmow_model/Classes/')
    installatie_location = class_location / 'Installatie'
    onderdeel_location = class_location / 'Onderdeel'
    levenscyclus_location = class_location / 'Levenscyclus'
    proefenmeting_location = class_location / 'ProefEnMeting'

    for dir_location in [installatie_location, onderdeel_location, levenscyclus_location, proefenmeting_location]:
        for f in os.listdir(dir_location):
            f = str(f)
            if not isfile(dir_location / f):
                continue
            classes_to_instantiate[Path(f).stem] = Path(dir_location / Path(f).stem).resolve()

    classes_to_instantiate['ActivityComplex'] = class_location / 'ImplementatieElement' / 'ActivityComplex'
    classes_to_instantiate[
        'ElectricityAppurtenance'] = class_location / 'ImplementatieElement' / 'ElectricityAppurtenance'
    classes_to_instantiate['Derdenobject'] = class_location / 'ImplementatieElement' / 'Derdenobject'
    classes_to_instantiate['ElectricityCable'] = class_location / 'ImplementatieElement' / 'ElectricityCable'
    classes_to_instantiate['Pipe'] = class_location / 'ImplementatieElement' / 'Pipe'
    classes_to_instantiate[
        'TelecommunicationsAppurtenance'] = class_location / 'ImplementatieElement' / 'TelecommunicationsAppurtenance'
    classes_to_instantiate[
        'TelecommunicationsCable'] = class_location / 'ImplementatieElement' / 'TelecommunicationsCable'

    all_instances_list = []
    for class_name, file_path in classes_to_instantiate.items():
        if class_name == 'HeeftBetrokkene':
            continue
        instance = create_dummy_instance(class_name, file_path)
        all_instances_list.append(instance)

    random_10_class_names = []
    while len(random_10_class_names) < 10:
        class_name = random.choice(list(classes_to_instantiate.keys()))
        if class_name == 'HeeftBetrokkene':
            continue
        random_10_class_names.append(class_name)

    random_10_class = []
    for class_name in random_10_class_names:
        for _ in range(1000):
            instance = create_dummy_instance(class_name, classes_to_instantiate[class_name])
            random_10_class.append(instance)

    converter = OtlmowConverter()
    converter.create_file_from_assets(Path('all_classes.csv'), list_of_objects=all_instances_list, split_per_type=False)
    converter.create_file_from_assets(Path('all_classes.json'), list_of_objects=all_instances_list)
    converter.create_file_from_assets(Path('all_classes.xlsx'), list_of_objects=all_instances_list)
    converter.create_file_from_assets(Path('all_classes.jsonld'), list_of_objects=all_instances_list)
    converter.create_file_from_assets(Path('all_classes.ttl'), list_of_objects=all_instances_list)
    converter.create_file_from_assets(Path('ten_random_classes.csv'), list_of_objects=random_10_class,
                                      split_per_type=False)
    converter.create_file_from_assets(Path('ten_random_classes.json'), list_of_objects=random_10_class)
    converter.create_file_from_assets(Path('ten_random_classes.xlsx'), list_of_objects=random_10_class)
    converter.create_file_from_assets(Path('ten_random_classes.ttl'), list_of_objects=random_10_class)
    converter.create_file_from_assets(Path('ten_random_classes.jsonld'), list_of_objects=random_10_class)

    end = time.time()
    print(f'Time: {round(end - start, 2)}')


def create_dummy_instance(class_name, file_path):
    class_ = get_class_from_fp_and_name(class_name, file_path)
    instance = class_()
    instance.fill_with_dummy_data()
    return instance


@cachetools.cached(cache={})
def get_class_from_fp_and_name(class_name, file_path):
    try:
        import_path = f'{file_path.parts[-3]}.{file_path.parts[-2]}.{file_path.parts[-1]}'
        if 'otlmow_model' not in import_path:
            import_path = 'otlmow_model.' + import_path
        py_mod = __import__(name=import_path, fromlist=f'{class_name}')
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f'Could not import the module for {import_path}')
    class_ = getattr(py_mod, class_name)
    return class_


if __name__ == '__main__':
    instantiate_all()
