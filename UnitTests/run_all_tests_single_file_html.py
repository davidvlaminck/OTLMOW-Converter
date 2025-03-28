import os, pathlib
import webbrowser

import pytest

os.chdir(pathlib.Path.cwd())

if __name__ == "__main__":
    pytest.main(['--cov', '-v', 'Converter_generic_test.py', '--cov-report=html'])
    webbrowser.open_new_tab(str(pathlib.Path('htmlcov/index.html')))
