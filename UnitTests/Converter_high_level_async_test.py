import asyncio
import os
from datetime import date
from pathlib import Path

import pytest
from pandas._testing import assert_frame_equal

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.FileFormats.PandasConverter import PandasConverter
from otlmow_converter.OtlmowConverter import OtlmowConverter, to_objects, to_file, to_dicts, to_dotnotation_dicts, \
    to_dataframe, to_dotnotation_dicts_async, to_dicts_async, to_objects_async, to_dataframe_async, to_file_async

model_directory_path = Path(__file__).parent / 'TestModel'


def return_test_objects() -> [AllCasesTestClass, AnotherTestClass]:
    instance1 = AllCasesTestClass()
    instance1.assetId.identificator = 'id1'
    instance1.testBooleanField = True
    instance1.testDateField = date(2020, 1, 1)
    instance1.testStringFieldMetKard = ['test1', 'test2']

    instance2 = AnotherTestClass()
    instance2.assetId.identificator = 'id2'
    instance2.notitie = 'note'
    instance2.non_conform_attribute = 'non conform value'
    return [instance1, instance2]


@pytest.mark.asyncio
async def test_dataframe_to_dotnotation_dicts():
    orig_list_of_objects = return_test_objects()
    df = await PandasConverter.convert_objects_to_single_dataframe_async(list_of_objects=orig_list_of_objects)
    expected_list_of_ddicts = [await DotnotationDictConverter.to_dict_async(o) for o in orig_list_of_objects]

    list_of_ddicts_gen = to_dotnotation_dicts_async(df, model_directory=model_directory_path)
    new_list_of_ddicts = await OtlmowConverter.collect_to_list(list_of_ddicts_gen)
    assert expected_list_of_ddicts == list(new_list_of_ddicts)


@pytest.mark.asyncio
async def test_dataframe_to_dicts():
    orig_list_of_objects = return_test_objects()
    df = await PandasConverter.convert_objects_to_single_dataframe_async(list_of_objects=orig_list_of_objects)
    expected_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]

    list_of_dicts_gen = to_dicts_async(df, model_directory=model_directory_path)
    new_list_of_dicts = await OtlmowConverter.collect_to_list(list_of_dicts_gen)
    assert expected_list_of_dicts == list(new_list_of_dicts)


@pytest.mark.asyncio
async def test_dotnotation_dicts_to_dataframe():
    orig_list_of_objects = return_test_objects()
    orig_list_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]
    expected_df = await PandasConverter.convert_objects_to_single_dataframe_async(list_of_objects=orig_list_of_objects)

    created_df = await OtlmowConverter.to_dataframe_async(
        subject=orig_list_of_ddicts, model_directory=model_directory_path)
    assert_frame_equal(expected_df, created_df)


@pytest.mark.asyncio
async def test_dicts_to_dataframe():
    orig_list_of_objects = return_test_objects()
    orig_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]
    expected_df = await PandasConverter.convert_objects_to_single_dataframe_async(list_of_objects=orig_list_of_objects)

    created_df = await OtlmowConverter.to_dataframe_async(subject=orig_list_of_dicts, model_directory=model_directory_path)
    assert_frame_equal(expected_df, created_df)


@pytest.mark.asyncio
async def test_file_to_dataframe():
    orig_list_of_objects = return_test_objects()
    expected_df = await PandasConverter.convert_objects_to_single_dataframe_async(list_of_objects=orig_list_of_objects)
    json_file_path = Path(__file__).parent / 'test_file_to_dataframe.json'
    await OtlmowConverter.from_objects_to_file_async(sequence_of_objects=orig_list_of_objects, file_path=json_file_path,
                                         model_directory=model_directory_path)

    created_df = await to_dataframe_async(json_file_path, model_directory=model_directory_path)
    assert_frame_equal(expected_df, created_df)

    os.unlink(json_file_path)


