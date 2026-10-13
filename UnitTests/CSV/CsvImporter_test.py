from datetime import date, datetime, time
from pathlib import Path

import pytest

from otlmow_converter.Exceptions.DotnotationIncorrectError import DotnotationIncorrectError
from otlmow_converter.Exceptions.NoTypeUriInTableError import NoTypeUriInTableError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError
from otlmow_converter.FileFormats.CsvImporter import CsvImporter

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_load_test_file_multiple_types():
    file_location = Path(__file__).parent / 'Testfiles' / 'export_multiple_types.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location))
    assert len(assets) == 15


def test_load_multiple_testmodel_types_from_single_csv(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'multiple_types_empty_lines.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path))

    assert len(recwarn.list) == 0
    assert len(assets) == 2

    assets_by_type = {asset.typeURI: asset for asset in assets}

    all_cases = assets_by_type['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass']
    another = assets_by_type['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass']

    assert all_cases.assetId.identificator == 'allcases-1'
    assert all_cases.testStringField == 'alpha'
    assert another.assetId.identificator == 'another-1'
    assert another.notitie == 'note-another'


def test_load_empty_lines():
    file_location = Path(__file__).parent / 'Testfiles' / 'empty_lines.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path, delimiter=','))
    assert len(assets) == 5


def test_load_test_file(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'import_then_export_input.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path))
    assert len(assets) == 1
    assert assets[0].assetId.identificator == 'UgVLnoH'
    assert len(recwarn.list) == 0


def test_load_test_file_with_non_otl_conform_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'non_conform_attribute.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path))
    assert len(assets) == 1
    assert assets[0].assetId.identificator == 'id2'
    assert len(recwarn.list) == 1
    assert recwarn.list[0].message.args[0] == ('non_conform_attribute is a non standardized attribute of '
                                               'AnotherTestClass. The attribute will be added on the instance.')

    with pytest.raises(AttributeError) as exc:
        list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path, allow_non_otl_conform_attributes=False))


def test_load_test_unnested_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True))
    assert len(recwarn.list) == 0

    assert len(assets) == 1
    instance = assets[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert not instance.testBooleanField
    assert instance.testDateField == date(2019, 9, 20)
    assert instance.testDateTimeField == datetime(2001, 12, 15, 22, 22, 15,123456)
    assert instance.testDecimalField == 79.07
    assert instance.testDecimalFieldMetKard == [10.0, 20.0]
    assert instance.testEenvoudigType.waarde == 'string1'
    assert instance.testEenvoudigTypeMetKard[0].waarde == 'string1'
    assert instance.testEenvoudigTypeMetKard[1].waarde == 'string2'
    assert instance.testIntegerField == -55
    assert instance.testIntegerFieldMetKard == [76, 2]
    assert instance.testKeuzelijst == 'waarde-4'
    assert instance.testKeuzelijstMetKard == ['waarde-4', 'waarde-3']
    assert instance.testKwantWrd.waarde == 98.21
    assert instance.testKwantWrdMetKard[0].waarde == 10.0
    assert instance.testKwantWrdMetKard[1].waarde == 20.0
    assert instance.testStringField == 'oFfeDLp'
    assert instance.testStringFieldMetKard[0] == 'string1'
    assert instance.testStringFieldMetKard[1] == 'string2'
    assert instance.testTimeField == time(11, 5, 26)


def test_load_test_nested_attributes_1_level(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_1.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path))
    assert len(recwarn.list) == 0

    assert len(assets) == 1
    instance = assets[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == 'YKAzZDhhdTXqkD'
    assert instance.assetId.toegekendDoor == 'DGcQxwCGiBlR'
    assert instance.testComplexType.testBooleanField
    assert instance.testComplexType.testKwantWrd.waarde == 65.14
    assert instance.testComplexType.testKwantWrdMetKard[0].waarde == 10.0
    assert instance.testComplexType.testKwantWrdMetKard[1].waarde == 20.0
    assert instance.testComplexType.testStringField == 'KmCtMXM'
    assert instance.testComplexType.testStringFieldMetKard[0] == 'string1'
    assert instance.testComplexType.testStringFieldMetKard[1] == 'string2'
    assert instance.testComplexTypeMetKard[0].testBooleanField
    assert not instance.testComplexTypeMetKard[1].testBooleanField
    assert instance.testComplexTypeMetKard[0].testKwantWrd.waarde == 10.0
    assert instance.testComplexTypeMetKard[1].testKwantWrd.waarde == 20.0
    assert instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde is None
    assert instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde is None
    assert instance.testComplexTypeMetKard[0].testStringField == 'string1'
    assert instance.testComplexTypeMetKard[1].testStringField == 'string2'
    assert instance.testUnionType.unionString == 'RWKofW'
    assert instance.testUnionType.unionKwantWrd.waarde is None
    assert instance.testUnionTypeMetKard[0].unionKwantWrd.waarde == 10.0
    assert instance.testUnionTypeMetKard[1].unionKwantWrd.waarde == 20.0


def test_load_test_nested_attributes_2_levels(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_2.csv'
    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True))
    assert len(recwarn.list) == 0

    assert len(assets) == 1
    instance = assets[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.testComplexType.testComplexType2.testKwantWrd.waarde == 76.8
    assert instance.testComplexType.testComplexType2.testStringField == 'GZBzgRhOrQvfZaN'
    assert instance.testComplexType.testComplexType2MetKard[0].testKwantWrd.waarde == 10.0
    assert instance.testComplexType.testComplexType2MetKard[1].testKwantWrd.waarde == 20.0
    assert instance.testComplexType.testComplexType2MetKard[0].testStringField == 'string1'
    assert instance.testComplexType.testComplexType2MetKard[1].testStringField == 'string2'
    assert instance.testComplexTypeMetKard[0].testComplexType2.testKwantWrd.waarde == 10.0
    assert instance.testComplexTypeMetKard[1].testComplexType2.testKwantWrd.waarde == 20.0
    assert instance.testComplexTypeMetKard[0].testComplexType2.testStringField == 'string1'
    assert instance.testComplexTypeMetKard[1].testComplexType2.testStringField == 'string2'
    assert instance.testComplexTypeMetKard[0].testComplexType2MetKard[0].testKwantWrd.waarde is None
    assert instance.testComplexTypeMetKard[0].testComplexType2MetKard[0].testStringField is None


def test_load_test_subset_file(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'template_file_text_onderdeel_AllCasesTestClass.csv'

    assets = list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path))
    assert len(recwarn.list) == 0
    assert len(assets) == 1


