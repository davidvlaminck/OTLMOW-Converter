import json
from collections.abc import Iterable
from pathlib import Path

global_relation_dict: dict = {}
global_class_dict: dict = {}

MODEL_ROOT_PATH = Path(__file__).parent.parent.parent


def get_hardcoded_relation_dict(model_directory: Path = None) -> dict:
    global global_relation_dict
    if global_relation_dict != {}:
        return global_relation_dict

    if model_directory is None:
        model_directory = MODEL_ROOT_PATH

    with open(model_directory / 'OtlmowModel' / 'generated_info.json', 'r') as f:
        generated_info_dict = json.load(f)
    global_relation_dict = generated_info_dict['relations']

    return global_relation_dict


def get_hardcoded_class_dict(model_directory: Path = None) -> dict:
    global global_class_dict
    if global_class_dict != {}:
        return global_class_dict

    if model_directory is None:
        model_directory = MODEL_ROOT_PATH

    with open(model_directory / 'OtlmowModel' / 'generated_info.json', 'r') as f:
        generated_info_dict = json.load(f)
    global_class_dict = generated_info_dict['classes']

    return global_class_dict

def get_concrete_subclasses_from_class_dict(base_uri: str, model_directory: Path = None) -> Iterable[str]:
    class_dict = get_hardcoded_class_dict(model_directory)
    for subclass in class_dict[base_uri]['direct_subclasses']:
        if not class_dict[subclass]['abstract']:
            yield subclass
        yield from get_concrete_subclasses_from_class_dict(subclass, model_directory)