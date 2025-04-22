from collections import defaultdict
from pathlib import Path

import pytest
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject


from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter


@pytest.fixture
def minimum():
    a = AllCasesTestClass()
    a.assetId.identificator = '1'
    return a

@pytest.fixture
def minimum_2():
    a = AllCasesTestClass()
    a.assetId.identificator = '2'
    return a

@pytest.fixture
def one_attribute():
    a = AllCasesTestClass()
    a.assetId.identificator = '1'
    a.toestand = 'in-gebruik'
    return a

@pytest.fixture
def one_complex_attribute():
    a = AllCasesTestClass()
    a.assetId.identificator = '1'
    a.testComplexTypeMetKard[0].testStringField = 'naam'
    return a


@pytest.fixture
def one_complex_attribute_different():
    a = AllCasesTestClass()
    a.assetId.identificator = '1'
    a.testComplexTypeMetKard[0].testStringField = 'naam_2'
    return a


@pytest.fixture
def one_complex_attribute_2():
    a = AllCasesTestClass()
    a.assetId.identificator = '1'
    a.testComplexTypeMetKard[0].testBooleanField = True
    return a


@pytest.fixture
def one_attribute_different():
    a = AllCasesTestClass()
    a.assetId.identificator = '1'
    a.toestand = 'in-opbouw'
    return a

@pytest.fixture
def two_attributes():
    a = AllCasesTestClass()
    a.assetId.identificator = '1'
    a.toestand = 'in-gebruik'
    a.testStringField = 'naam'
    return a

@pytest.fixture
def two_attributes_different():
    a = AllCasesTestClass()
    a.assetId.identificator = '1'
    a.toestand = 'in-opbouw'
    a.testStringField = 'naam_2'
    return a

@pytest.fixture
def other_type():
    a = AnotherTestClass()
    a.assetId.identificator = '1'
    return a

@pytest.fixture
def empty():
    return AllCasesTestClass()


class NoIdentificatorError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class CannotCombineDifferentAssetsError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class CannotCombineAssetsError(ValueError):
    def __init__(self, message):
        super().__init__(message)


def combine_assets(asset_list: list[OTLObject]) -> list[OTLObject]:
    assets = defaultdict(list)
    for asset in asset_list:
        if asset.typeURI == 'http://purl.org/dc/terms/Agent':
            assets[asset.agentId.identificator].append(asset)
        else:
            assets[asset.assetId.identificator].append(asset)
    combined_assets = []
    for asset_list in assets.values():
        if len(asset_list) == 1:
            combined_assets.append(asset_list[0])
        else:
            combined_asset = combine_two_asset_instances(asset_list[0], asset_list[1])
            for asset in asset_list[2:]:
                combined_asset = combine_two_asset_instances(combined_asset, asset)
            combined_assets.append(combined_asset)
    return combined_assets


def combine_two_asset_instances(asset1: OTLObject, asset2: OTLObject) -> OTLObject:
    if asset1 is None or asset2 is None:
        raise ValueError('One of the assets is None')

    if asset1.assetId.identificator is None or asset2.assetId.identificator is None:
        raise NoIdentificatorError('One of the assets has no assetId.identificator')

    if asset1.assetId.identificator != asset2.assetId.identificator:
        raise CannotCombineDifferentAssetsError('The assets have different assetId.identificator values')

    if asset1.typeURI != asset2.typeURI:
        raise CannotCombineDifferentAssetsError('The assets have different types')

    ddict1 = DotnotationDictConverter.to_dict(asset1)
    ddict2 = DotnotationDictConverter.to_dict(asset2)
    ddict2.pop('assetId.identificator')

    attribute_errors = []
    for key, value in ddict2.items():
        if value is None:
            continue
        if key == 'typeURI':
            continue

        if key in ddict1 and ddict1[key] is not None and ddict1[key] != value:
            attribute_errors.append((key, ddict1[key], value))
        else:
            ddict1[key] = value

    if attribute_errors:
        error_str = '\n'.join([f'{key}: {ddict1[key]}, {value}' for key, _, value in sorted(attribute_errors)])
        raise CannotCombineAssetsError(
            message=f'Cannot combine the assets with id {asset1.assetId.identificator} because some attributes '
                    'have conflicting values:\n'
                    f'{error_str}')

    return DotnotationDictConverter.from_dict(ddict1, model_directory=Path(__file__).parent / 'TestModel')

