import json
from pathlib import Path
from typing import Dict

CURRENT_DIR = Path(__file__).parent

OTLMOW_CONVERTER_SETTINGS: Dict = {}

def _load_settings_by_dict(settings_dict: Dict) -> None:
    global OTLMOW_CONVERTER_SETTINGS
    OTLMOW_CONVERTER_SETTINGS = settings_dict


def load_settings(settings_path: Path = CURRENT_DIR / 'settings_otlmow_converter.json') -> None:
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