@pytest.mark.asyncio
async def test_dicts_to_dotnotation_dicts():
    orig_list_of_objects = return_test_objects()
    orig_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]
    expected_list_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]

    list_of_ddicts_gen = to_dotnotation_dicts_async(orig_list_of_dicts, model_directory=model_directory_path)
    new_list_of_ddicts = await OtlmowConverter.collect_to_list(list_of_ddicts_gen)
    assert expected_list_of_ddicts == list(new_list_of_ddicts)


@pytest.mark.asyncio
async def test_dotnotation_dicts_to_dicts():
    orig_list_of_objects = return_test_objects()
    orig_list_of_ddicts = [await DotnotationDictConverter.to_dict_async(o) for o in orig_list_of_objects]
    expected_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]

    list_of_dicts_gen = to_dicts_async(orig_list_of_ddicts, model_directory=model_directory_path)
    new_list_of_dicts = await OtlmowConverter.collect_to_list(list_of_dicts_gen)
    assert expected_list_of_dicts == list(new_list_of_dicts)


@pytest.mark.asyncio
async def test_dataframe_to_dataframe():
    orig_list_of_objects = return_test_objects()
    expected_df = await PandasConverter.convert_objects_to_single_dataframe_async(list_of_objects=orig_list_of_objects)

    created_df = await to_dataframe_async(expected_df, model_directory=model_directory_path)
    assert_frame_equal(expected_df, created_df)


@pytest.mark.asyncio
async def test_dicts_to_dicts():
    orig_list_of_objects = return_test_objects()
    orig_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]

    list_of_dicts_gen = to_dicts_async(orig_list_of_dicts, model_directory=model_directory_path)
    new_list_of_dicts = await OtlmowConverter.collect_to_list(list_of_dicts_gen)
    assert orig_list_of_dicts == new_list_of_dicts


@pytest.mark.asyncio
async def test_dotnotation_dicts_to_dotnotation_dicts():
    orig_list_of_objects = return_test_objects()
    orig_list_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]

    list_of_ddicts_gen = to_dotnotation_dicts_async(orig_list_of_ddicts, model_directory=model_directory_path)
    new_list_of_ddicts = await OtlmowConverter.collect_to_list(list_of_ddicts_gen)
    assert orig_list_of_ddicts == list(new_list_of_ddicts)


@pytest.mark.asyncio
async def test_file_to_dotnotation_dicts():
    orig_list_of_objects = return_test_objects()
    json_file_path = Path(__file__).parent / 'test_file_to_dotnotation_dicts.json'
    await OtlmowConverter.from_objects_to_file_async(sequence_of_objects=orig_list_of_objects, file_path=json_file_path,
                                         model_directory=model_directory_path)

    list_of_ddicts_gen = to_dotnotation_dicts_async(subject=json_file_path, model_directory=model_directory_path)
    new_list_of_ddicts = await OtlmowConverter.collect_to_list(list_of_ddicts_gen)

    assert new_list_of_ddicts == [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]
    os.unlink(json_file_path)


@pytest.mark.asyncio
async def test_file_to_dicts():
    orig_list_of_objects = return_test_objects()
    json_file_path = Path(__file__).parent / 'test_file_to_dicts.json'
    await OtlmowConverter.from_objects_to_file_async(sequence_of_objects=orig_list_of_objects, file_path=json_file_path,
                                         model_directory=model_directory_path)

    list_of_dicts_gen = to_dicts_async(subject=json_file_path, model_directory=model_directory_path)
    new_list_of_ddicts = await OtlmowConverter.collect_to_list(list_of_dicts_gen)

    assert new_list_of_ddicts == [o.to_dict() for o in orig_list_of_objects]
    os.unlink(json_file_path)


@pytest.mark.asyncio
async def test_objects_to_dataframe():
    orig_list_of_objects = return_test_objects()
    expected_df = await PandasConverter.convert_objects_to_single_dataframe_async(list_of_objects=orig_list_of_objects)
    created_df = await to_dataframe_async(orig_list_of_objects, model_directory=model_directory_path)
    assert_frame_equal(expected_df, created_df)


