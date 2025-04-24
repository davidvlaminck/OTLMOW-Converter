from pathlib import Path

import pytest
from otlmow_model.OtlmowModel.Classes.Agent import Agent

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.Exceptions.CannotCombineAssetsError import CannotCombineAssetsError
from otlmow_converter.Exceptions.CannotCombineDifferentAssetsError import CannotCombineDifferentAssetsError
from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.Exceptions.NoIdentificatorError import NoIdentificatorError
from otlmow_converter.HelperFunctions import combine_assets, combine_two_asset_instances, combine_files


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
def agent_one_attribute():
    a = Agent()
    a.agentId.identificator = '1'
    a.naam = 'naam'
    return a


@pytest.fixture
def agent_one_attribute_different():
    a = Agent()
    a.agentId.identificator = '1'
    a.contactinfo[0].contactnaam = 'naam_2'
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


test_model_directory = Path(__file__).parent / 'TestModel'
combine_directory = Path(__file__).parent / 'Combine'


def test_combine_files_two_errors_in_two_files(subtests):
    csv_path = combine_directory / 'asset_2.csv'
    json_path = combine_directory / 'asset_2.json'

    with pytest.raises(ExceptionsGroup) as exc_group:
        combine_files([csv_path, json_path], model_directory=test_model_directory)

    exc1 = exc_group.value.exceptions[0]
    exc2 = exc_group.value.exceptions[1]

    with subtests.test('Check amount of exceptions and types'):
        assert len(exc_group.value.exceptions) == 2
        assert isinstance(exc1, CannotCombineAssetsError)
        assert isinstance(exc2, CannotCombineDifferentAssetsError)

    with subtests.test('Check 1st exception message'):
        assert exc1.message == ('Cannot combine the assets with id: "1" with type "onderdeel#AllCasesTestClass"\n'
                                     'that occur in files: "asset_2.csv", "asset_2.json"\n'
                                     'due to conflicting values in attribute(s):\n'
                                     'testBooleanField: False != True\n'
                                     'testStringField: naam != naam_2')
    with subtests.test('Check 1st exception attributes: id and type_uri'):
        assert exc1.object_id == '1'
        assert exc1.type_uri == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'

    with subtests.test('Check 1st exception attributes: attribute error list'):
        assert exc1.attribute_errors == [('testBooleanField', (False, True)),
                                              ('testStringField', ('naam', 'naam_2'))]

    with subtests.test('Check 1st exception attributes: file list'):
        assert exc1.files == [csv_path, json_path]

    with subtests.test('Check 2nd exception message'):
        assert exc2.message == ('Cannot combine the assets with id: "2"\n'
                                'that occur in files: "asset_2.csv", "asset_2.json"\n'
                                'due to conflicting types: onderdeel#AllCasesTestClass != onderdeel#AnotherTestClass')

    with subtests.test('Check 2nd exception attributes: id and type_uri'):
        assert exc2.object_id == '2'
        assert exc2.type_uri is None

    with subtests.test('Check 2nd exception attributes: attribute error list'):
        assert exc2.attribute_errors == [('typeURI',
                                          ('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass',
                                           'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'))]

    with subtests.test('Check 2nd exception attributes: file list'):
        assert exc2.files == [csv_path, json_path]


def test_combine_files_three_files_failing(subtests):
    csv_path = combine_directory / 'asset_1.csv'
    json_path = combine_directory / 'asset_1.json'
    xlsx_path = combine_directory / 'asset_1.xlsx'

    with pytest.raises(ExceptionsGroup) as exc_group:
        combine_files([csv_path, json_path, xlsx_path], model_directory=test_model_directory)

    exc = exc_group.value.exceptions[0]
    with subtests.test('Check exception message'):
        assert exc.message == ('Cannot combine the assets with id: "1" with type "onderdeel#AllCasesTestClass"\n'
                                     'that occur in files: "asset_1.csv", "asset_1.json", "asset_1.xlsx"\n'
                                     'due to conflicting values in attribute(s):\n'
                                     'testBooleanField: False != True\n'
                                     'testStringField: naam != naam_2')
    with subtests.test('Check exception attributes: id and type_uri'):
        assert exc.object_id == '1'
        assert exc.type_uri == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'

    with subtests.test('Check exception attributes: attribute error list'):
        assert exc.attribute_errors == [('testBooleanField', (False, True)),
                                              ('testStringField', ('naam', 'naam_2'))]

    with subtests.test('Check exception attributes: file list'):
        assert exc.files == [csv_path, json_path, xlsx_path]


