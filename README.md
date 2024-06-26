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

## Functionality
The core functionality of this library is creating instances of otlmow_model classes by converting or creating them. 
The instances can then be manipulated and finally exported to a different format. When exporting to a file, a DAVIE 
compliant format can be chosen so that the data can be imported in the DAVIE application.

### Supported formats and objects
Using this library, you can convert between the following objects and formats
1. otlmow class objects
   - class objects can simply be instantiated in code or created using the helpers in the otlmow-model library
2. files
   - chose one of the many [supported file formats](#supported-file-formats) to read from or write data to
   - some file formats are DAVIE compliant, meaning they can be imported in the DAVIE application
3. dictionaries
   - class objects have a simple dictionary representation and are more efficient to work with in memory
   - some attribute values can be dictionaries themselves
   - because of cardinality, dictionary values can be a list of values or a list of dictionaries
   - with rdf as true, the dictionary uses the RDF representation with full URIs as keys (and some of the values)
4. dotnotation dictionaries
   - these are similar to dictionaries, but they use dotnotation to access values
   - as a result these are never nested and lists are converted to a string per convention
5. pandas dataframes
   - the popular pandas library is supported for reading and writing data, but it is not DAVIE compliant
   - it uses the dotnotation convention

### Converter class
The main class in this library is the OtlmowConverter class. This class is a facade class and has a couple of methods 
to convert between the different types of objects. The main methods are:
* to_objects: converts to instantiated otlmow class objects
* to_file: converts to a file
* to_dicts: converts to an iterable of dictionaries
* to_dotnotation_dicts: converts to an iterable of to_dotnotation dictionaries
* to_dataframe: converts to a pandas dataframe (or a dictionary holding multiple dataframes)

These methods can use any of the supported formats as input (subject). 
The methods determine the format of the subject and convert it to the desired format.

There are also from_A_to_B methods (i.e. from_dicts_to_objects) where either A or B are otlmow class objects. 
These methods are more efficient as they do not need to determine the format of the subject.

## Installation and requirements
OTLMOW-Converter has a couple of dependencies besides the standard Python libraries. It depends on another OTLMOW 
package: otlmow-model. These libraries will be automatically installed when installing this library. Currently, you 
need at least Python version 3.8 to use this library.

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
## Supported file formats
The following file formats are supported in OtlmowConverter
| File format | Read | Write | DAVIE compliant |
| --- | --- | --- | --- |
| CSV | Yes | Yes | Yes |
| Excel | Yes | Yes | Yes |
| JSON | Yes | Yes | Yes |
| GeoJSON | Yes | Yes | Yes |
| JSON-LD | Yes | Yes | No |
| Pandas Dataframe | Yes | Yes | No |
| TTL | No | Yes | No |