@pytest.mark.asyncio
async def test_objects_to_dicts():
    orig_list_of_objects = return_test_objects()
    expected_dicts = [o.to_dict() for o in orig_list_of_objects]
    list_of_dicts_gen = to_dicts_async(orig_list_of_objects, model_directory=model_directory_path)
    new_list_of_dicts = await OtlmowConverter.collect_to_list(list_of_dicts_gen)
    assert new_list_of_dicts == expected_dicts


@pytest.mark.asyncio
async def test_objects_to_dotnotation_dicts():
    orig_list_of_objects = return_test_objects()
    expected_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]
    list_of_ddicts_gen = to_dotnotation_dicts_async(orig_list_of_objects, model_directory=model_directory_path)
    new_list_of_ddicts = await OtlmowConverter.collect_to_list(list_of_ddicts_gen)
    assert list(new_list_of_ddicts) == expected_ddicts


@pytest.mark.asyncio
async def test_dataframe_to_file():
    orig_list_of_objects = return_test_objects()
    df = await PandasConverter.convert_objects_to_single_dataframe_async(list_of_objects=orig_list_of_objects)
    excel_file_path = Path(__file__).parent / 'test_dataframe_to_file.xlsx'
    json_file_path = Path(__file__).parent / 'test_dataframe_to_file.json'
    csv_file_path = Path(__file__).parent / 'test_dataframe_to_file.csv'
    csv_file_path_2 = Path(__file__).parent / 'test_dataframe_to_file_onderdeel_AllCasesTestClass.csv'
    csv_file_path_3 = Path(__file__).parent / 'test_dataframe_to_file_onderdeel_AnotherTestClass.csv'

    geojson_file_path = Path(__file__).parent / 'test_dataframe_to_file.geojson'

    await to_file_async(subject=df, file_path=excel_file_path, model_directory=model_directory_path)
    from_excel_objects = await OtlmowConverter.from_file_to_objects_async(excel_file_path,
                                                                          model_directory=model_directory_path)
    assert orig_list_of_objects == list(from_excel_objects)

    await to_file_async(subject=df, file_path=json_file_path, model_directory=model_directory_path)
    from_json_objects = await OtlmowConverter.from_file_to_objects_async(json_file_path,
                                                                    model_directory=model_directory_path)
    assert orig_list_of_objects == from_json_objects

    await to_file_async(subject=df, file_path=csv_file_path, model_directory=model_directory_path)
    from_csv_objects_2 = await OtlmowConverter.from_file_to_objects_async(csv_file_path_2, model_directory=model_directory_path)
    from_csv_objects_3 = await OtlmowConverter.from_file_to_objects_async(csv_file_path_3, model_directory=model_directory_path)
    combined_list = list(from_csv_objects_2) + list(from_csv_objects_3)
    assert orig_list_of_objects == combined_list

    await to_file_async(subject=df, file_path=geojson_file_path, model_directory=model_directory_path)
    from_geojson_objects = await OtlmowConverter.from_file_to_objects(geojson_file_path, model_directory=model_directory_path)
    assert orig_list_of_objects == list(from_geojson_objects)

    os.unlink(excel_file_path)
    os.unlink(json_file_path)
    os.unlink(csv_file_path_2)
    os.unlink(csv_file_path_3)
    os.unlink(geojson_file_path)