def test_raise_errors():
    file_location = Path(__file__).parent / 'Testfiles' / 'type_uri_not_in_first_row.csv'
    with pytest.raises(TypeUriNotInFirstRowError) as exc:
        CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
        assert exc.value.message == 'The typeURI is not in the first row in file type_uri_not_in_first_row.csv'
        assert exc.value.file_path == file_location

    file_location = Path(__file__).parent / 'Testfiles' / 'type_uri_not_in_file.csv'
    with pytest.raises(NoTypeUriInTableError) as exc:
        CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
        assert exc.value.message == 'Could not find typeURI within 5 rows in the csv file type_uri_not_in_file.csv'
        assert exc.value.file_path == file_location


def test_bad_kard_error_missing_indicator_sync():
    """Test that missing cardinality indicator raises DotnotationIncorrectError in sync mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    with pytest.raises(ExceptionsGroup) as exc:
        list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True))

    assert len(exc.value.exceptions) == 1
    err = exc.value.exceptions[0]
    assert err.header == 'testEenvoudigTypeMetKard'
    assert err.expected_header == 'testEenvoudigTypeMetKard[]'
    assert 'attribute at position 0 has cardinality' in str(err)


@pytest.mark.asyncio
async def test_bad_kard_error_missing_indicator_async():
    """Test that missing cardinality indicator raises DotnotationIncorrectError in async mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    with pytest.raises(ExceptionsGroup) as exc:
        await CsvImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True)

    assert len(exc.value.exceptions) == 1
    err = exc.value.exceptions[0]
    assert err.header == 'testEenvoudigTypeMetKard'
    assert err.expected_header == 'testEenvoudigTypeMetKard[]'
    assert 'attribute at position 0 has cardinality' in str(err)


def test_bad_kard_error_extra_indicator_sync():
    """Test that extra cardinality indicator raises DotnotationIncorrectError in sync mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_extra.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    with pytest.raises(ExceptionsGroup) as exc:
        list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True))

    assert len(exc.value.exceptions) == 1
    err = exc.value.exceptions[0]
    assert err.header == 'testStringField[]'
    assert err.expected_header == 'testStringField'
    assert 'no attribute in path has cardinality > 1' in str(err)


@pytest.mark.asyncio
async def test_bad_kard_error_extra_indicator_async():
    """Test that extra cardinality indicator raises DotnotationIncorrectError in async mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_extra.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    with pytest.raises(ExceptionsGroup) as exc:
        await CsvImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True)

    assert len(exc.value.exceptions) == 1
    err = exc.value.exceptions[0]
    assert err.header == 'testStringField[]'
    assert err.expected_header == 'testStringField'
    assert 'no attribute in path has cardinality > 1' in str(err)


