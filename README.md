# OTLMOW-Converter
## OTLMOW Project 
This project aims to implement the Flemish data standard OTL (https://wegenenverkeer.data.vlaanderen.be/) in Python.
It is split into different packages to reduce compatibility issues
- otlmow_model
- otlmow_modelbuilder
- otlmow_converter (you are currently looking at this package)
- otlmow_template

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
otlmowconverter
formats:
csv
xlsx
json
jsonld
ttl

-->