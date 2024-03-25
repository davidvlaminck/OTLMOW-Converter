import json
from pathlib import Path
from typing import Dict

CURRENT_DIR = Path(__file__).parent


class GlobalVariables:
    settings = {}

def _load_settings_by_dict(settings_dict: Dict) -> None:
    GlobalVariables.settings = settings_dict


def load_settings(settings_path: Path = CURRENT_DIR / 'settings_otlmow_converter.json') -> None:
    if GlobalVariables.settings != {}:
        return
    if not settings_path.exists():
        raise FileNotFoundError(f'{settings_path} is not a valid path. File does not exist.')

    try:
        with open(settings_path) as settings_file:
            settings_dict = json.load(settings_file)
            _load_settings_by_dict(settings_dict)
    except OSError as e:
        raise ImportError(
            f'Could not open the settings file at {settings_path}'
        ) from e


def _update_dict(orig_dict: Dict, extra_dict: Dict) -> None:
    for k, v in extra_dict.items():
        if isinstance(v, dict):
            _update_dict(orig_dict[k], v)
        else:
            orig_dict[k] = v


def update_settings_by_dict(settings_dict: Dict) -> None:
    _update_dict(GlobalVariables.settings, settings_dict)
    print(GlobalVariables.settings)
