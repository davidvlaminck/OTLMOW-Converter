# OTLMOW-Converter
[![PyPI](https://img.shields.io/pypi/v/otlmow-converter?label=latest%20release)](https://pypi.org/project/otlmow-converter/)
[![otlmow-converter-downloads](https://img.shields.io/pypi/dm/otlmow-converter)](https://pypi.org/project/otlmow-converter/)
[![Unittests](https://github.com/davidvlaminck/OTLMOW-ModelBuilder/actions/workflows/unittest.yml/badge.svg)](https://github.com/davidvlaminck/OTLMOW-Converter/actions/workflows/unittest.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/otlmow-converter)
[![GitHub issues](https://img.shields.io/github/issues/davidvlaminck/OTLMOW-Converter)](https://github.com/davidvlaminck/OTLMOW-Converter/issues)
[![coverage](https://github.com/davidvlaminck/OTLMOW-Converter/blob/master/UnitTests/coverage.svg)](https://htmlpreview.github.io/?https://github.com/davidvlaminck/OTLMOW-Converter/blob/master/UnitTests/htmlcov/index.html)


## OTLMOW Project 
This project aims to implement the Flemish data standard OTL (https://wegenenverkeer.data.vlaanderen.be/) in Python.
It is split into different packages to reduce compatibility issues
- [otlmow_model](https://github.com/davidvlaminck/OTLMOW-Model)
- [otlmow_modelbuilder](https://github.com/davidvlaminck/OTLMOW-ModelBuilder)
- [otlmow_converter](https://github.com/davidvlaminck/OTLMOW-Converter) (you are currently looking at this package)
- [otlmow_template](https://github.com/davidvlaminck/OTLMOW-Template) 
- [otlmow_postenmapping](https://github.com/davidvlaminck/OTLMOW-PostenMapping) 

## Installation and requirements
OTLMOW-Converter has two dependencies besides the standard Python libraries: pandas and openpyxl. It will be automatically installed when installing this library. 
Currently, you need at least Python version 3.8 to use this library.

To install the OTL MOW project into your Python project, use pip to install it:
``` 
pip install otlmow_converter
```
To upgrade an existing installation use:
``` 
pip install otlmow_converter --upgrade
```

## Usage
The core functionality of this library is creating objects of otlmow_model by, either using helper functions or reading a DAVIE file. Then the user can manipulate the objects and finally export them to a valid DAVIE file that can be imported in the application.

<!--- 
assetfactory
relationcreator

-->
In the following example 100 objects are created and exported to a csv file.
```
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.Classes.Onderdeel.Camera import Camera

created_assets = []
for nr in range(1, 100):
    d = {'toestand': 'in-gebruik', 'isPtz': (nr <= 50),
        'assetId': {'identificator': f'camera_{nr}'}}
    created_assets.append(Camera.from_dict(d))

converter = OtlmowConverter()
converter.create_file_from_assets(filepath=Path('new_cameras.csv'), list_of_objects=created_assets)
```
It's also possible to import objects from a file and export it to a different format.
```
from otlmow_converter.OtlmowConverter import OtlmowConverter

converter = OtlmowConverter()
created_assets = converter.create_assets_from_file(filepath=Path('new_cameras.csv'))
converter.create_file_from_assets(filepath=Path('new_cameras.json'), list_of_objects=created_assets)
```

## Formats
The following file formats are supported in OtlmowConverter
| File format | Read | Write | DAVIE compliant |
| --- | --- | --- | --- |
| CSV | Yes | Yes | Yes |
| Excel | Yes | Yes | Yes |
| JSON | Yes | Yes | Yes |
| GEOJSON| Yes | Yes | Yes |
| JSON-LD| Yes | Yes | No |
| TTL | No | Yes | No |