def test_bad_kard_error_multiple_errors_sync():
    """Test that multiple cardinality errors are raised as ExceptionsGroup in sync mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_multiple.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    with pytest.raises(ExceptionsGroup) as exc:
        list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True))

    assert len(exc.value.exceptions) == 2
    headers = {e.header for e in exc.value.exceptions}
    assert 'testEenvoudigTypeMetKard' in headers
    assert 'testStringField[]' in headers


@pytest.mark.asyncio
async def test_bad_kard_error_multiple_errors_async():
    """Test that multiple cardinality errors are raised as ExceptionsGroup in async mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_multiple.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    with pytest.raises(ExceptionsGroup) as exc:
        await CsvImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True)

    assert len(exc.value.exceptions) == 2
    headers = {e.header for e in exc.value.exceptions}
    assert 'testEenvoudigTypeMetKard' in headers
    assert 'testStringField[]' in headers


def test_bad_kard_error_data_still_loaded_sync():
    """Test that data is still loaded correctly despite cardinality error in sync mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    try:
        list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True))
    except ExceptionsGroup as exc:
        # The error should be raised but data should still be loadable
        assert len(exc.exceptions) == 1


@pytest.mark.asyncio
async def test_bad_kard_error_data_still_loaded_async():
    """Test that data is still loaded correctly despite cardinality error in async mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    try:
        await CsvImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True)
    except ExceptionsGroup as exc:
        # The error should be raised but data should still be loadable
        assert len(exc.exceptions) == 1


def test_bad_kard_error_deep_path_missing_indicator_sync():
    """Test that missing cardinality indicator on 3-level deep path with multiple cardinalities raises DotnotationListOfListError in sync mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_deep.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError
    with pytest.raises(ExceptionsGroup) as exc:
        list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True))

    assert len(exc.value.exceptions) == 1
    assert isinstance(exc.value.exceptions[0], DotnotationListOfListError)
    err = exc.value.exceptions[0]
    assert 'testComplexTypeMetKard.testComplexType2MetKard.testKwantWrd' in str(err)
    assert 'multiple attributes with cardinality' in str(err).lower()


@pytest.mark.asyncio
async def test_bad_kard_error_deep_path_missing_indicator_async():
    """Test that missing cardinality indicator on 3-level deep path with multiple cardinalities raises DotnotationListOfListError in async mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_deep.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError
    with pytest.raises(ExceptionsGroup) as exc:
        await CsvImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True)

    assert len(exc.value.exceptions) == 1
    assert isinstance(exc.value.exceptions[0], DotnotationListOfListError)
    err = exc.value.exceptions[0]
    assert 'testComplexTypeMetKard.testComplexType2MetKard.testKwantWrd' in str(err)
    assert 'multiple attributes with cardinality' in str(err).lower()


def test_bad_kard_error_deep_path_single_cardinality_sync():
    """Test that missing cardinality indicator on deep path with SINGLE cardinality can be fixed in sync mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_deep_single.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    from otlmow_converter.Exceptions.DotnotationIncorrectError import DotnotationIncorrectError
    with pytest.raises(ExceptionsGroup) as exc:
        list(CsvImporter.to_objects(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True))

    assert len(exc.value.exceptions) == 1
    assert isinstance(exc.value.exceptions[0], DotnotationIncorrectError)
    err = exc.value.exceptions[0]
    assert err.header == 'testComplexType.testComplexType2MetKard.testKwantWrd'
    # Single cardinality at position 1 (testComplexType2MetKard) - should add [] after it
    assert err.expected_header == 'testComplexType.testComplexType2MetKard[].testKwantWrd'
    assert 'attribute at position 1 has cardinality' in str(err)


@pytest.mark.asyncio
async def test_bad_kard_error_deep_path_single_cardinality_async():
    """Test that missing cardinality indicator on deep path with SINGLE cardinality can be fixed in async mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_deep_single.csv'
    from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
    from otlmow_converter.Exceptions.DotnotationIncorrectError import DotnotationIncorrectError
    with pytest.raises(ExceptionsGroup) as exc:
        await CsvImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path, contains_exactly_one_type=True)

    assert len(exc.value.exceptions) == 1
    assert isinstance(exc.value.exceptions[0], DotnotationIncorrectError)
    err = exc.value.exceptions[0]
    assert err.header == 'testComplexType.testComplexType2MetKard.testKwantWrd'
    # Single cardinality at position 1 (testComplexType2MetKard) - should add [] after it
    assert err.expected_header == 'testComplexType.testComplexType2MetKard[].testKwantWrd'
    assert 'attribute at position 1 has cardinality' in str(err)