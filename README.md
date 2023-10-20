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
- [otlmow_davie](https://github.com/davidvlaminck/OTLMOW-DAVIE)
- [otlmow_visuals](https://github.com/davidvlaminck/OTLMOW-Visuals)
- [otlmow_gui](https://github.com/davidvlaminck/OTLMOW-GUI)


## Installation and requirements
OTLMOW-Converter has a couple of dependencies besides the standard Python libraries. It depends on another OTLMOW package: otlmow-model. These libraries will be automatically installed when installing this library. Currently, you need at least Python version 3.7 to use this library.

To install the OTL MOW project into your Python project, use pip to install it:
``` 
pip install otlmow_converter
```
To upgrade an existing installation use:
``` 
pip install otlmow_converter --upgrade
```

## Code examples and usage
See the [Readme notebook](https://github.com/davidvlaminck/OTLMOW-Converter/blob/master/Readme.ipynb)

<!--- 
assetfactory
relationcreator
-->
## Supported formats
The following file formats are supported in OtlmowConverter
| File format | Read | Write | DAVIE compliant |
| --- | --- | --- | --- |
| CSV | Yes | Yes | Yes |
| Excel | Yes | Yes | Yes |
| JSON | Yes | Yes | Yes |
| GEOJSON| Yes | Yes | Yes |
| JSON-LD| Yes | Yes | No |
| TTL | No | Yes | No |