@pytest.mark.asyncio
async def test_dotnotation_dicts_to_file():
    orig_list_of_objects = return_test_objects()
    orig_list_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]
    excel_file_path = Path(__file__).parent / 'test_dotnotation_dicts_to_file.xlsx'
    json_file_path = Path(__file__).parent / 'test_dotnotation_dicts_to_file.json'
    csv_file_path = Path(__file__).parent / 'test_dotnotation_dicts_to_file.csv'
    csv_file_path_2 = Path(__file__).parent / 'test_dotnotation_dicts_to_file_onderdeel_AllCasesTestClass.csv'
    csv_file_path_3 = Path(__file__).parent / 'test_dotnotation_dicts_to_file_onderdeel_AnotherTestClass.csv'
    geojson_file_path = Path(__file__).parent / 'test_dotnotation_dicts_to_file.geojson'

    await to_file_async(subject=orig_list_of_ddicts, file_path=excel_file_path, model_directory=model_directory_path)
    from_excel_objects = await OtlmowConverter.from_file_to_objects_async(excel_file_path,
                                                                     model_directory=model_directory_path)
    assert orig_list_of_objects == list(from_excel_objects)

    await to_file_async(subject=orig_list_of_ddicts, file_path=json_file_path, model_directory=model_directory_path)
    from_json_objects = await OtlmowConverter.from_file_to_objects_async(json_file_path, model_directory=model_directory_path)
    assert orig_list_of_objects == list(from_json_objects)

    await to_file_async(subject=orig_list_of_ddicts, file_path=csv_file_path, model_directory=model_directory_path)
    from_csv_objects_2 = await OtlmowConverter.from_file_to_objects_async(csv_file_path_2, model_directory=model_directory_path)
    from_csv_objects_3 = await OtlmowConverter.from_file_to_objects_async(csv_file_path_3, model_directory=model_directory_path)
    combined_list = list(from_csv_objects_2) + list(from_csv_objects_3)
    assert orig_list_of_objects == combined_list

    await to_file_async(subject=orig_list_of_ddicts, file_path=geojson_file_path,
                            model_directory=model_directory_path)
    from_geojson_objects = await OtlmowConverter.from_file_to_objects_async(geojson_file_path, model_directory=model_directory_path)
    assert orig_list_of_objects == list(from_geojson_objects)

    os.unlink(excel_file_path)
    os.unlink(json_file_path)
    os.unlink(csv_file_path_2)
    os.unlink(csv_file_path_3)
    os.unlink(geojson_file_path)