def test_combine_assets_multiple_instances(minimum, minimum_2, one_attribute, one_complex_attribute):
    results = combine_assets([minimum, minimum_2, one_attribute, one_complex_attribute], test_model_directory)
    assert len(results) == 2
    assert results[0].assetId.identificator == '1'
    assert results[0].toestand == 'in-gebruik'
    assert results[0].testComplexTypeMetKard[0].testStringField == 'naam'
    assert results[1].assetId.identificator == '2'


def test_combine_assets_two_instances(minimum, one_attribute):
    results = combine_assets([minimum, one_attribute], test_model_directory)
    assert len(results) == 1
    assert results[0].assetId.identificator == '1'
    assert results[0].toestand == 'in-gebruik'


def test_combine_assets_two_instances_agent(agent_one_attribute, agent_one_attribute_different):
    results = combine_assets([agent_one_attribute, agent_one_attribute_different])
    assert len(results) == 1
    assert results[0].naam == 'naam'
    assert results[0].contactinfo[0].contactnaam == 'naam_2'


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
    result = combine_two_asset_instances(asset1=minimum, asset2=minimum, model_directory=test_model_directory)
    assert result == minimum


def test_combine_two_asset_instances_one_attribute(minimum, one_attribute):
    result = combine_two_asset_instances(asset1=minimum, asset2=one_attribute, model_directory=test_model_directory)
    assert result == one_attribute


def test_combine_two_asset_instances_one_attribute_incompatible(one_attribute_different, one_attribute):
    with pytest.raises(CannotCombineAssetsError) as exc:
        combine_two_asset_instances(asset1=one_attribute, asset2=one_attribute_different,
                                    model_directory=test_model_directory)
    assert exc.value.args[0] == ('Cannot combine the assets with id 1 because some attributes have conflicting '
     'values:\n'
     'toestand: in-gebruik, in-opbouw')


def test_combine_two_asset_instances_two_attributes_incompatible(two_attributes, two_attributes_different):
    with pytest.raises(CannotCombineAssetsError) as exc:
        combine_two_asset_instances(asset1=two_attributes, asset2=two_attributes_different,
                                    model_directory=test_model_directory)
    assert exc.value.args[0] == ('Cannot combine the assets with id 1 because some attributes have conflicting values:\n'
                                 'testStringField: naam, naam_2\n'
                                 'toestand: in-gebruik, in-opbouw')


def test_combine_two_asset_instances_one_complex_attribute(one_complex_attribute, one_complex_attribute_2):
    result = combine_two_asset_instances(asset1=one_complex_attribute, asset2=one_complex_attribute_2,
                                         model_directory=test_model_directory)
    resulting_asset = AllCasesTestClass()
    resulting_asset.assetId.identificator = '1'
    resulting_asset.testComplexTypeMetKard[0].testStringField = 'naam'
    resulting_asset.testComplexTypeMetKard[0].testBooleanField = True

    assert result == resulting_asset


def test_combine_two_asset_instances_one_complex_attribute_incompatible(one_complex_attribute, one_complex_attribute_different):
    with pytest.raises(CannotCombineAssetsError) as exc:
        combine_two_asset_instances(asset1=one_complex_attribute, asset2=one_complex_attribute_different,
                                    model_directory=test_model_directory)
    assert exc.value.args[0] == (f'Cannot combine the assets with id 1 because some '
                           'attributes have conflicting values:\n'
                           "testComplexTypeMetKard[].testStringField: ['naam'], ['naam_2']")
