from pathlib import Path


def get_settings_path_for_unittests():
    this_file = Path(__file__)
    return this_file.parent / 'settings_OTLMOW.json'