@pytest.mark.asyncio
async def test_file_to_file():
    orig_list_of_objects = return_test_objects()
    excel_file_path = Path(__file__).parent / 'test_file_to_file.xlsx'
    json_file_path = Path(__file__).parent / 'test_file_to_file.json'
    csv_file_path = Path(__file__).parent / 'test_file_to_file.csv'
    csv_file_path_2 = Path(__file__).parent / 'test_file_to_file_onderdeel_AllCasesTestClass.csv'
    csv_file_path_3 = Path(__file__).parent / 'test_file_to_file_onderdeel_AnotherTestClass.csv'
    geojson_file_path = Path(__file__).parent / 'test_file_to_file.geojson'
    created_excel_file_path = Path(__file__).parent / 'created_test_file_to_file.xlsx'
    created_json_file_path = Path(__file__).parent / 'created_test_file_to_file.json'
    created_csv_file_path = Path(__file__).parent / 'created_test_file_to_file.csv'
    created_csv_file_path_2 = Path(__file__).parent / 'created_test_file_to_file_onderdeel_AllCasesTestClass.csv'
    created_csv_file_path_3 = Path(__file__).parent / 'created_test_file_to_file_onderdeel_AnotherTestClass.csv'
    created_geojson_file_path = Path(__file__).parent / 'created_test_file_to_file.geojson'

    await OtlmowConverter.from_objects_to_file_async(
        sequence_of_objects=orig_list_of_objects, file_path=excel_file_path,model_directory=model_directory_path)

    await to_file_async(subject=excel_file_path, file_path=created_excel_file_path,
                        model_directory=model_directory_path)
    imported_excel_file = await OtlmowConverter.from_file_to_objects_async(
        excel_file_path, model_directory=model_directory_path)
    imported_created_excel_file = await OtlmowConverter.from_file_to_objects_async(
        created_excel_file_path, model_directory=model_directory_path)
    assert list(imported_excel_file) == list(imported_created_excel_file)

    await OtlmowConverter.from_objects_to_file_async(sequence_of_objects=orig_list_of_objects, file_path=json_file_path,
                                            model_directory=model_directory_path)
    await to_file_async(subject=json_file_path, file_path=created_json_file_path, model_directory=model_directory_path)
    imported_json_file = await OtlmowConverter.from_file_to_objects_async(json_file_path, model_directory=model_directory_path)
    imported_created_json_file = await OtlmowConverter.from_file_to_objects_async(created_json_file_path,
                                                                      model_directory=model_directory_path)
    assert list(imported_json_file) == list(imported_created_json_file)

    await OtlmowConverter.from_objects_to_file_async(sequence_of_objects=orig_list_of_objects, file_path=csv_file_path,
                                         model_directory=model_directory_path)
    await to_file_async(subject=csv_file_path_2, file_path=created_csv_file_path, model_directory=model_directory_path)
    await to_file_async(subject=csv_file_path_3, file_path=created_csv_file_path, model_directory=model_directory_path)
    imported_csv_file_2 = await OtlmowConverter.from_file_to_objects_async(
        csv_file_path_2, model_directory=model_directory_path)
    imported_csv_file_3 = await OtlmowConverter.from_file_to_objects_async(csv_file_path_3, model_directory=model_directory_path)
    imported_created_csv_file_2 = await OtlmowConverter.from_file_to_objects_async(created_csv_file_path_2, model_directory=model_directory_path)
    imported_created_csv_file_3 = await OtlmowConverter.from_file_to_objects_async(created_csv_file_path_3, model_directory=model_directory_path)
    combined_list = list(imported_csv_file_2) + list(imported_csv_file_3)
    combined_created_list = list(imported_created_csv_file_2) + list(imported_created_csv_file_3)
    assert combined_list == combined_created_list

    await OtlmowConverter.from_objects_to_file_async(sequence_of_objects=orig_list_of_objects, file_path=geojson_file_path,
                                         model_directory=model_directory_path)
    await to_file_async(subject=geojson_file_path, file_path=created_geojson_file_path, model_directory=model_directory_path)
    imported_geojson_file = await OtlmowConverter.from_file_to_objects_async(geojson_file_path,
                                                                        model_directory=model_directory_path)
    imported_created_geojson_file = await OtlmowConverter.from_file_to_objects_async(created_geojson_file_path,
                                                                         model_directory=model_directory_path)
    assert list(imported_geojson_file) == list(imported_created_geojson_file)

    os.unlink(excel_file_path)
    os.unlink(created_excel_file_path)
    os.unlink(json_file_path)
    os.unlink(created_json_file_path)
    os.unlink(csv_file_path_2)
    os.unlink(csv_file_path_3)
    os.unlink(created_csv_file_path_2)
    os.unlink(created_csv_file_path_3)
    os.unlink(geojson_file_path)
    os.unlink(created_geojson_file_path)


@pytest.mark.asyncio
async def test_objects_to_file():
    orig_list_of_objects = return_test_objects()
    excel_file_path = Path(__file__).parent / 'test_objects_to_file.xlsx'
    json_file_path = Path(__file__).parent / 'test_objects_to_file.json'
    csv_file_path = Path(__file__).parent / 'test_objects_to_file.csv'
    csv_file_path_2 = Path(__file__).parent / 'test_objects_to_file_onderdeel_AllCasesTestClass.csv'
    csv_file_path_3 = Path(__file__).parent / 'test_objects_to_file_onderdeel_AnotherTestClass.csv'
    geojson_file_path = Path(__file__).parent / 'test_objects_to_file.geojson'

    await to_file_async(subject=orig_list_of_objects, file_path=json_file_path)
    from_json_objects = await OtlmowConverter.from_file_to_objects_async(
        json_file_path, model_directory=model_directory_path)
    assert orig_list_of_objects == from_json_objects

    await to_file_async(subject=orig_list_of_objects, file_path=excel_file_path)
    from_excel_objects = await OtlmowConverter.from_file_to_objects_async(
        excel_file_path, model_directory=model_directory_path)
    assert orig_list_of_objects == from_excel_objects

    await to_file_async(subject=orig_list_of_objects, file_path=csv_file_path)
    from_csv_objects_2 = await OtlmowConverter.from_file_to_objects_async(
        csv_file_path_2, model_directory=model_directory_path)
    from_csv_objects_3 = await OtlmowConverter.from_file_to_objects_async(
        csv_file_path_3, model_directory=model_directory_path)
    combined_list = from_csv_objects_2 + from_csv_objects_3
    assert orig_list_of_objects == combined_list

    await to_file_async(subject=orig_list_of_objects, file_path=geojson_file_path)
    from_geojson_objects = await OtlmowConverter.from_file_to_objects_async(
        geojson_file_path, model_directory=model_directory_path)
    assert orig_list_of_objects == from_geojson_objects

    os.unlink(excel_file_path)
    os.unlink(json_file_path)
    os.unlink(csv_file_path_2)
    os.unlink(csv_file_path_3)
    os.unlink(geojson_file_path)


