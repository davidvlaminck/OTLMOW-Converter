from datetime import datetime
from pathlib import Path

from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    otlmow_converter = OtlmowConverter()

    instance = AllCasesTestClass()
    instance.assetId.identificator = '0000'
    instance.testBooleanField = False
    instance.testDecimalField = 79.07
    instance.testIntegerField = -55
    assets = [instance]

# export
    file_path = Path(f'Output/{datetime.now().strftime("%Y%m%d%H%M%S")}_testclass.ttl')
    file_path = Path(f'Output/testclass.ttl')
    otlmow_converter.create_file_from_assets(filepath=file_path, list_of_objects=assets)