# TODO agent tests

def test_combine_assets_multiple_instances(minimum, minimum_2, one_attribute, one_complex_attribute):
    results = combine_assets([minimum, minimum_2, one_attribute, one_complex_attribute])
    assert len(results) == 2
    assert results[0].assetId.identificator == '1'
    assert results[0].toestand == 'in-gebruik'
    assert results[0].testComplexTypeMetKard[0].testStringField == 'naam'
    assert results[1].assetId.identificator == '2'


def test_combine_assets_two_instances(minimum, one_attribute):
    results = combine_assets([minimum, one_attribute])
    assert len(results) == 1
    assert results[0].assetId.identificator == '1'
    assert results[0].toestand == 'in-gebruik'


def test_combine_two_asset_instances_empty_arguments(empty):
    with pytest.raises(ValueError):
        combine_two_asset_instances(asset1=None, asset2=None)
    with pytest.raises(ValueError):
        combine_two_asset_instances(asset1=empty, asset2=None)


def test_combine_two_asset_instances_empty_asset_identificator(minimum, empty):
    with pytest.raises(NoIdentificatorError):
        combine_two_asset_instances(asset1=empty, asset2=minimum)
    with pytest.raises(NoIdentificatorError):
        combine_two_asset_instances(asset1=minimum, asset2=empty)


def test_combine_two_asset_instances_different_identificators(minimum, minimum_2):
    with pytest.raises(CannotCombineDifferentAssetsError):
        combine_two_asset_instances(asset1=minimum, asset2=minimum_2)


def test_combine_two_asset_instances_different_types(minimum, other_type):
    with pytest.raises(CannotCombineDifferentAssetsError):
        combine_two_asset_instances(asset1=minimum, asset2=other_type)


def test_combine_two_asset_instances_no_attributes(minimum):
    result = combine_two_asset_instances(asset1=minimum, asset2=minimum)
    assert result == minimum


def test_combine_two_asset_instances_one_attribute(minimum, one_attribute):
    result = combine_two_asset_instances(asset1=minimum, asset2=one_attribute)
    assert result == one_attribute


def test_combine_two_asset_instances_one_attribute_incompatible(one_attribute_different, one_attribute):
    with pytest.raises(CannotCombineAssetsError) as exc:
        combine_two_asset_instances(asset1=one_attribute, asset2=one_attribute_different)
    assert exc.value.args[0] == ('Cannot combine the assets with id 1 because some attributes have conflicting '
     'values:\n'
     'toestand: in-gebruik, in-opbouw')


def test_combine_two_asset_instances_two_attributes_incompatible(two_attributes, two_attributes_different):
    with pytest.raises(CannotCombineAssetsError) as exc:
        combine_two_asset_instances(asset1=two_attributes, asset2=two_attributes_different)
    assert exc.value.args[0] == ('Cannot combine the assets with id 1 because some attributes have conflicting values:\n'
                                 'testStringField: naam, naam_2\n'
                                 'toestand: in-gebruik, in-opbouw')

def test_combine_two_asset_instances_one_complex_attribute(one_complex_attribute, one_complex_attribute_2):
    result = combine_two_asset_instances(asset1=one_complex_attribute, asset2=one_complex_attribute_2)
    resulting_asset = AllCasesTestClass()
    resulting_asset.assetId.identificator = '1'
    resulting_asset.testComplexTypeMetKard[0].testStringField = 'naam'
    resulting_asset.testComplexTypeMetKard[0].testBooleanField = True

    assert result == resulting_asset


def test_combine_two_asset_instances_one_complex_attribute_incompatible(one_complex_attribute, one_complex_attribute_different):
    with pytest.raises(CannotCombineAssetsError) as exc:
        combine_two_asset_instances(asset1=one_complex_attribute, asset2=one_complex_attribute_different)
    assert exc.value.args[0] == (f'Cannot combine the assets with id 1 because some '
                           'attributes have conflicting values:\n'
                           "testComplexTypeMetKard[].testStringField: ['naam'], ['naam_2']")