@pytest.mark.asyncio
async def test_dicts_to_file():
    orig_list_of_objects = return_test_objects()
    orig_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]
    excel_file_path = Path(__file__).parent / 'test_dicts_to_file.xlsx'
    json_file_path = Path(__file__).parent / 'test_dicts_to_file.json'
    csv_file_path = Path(__file__).parent / 'test_dicts_to_file.csv'
    csv_file_path_2 = Path(__file__).parent / 'test_dicts_to_file_onderdeel_AllCasesTestClass.csv'
    csv_file_path_3 = Path(__file__).parent / 'test_dicts_to_file_onderdeel_AnotherTestClass.csv'
    geojson_file_path = Path(__file__).parent / 'test_dicts_to_file.geojson'

    await to_file_async(subject=orig_list_of_dicts, file_path=json_file_path, model_directory=model_directory_path)
    from_json_objects = await OtlmowConverter.from_file_to_objects_async(json_file_path, model_directory=model_directory_path)
    assert orig_list_of_objects == list(from_json_objects)

    await to_file_async(subject=orig_list_of_dicts, file_path=excel_file_path, model_directory=model_directory_path)
    from_excel_objects = await OtlmowConverter.from_file_to_objects_async(excel_file_path, model_directory=model_directory_path)
    assert orig_list_of_objects == list(from_excel_objects)

    await to_file_async(subject=orig_list_of_dicts, file_path=csv_file_path, model_directory=model_directory_path)
    from_csv_objects_2 = await OtlmowConverter.from_file_to_objects_async(csv_file_path_2, model_directory=model_directory_path)
    from_csv_objects_3 = await OtlmowConverter.from_file_to_objects_async(csv_file_path_3, model_directory=model_directory_path)
    combined_list = list(from_csv_objects_2) + list(from_csv_objects_3)
    assert orig_list_of_objects == combined_list

    await to_file_async(subject=orig_list_of_dicts, file_path=geojson_file_path,
                            model_directory=model_directory_path)
    from_geojson_objects = await OtlmowConverter.from_file_to_objects_async(geojson_file_path, model_directory=model_directory_path)
    assert orig_list_of_objects == list(from_geojson_objects)

    os.unlink(excel_file_path)
    os.unlink(json_file_path)
    os.unlink(csv_file_path_2)
    os.unlink(csv_file_path_3)
    os.unlink(geojson_file_path)


