import datetime
import os
from pathlib import Path

import pytest

from otlmow_converter.Exceptions.BadLinesInExcelError import BadLinesInExcelError
from otlmow_converter.Exceptions.DotnotationIncorrectError import DotnotationIncorrectError
from otlmow_converter.Exceptions.ErrorInExcelLine import ErrorInExcelLine
from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.Exceptions.InvalidColumnNamesInExcelTabError import InvalidColumnNamesInExcelTabError
from otlmow_converter.Exceptions.MissingHeaderError import MissingHeaderError
from otlmow_converter.Exceptions.NoTypeUriInExcelTabError import NoTypeUriInExcelTabError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError
from otlmow_converter.Exceptions.UnknownExcelError import UnknownExcelError
from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

model_directory_path = Path(__file__).parent.parent / 'TestModel'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_load_test_unnested_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes.xlsx'

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
    warns = [w for w in recwarn.list if w.category is not DeprecationWarning]  # remove deprecation warnings
    assert not warns

    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == '0000-0000'
    assert not instance.testBooleanField
    assert instance.testDateField == datetime.date(2019, 9, 20)
    assert instance.testDateTimeField == datetime.datetime(2001, 12, 15, 22, 22, 15)
    assert instance.testDecimalField == 79.07
    assert instance.testDecimalFieldMetKard == [10.0, 20.0]
    assert instance.testEenvoudigType.waarde == 'string1'
    assert instance.testIntegerField == -55
    assert instance.testIntegerFieldMetKard == [76, 2]
    assert instance.testKeuzelijst == 'waarde-4'
    assert instance.testKeuzelijstMetKard == ['waarde-4', 'waarde-3']
    assert instance.testKwantWrd.waarde == 98.21
    assert instance.testStringField == 'oFfeDLp'
    assert instance.testStringFieldMetKard[0] == 'string1'
    assert instance.testStringFieldMetKard[1] == 'string2'
    assert instance.testTimeField == datetime.time(11, 5, 26)
    assert instance.geometry == 'POINT Z (200000 200000 0)'


def test_load_empty_sheet(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'empty_sheet.xlsx'

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
    warns = [w for w in recwarn.list if w.category is not DeprecationWarning]  # remove deprecation warnings
    assert not warns
    assert len(objects) == 1


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_load_test_nested_attributes_1_level(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_1.xlsx'

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)

    warns = [w for w in recwarn.list if w.category is not DeprecationWarning]  # remove deprecation warnings
    assert not warns

    assert len(objects) == 1

    instance = objects[0]
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


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_load_test_nested_attributes_2_levels(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_2.xlsx'

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
    warns = [w for w in recwarn.list if w.category is not DeprecationWarning]  # remove deprecation warnings
    assert not warns

    assert len(objects) == 1

    instance = objects[0]
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


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_get_index_of_typeURI_column_in_sheet():
    file_location = Path(__file__).parent / 'Testfiles' / 'typeURITestFile.xlsx'

    with pytest.raises(ExceptionsGroup) as ex:
        ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)

    ex = ex.value
    assert isinstance(ex, ExceptionsGroup)
    assert len(ex.exceptions) == 2
    assert len(ex.objects) == 1

    exception_1 = ex.exceptions[0]
    assert isinstance(exception_1, TypeUriNotInFirstRowError)
    assert exception_1.file_path == file_location
    assert exception_1.tab == 'type_uri_third_row'

    exception_2 = ex.exceptions[1]
    assert isinstance(exception_2, NoTypeUriInExcelTabError)
    assert exception_2.file_path == file_location
    assert exception_2.tab == 'no_type_uri_in_sheet'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_bad_columns():
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_columns.xlsx'

    with pytest.raises(ExceptionsGroup) as ex:
        ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)

    ex = ex.value
    assert isinstance(ex, ExceptionsGroup)
    assert len(ex.exceptions) == 1
    assert len(ex.objects) == 1

    exception_1 = ex.exceptions[0]
    assert isinstance(exception_1, MissingHeaderError)
    assert exception_1.file_path == file_location
    assert exception_1.tab == 'missing header'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_bad_column_integer():
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_column_int.xlsx'

    with pytest.raises(ExceptionsGroup) as ex:
        ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path,
                                 allow_non_otl_conform_attributes=False)

    ex = ex.value
    assert isinstance(ex, ExceptionsGroup)
    assert len(ex.exceptions) == 1

    exception_1 = ex.exceptions[0]
    assert isinstance(exception_1, UnknownExcelError)
    assert exception_1.file_path == file_location
    assert exception_1.tab == 'int_in_header'


