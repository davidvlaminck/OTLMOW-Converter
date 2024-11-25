import json
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