@pytest.mark.asyncio
async def test_file_to_objects():
    excel_file_path = Path(__file__).parent / 'test_file_to_objects.xlsx'
    json_file_path = Path(__file__).parent / 'test_file_to_objects.json'
    csv_file_path = Path(__file__).parent / 'test_file_to_objects.csv'
    csv_file_path_2 = Path(__file__).parent / 'test_file_to_objects_onderdeel_AllCasesTestClass.csv'
    csv_file_path_3 = Path(__file__).parent / 'test_file_to_objects_onderdeel_AnotherTestClass.csv'
    geojson_file_path = Path(__file__).parent / 'test_file_to_objects.geojson'

    orig_list_of_objects = return_test_objects()

    await OtlmowConverter.from_objects_to_file_async(sequence_of_objects=orig_list_of_objects, file_path=csv_file_path)
    from_csv_objects_2_gen = to_objects_async(csv_file_path_2, model_directory=model_directory_path)
    from_csv_objects_2 = await OtlmowConverter.collect_to_list(from_csv_objects_2_gen)
    from_csv_objects_3_gen = to_objects_async(csv_file_path_3, model_directory=model_directory_path)
    from_csv_objects_3 = await OtlmowConverter.collect_to_list(from_csv_objects_3_gen)
    combined_list = from_csv_objects_2 + from_csv_objects_3
    assert orig_list_of_objects == combined_list

    await OtlmowConverter.from_objects_to_file_async(sequence_of_objects=orig_list_of_objects, file_path=excel_file_path)
    from_excel_objects_gen = to_objects_async(excel_file_path, model_directory=model_directory_path)
    from_excel_objects = await OtlmowConverter.collect_to_list(from_excel_objects_gen)
    assert orig_list_of_objects == from_excel_objects

    await OtlmowConverter.from_objects_to_file_async(sequence_of_objects=orig_list_of_objects, file_path=json_file_path)
    from_json_objects_gen = to_objects_async(json_file_path, model_directory=model_directory_path)
    from_json_objects = await OtlmowConverter.collect_to_list(from_json_objects_gen)
    assert orig_list_of_objects == from_json_objects

    await OtlmowConverter.from_objects_to_file_async(sequence_of_objects=orig_list_of_objects, file_path=geojson_file_path)
    from_geojson_objects_gen = to_objects_async(geojson_file_path, model_directory=model_directory_path)
    from_geojson_objects = await OtlmowConverter.collect_to_list(from_geojson_objects_gen)
    assert orig_list_of_objects == from_geojson_objects

    os.unlink(excel_file_path)
    os.unlink(json_file_path)
    os.unlink(csv_file_path_2)
    os.unlink(csv_file_path_3)
    os.unlink(geojson_file_path)


@pytest.mark.asyncio
async def test_objects_to_objects():
    orig_list_of_objects = return_test_objects()
    new_list_of_objects = to_objects_async(orig_list_of_objects, model_directory=model_directory_path)
    new_list_of_objects = await OtlmowConverter.collect_to_list(new_list_of_objects)
    assert orig_list_of_objects == list(new_list_of_objects)


@pytest.mark.asyncio
async def test_dicts_to_objects():
    orig_list_of_objects = return_test_objects()
    sequence_of_dicts = [o.to_dict() for o in orig_list_of_objects]
    new_list_of_objects_gen = to_objects_async(sequence_of_dicts, model_directory=model_directory_path)
    new_list_of_objects = await OtlmowConverter.collect_to_list(new_list_of_objects_gen)
    assert orig_list_of_objects == list(new_list_of_objects)


@pytest.mark.asyncio
async def test_dotnotation_dicts_to_objects():
    orig_list_of_objects = return_test_objects()
    sequence_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]
    list_of_objects_gen = to_objects_async(sequence_of_ddicts, model_directory=model_directory_path)
    new_list_of_objects = await OtlmowConverter.collect_to_list(list_of_objects_gen)
    assert orig_list_of_objects == list(new_list_of_objects)


@pytest.mark.asyncio
async def test_dataframe_to_objects():
    orig_list_of_objects = return_test_objects()
    df = await PandasConverter.convert_objects_to_single_dataframe_async(list_of_objects=orig_list_of_objects)
    list_of_objects_gen = to_objects_async(df, model_directory=model_directory_path)
    new_list_of_objects = await OtlmowConverter.collect_to_list(list_of_objects_gen)

    assert orig_list_of_objects == new_list_of_objects