def test_check_headers():
    file_location = Path(__file__).parent / 'Testfiles' / 'typeURITestFile.xlsx'

    all_cases_uri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    try:
        ExcelImporter.check_headers(
            filepath=file_location, model_directory=model_directory_path, sheet='<Worksheet "correct_sheet">',
            headers=['typeURI', 'testStringField', 'bad_name_field', '[DEPRECATED] d_a', 'list[].list[]'],
            type_uris=[all_cases_uri],
            sheet_data=[
                ['typeURI', 'testStringField', 'bad_name_field', '[DEPRECATED] d_a', 'list[].list[]'],
                [all_cases_uri, 'val', 'val2', 'val3', 'val4'],
            ],
            type_uri_index=0,
            allow_non_otl_conform_attributes=False)
    except InvalidColumnNamesInExcelTabError as ex:
        assert ex.bad_columns == ['bad_name_field', '[DEPRECATED] d_a', 'list[].list[]']


def test_check_headers_multiple_types_column_data():
    """A header unknown to one type must not fail when that type has no data in the column.

    Only types that actually populate a column are validated against that column's header,
    so a column used exclusively by one type does not fail validation for another type.
    """
    all_cases_uri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    another_uri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'

    # testStringField exists on AllCasesTestClass but NOT on AnotherTestClass.
    # Only the AllCasesTestClass row populates the column, so AnotherTestClass must not be
    # validated against it (no AttributeError / bad_columns for AnotherTestClass).
    fixed_headers, cardinality_errors = ExcelImporter.check_headers(
        filepath=Path(__file__).parent / 'Testfiles' / 'typeURITestFile.xlsx',
        model_directory=model_directory_path,
        sheet='<Worksheet "correct_sheet">',
        headers=['typeURI', 'testStringField'],
        type_uris=[all_cases_uri, another_uri],
        sheet_data=[
            ['typeURI', 'testStringField'],
            [all_cases_uri, 'a value'],            # AllCasesTestClass populates the column
            [another_uri, None],                    # AnotherTestClass has no data in the column
        ],
        type_uri_index=0,
        allow_non_otl_conform_attributes=False)

    assert fixed_headers == ['typeURI', 'testStringField']
    assert cardinality_errors == []



@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_load_non_conform_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'non_conform_attribute.xlsx'

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path,
                                       warn_for_non_otl_conform_attributes=False)
    warns = [w for w in recwarn.list if w.category is not DeprecationWarning]  # remove deprecation warnings
    assert not warns

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.testBooleanField
    assert instance.non_conform_attribute == 'value'


