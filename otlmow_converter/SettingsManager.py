import json
import os
from pathlib import Path
from typing import Dict


def _check_settings_with_default(settings_path: Path) -> Path:
    if settings_path is None:
        current_file_path = Path(__file__)
        settings_path = Path(current_file_path.parent / 'settings_otlmow_converter.json')

    if not os.path.isfile(settings_path):
        raise FileNotFoundError(f'{settings_path} is not a valid path. File does not exist.')

    return settings_path


def load_settings(settings_path: Path) -> Dict:
    settings_path = _check_settings_with_default(settings_path=settings_path)

    try:
        with open(settings_path) as settings_file:
            return json.load(settings_file)
    except OSError:
        raise ImportError(f'Could not open the settings file at {settings_path}')
