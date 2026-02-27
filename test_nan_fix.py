#!/usr/bin/env python
"""Test script to verify NaN handling in PandasConverter works correctly."""

import numpy as np
from pandas import DataFrame
from pathlib import Path
from otlmow_converter.FileFormats.PandasConverter import PandasConverter
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass

model_directory_path = Path(__file__).parent / 'UnitTests' / 'TestModel'

def test_nan_handling():
    """Test that NaN values are properly converted to None regardless of pandas version."""
    print("Testing NaN handling in PandasConverter...")

    # Create test instances
    instance = AllCasesTestClass()
    instance.assetId.identificator = '01'
    instance.testBooleanField = True

    instance2 = AnotherTestClass()
    instance2.assetId.identificator = '02'
    instance2.notitie = 'random note'

    instances = [instance, instance2]

    # Convert to dataframe
    df = DataFrame(PandasConverter.convert_objects_to_single_dataframe(list_of_objects=instances))
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame dtypes:\n{df.dtypes}\n")

    # Check for NaN values in the dataframe
    print("DataFrame with potential NaN values:")
    print(df[['notitie', 'testBooleanField']].to_string())
    print()

    # Convert back to objects
    objects = list(PandasConverter.convert_dataframe_to_objects(dataframe=df, model_directory=model_directory_path))
    print(f"Converted {len(objects)} objects")

    # Verify NaN handling
    print(f"\nObject 0 notitie value: {repr(objects[0].notitie)}")
    print(f"Object 0 notitie is None: {objects[0].notitie is None}")
    print(f"Object 0 notitie type: {type(objects[0].notitie)}")

    # The assertion that was failing in GitHub Actions
    assert objects[0].notitie is None, f"Expected None, got {repr(objects[0].notitie)}"
    assert objects[0].testBooleanField is True
    assert objects[1].notitie == 'random note'

    print("\n✓ All NaN handling tests passed!")

if __name__ == '__main__':
    test_nan_handling()