def test_empty_lines_in_excel(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'empty_lines.xlsx'

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
    warns = [w for w in recwarn.list if w.category is not DeprecationWarning]  # remove deprecation warnings
    assert not warns

    assert objects[0].typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert len(objects) == 5


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_load_dates_in_excel(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'file_with_date.xlsx'

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
    warns = [w for w in recwarn.list if w.category is not DeprecationWarning]  # remove deprecation warnings
    assert not warns

    assert objects[0].typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert objects[0].datumOprichtingObject == datetime.date(2004,1,3)
    assert objects[1].datumOprichtingObject == datetime.date(2002,2,2)
    assert objects[2].datumOprichtingObject == datetime.date(2004,1,4)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_load_multiple_errors_in_different_lines(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'multiple_errors_in_different_lines.xlsx'

    with pytest.raises(ExceptionsGroup) as ex:
        ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path,
                                           warn_for_non_otl_conform_attributes=False)
    ex = ex.value
    assert isinstance(ex, ExceptionsGroup)
    assert len(ex.objects) == 2
    assert len(ex.exceptions) == 1

    bad_lines_error = ex.exceptions[0]
    # Assert that bad_lines_error is of the expected type
    assert isinstance(bad_lines_error, BadLinesInExcelError)
    # Assert that bad_lines_error.exceptions is a list with expected length
    assert isinstance(bad_lines_error.exceptions, list)
    assert len(bad_lines_error.exceptions) == 3

    assert isinstance(bad_lines_error.exceptions[0], ErrorInExcelLine)
    assert isinstance(bad_lines_error.exceptions[1], ErrorInExcelLine)
    assert isinstance(bad_lines_error.exceptions[2], ErrorInExcelLine)

    assert (str(bad_lines_error.exceptions[0]) ==
            ('Error in line 2: MultipleAttributeError with 1 error(s):\n'
             '- OTLAttributeError on attribute "geometry" with value "aaa": ValueError'))
    assert (str(bad_lines_error.exceptions[1]) ==
            ('Error in line 4: MultipleAttributeError with 1 error(s):\n'
             '- OTLAttributeError on attribute "testDateField" with value "aaa": CouldNotConvertToCorrectTypeError'))
    assert (str(bad_lines_error.exceptions[2]) ==
            ('Error in line 6: MultipleAttributeError with 1 error(s):\n'
             '- OTLAttributeError on attribute "testBooleanField" with value "aaa": CouldNotConvertToCorrectTypeError'))


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_ignore_x_columns_true(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'ignore_x_columns.xlsx'

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path,
                                       ignore_X_columns=True)

    x_warnings = [w for w in recwarn.list if 'X_doelIsActief' in str(w.message)]
    assert not x_warnings

    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.testStringField == 'test_string'
    assert not hasattr(instance, 'X_doelIsActief')


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_ignore_x_columns_false(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'ignore_x_columns.xlsx'

    objects = ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path,
                                       ignore_X_columns=False)

    x_warnings = [w for w in recwarn.list if 'X_doelIsActief' in str(w.message)]
    assert len(x_warnings) > 0

    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.testStringField == 'test_string'
    assert hasattr(instance, 'X_doelIsActief')
    assert instance.X_doelIsActief == 'some_value'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_bad_kard_error_missing_indicator_sync():
    """Test that missing cardinality indicator raises DotnotationIncorrectError in sync mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header.xlsx'
    with pytest.raises(ExceptionsGroup) as exc:
        ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)

    ex = exc.value
    assert len(ex.exceptions) == 1
    assert isinstance(ex.exceptions[0], DotnotationIncorrectError)
    err = ex.exceptions[0]
    assert err.header == 'testEenvoudigTypeMetKard'
    assert err.expected_header == 'testEenvoudigTypeMetKard[]'
    assert 'attribute at position 0 has cardinality' in str(err)
    assert err.tab == 'Sheet1'


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
async def test_bad_kard_error_missing_indicator_async():
    """Test that missing cardinality indicator raises DotnotationIncorrectError in async mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header.xlsx'
    with pytest.raises(ExceptionsGroup) as exc:
        await ExcelImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)

    ex = exc.value
    assert len(ex.exceptions) == 1
    assert isinstance(ex.exceptions[0], DotnotationIncorrectError)
    err = ex.exceptions[0]
    assert err.header == 'testEenvoudigTypeMetKard'
    assert err.expected_header == 'testEenvoudigTypeMetKard[]'
    assert 'attribute at position 0 has cardinality' in str(err)
    assert err.tab == 'Sheet1'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_bad_kard_error_extra_indicator_sync():
    """Test that extra cardinality indicator raises DotnotationIncorrectError in sync mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_extra.xlsx'
    with pytest.raises(ExceptionsGroup) as exc:
        ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)

    ex = exc.value
    assert len(ex.exceptions) == 1
    assert isinstance(ex.exceptions[0], DotnotationIncorrectError)
    err = ex.exceptions[0]
    assert err.header == 'testStringField[]'
    assert err.expected_header == 'testStringField'
    assert 'no attribute in path has cardinality > 1' in str(err)
    assert err.tab == 'Sheet1'


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
async def test_bad_kard_error_extra_indicator_async():
    """Test that extra cardinality indicator raises DotnotationIncorrectError in async mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_extra.xlsx'
    with pytest.raises(ExceptionsGroup) as exc:
        await ExcelImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)

    ex = exc.value
    assert len(ex.exceptions) == 1
    assert isinstance(ex.exceptions[0], DotnotationIncorrectError)
    err = ex.exceptions[0]
    assert err.header == 'testStringField[]'
    assert err.expected_header == 'testStringField'
    assert 'no attribute in path has cardinality > 1' in str(err)
    assert err.tab == 'Sheet1'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_bad_kard_error_multiple_errors_sync():
    """Test that multiple cardinality errors are raised as ExceptionsGroup in sync mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_multiple.xlsx'
    with pytest.raises(ExceptionsGroup) as exc:
        ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)

    ex = exc.value
    assert len(ex.exceptions) == 2
    headers = {e.header for e in ex.exceptions}
    assert 'testEenvoudigTypeMetKard' in headers
    assert 'testStringField[]' in headers


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
async def test_bad_kard_error_multiple_errors_async():
    """Test that multiple cardinality errors are raised as ExceptionsGroup in async mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_multiple.xlsx'
    with pytest.raises(ExceptionsGroup) as exc:
        await ExcelImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)

    ex = exc.value
    assert len(ex.exceptions) == 2
    headers = {e.header for e in ex.exceptions}
    assert 'testEenvoudigTypeMetKard' in headers
    assert 'testStringField[]' in headers


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_bad_kard_error_deep_path_missing_indicator_sync():
    """Test that missing cardinality indicator on 3-level deep path with multiple cardinalities raises DotnotationListOfListError in sync mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_deep.xlsx'
    from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError
    with pytest.raises(ExceptionsGroup) as exc:
        ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)

    ex = exc.value
    assert len(ex.exceptions) == 1
    assert isinstance(ex.exceptions[0], DotnotationListOfListError)
    err = ex.exceptions[0]
    assert 'testComplexTypeMetKard.testComplexType2MetKard.testKwantWrd' in str(err)
    assert 'multiple attributes with cardinality' in str(err).lower()


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
async def test_bad_kard_error_deep_path_missing_indicator_async():
    """Test that missing cardinality indicator on 3-level deep path with multiple cardinalities raises DotnotationListOfListError in async mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_deep.xlsx'
    from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError
    with pytest.raises(ExceptionsGroup) as exc:
        await ExcelImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)

    ex = exc.value
    assert len(ex.exceptions) == 1
    assert isinstance(ex.exceptions[0], DotnotationListOfListError)
    err = ex.exceptions[0]
    assert 'testComplexTypeMetKard.testComplexType2MetKard.testKwantWrd' in str(err)
    assert 'multiple attributes with cardinality' in str(err).lower()


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_bad_kard_error_deep_path_single_cardinality_sync():
    """Test that missing cardinality indicator on deep path with SINGLE cardinality can be fixed in sync mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_deep_single.xlsx'
    with pytest.raises(ExceptionsGroup) as exc:
        ExcelImporter.to_objects(filepath=file_location, model_directory=model_directory_path)

    ex = exc.value
    assert len(ex.exceptions) == 1
    assert isinstance(ex.exceptions[0], DotnotationIncorrectError)
    err = ex.exceptions[0]
    assert err.header == 'testComplexType.testComplexType2MetKard.testKwantWrd'
    # Single cardinality at position 1 (testComplexType2MetKard) - should add [] after it
    assert err.expected_header == 'testComplexType.testComplexType2MetKard[].testKwantWrd'
    assert 'attribute at position 1 has cardinality' in str(err)
    assert err.tab == 'Sheet'


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
async def test_bad_kard_error_deep_path_single_cardinality_async():
    """Test that missing cardinality indicator on deep path with SINGLE cardinality can be fixed in async mode."""
    file_location = Path(__file__).parent / 'Testfiles' / 'bad_kard_header_deep_single.xlsx'
    with pytest.raises(ExceptionsGroup) as exc:
        await ExcelImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)

    ex = exc.value
    assert len(ex.exceptions) == 1
    assert isinstance(ex.exceptions[0], DotnotationIncorrectError)
    err = ex.exceptions[0]
    assert err.header == 'testComplexType.testComplexType2MetKard.testKwantWrd'
    # Single cardinality at position 1 (testComplexType2MetKard) - should add [] after it
    assert err.expected_header == 'testComplexType.testComplexType2MetKard[].testKwantWrd'
    assert 'attribute at position 1 has cardinality' in str(err)
    assert err.tab == 'Sheet'