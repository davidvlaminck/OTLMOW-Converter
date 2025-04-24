from datetime import date
from pathlib import Path

import pytest
from otlmow_model.OtlmowModel.Exceptions.NonStandardAttributeWarning import NonStandardAttributeWarning
from pandas._testing import assert_frame_equal

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.FileFormats.PandasConverter import PandasConverter
from otlmow_converter.OtlmowConverter import OtlmowConverter, to_objects, to_file, to_dicts, to_dotnotation_dicts, \
    to_dataframe

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

# +-------------------+------+------+-------+---------+----+
# | from     -->   to | objs | file | dicts | d_dicts | df |
# +-------------------+------+------+-------+---------+----+
# | objects           |  X   |  X   |   X   |    X    | X  |
# | file              |  X   |  X   |   X   |    X    | X  |
# | dicts             |  X   |  X   |   X   |    X    | X  |
# | dotnotation_dicts |  X   |  X   |   X   |    X    | X  |
# | dataframe         |  X   |  X   |   X   |    X    | X  |
# +-------------------+------+------+-------+---------+----+


def test_dataframe_to_dotnotation_dicts():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=orig_list_of_objects)
        expected_list_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]

        new_list_of_ddicts = to_dotnotation_dicts(df, model_directory=model_directory_path)
        assert expected_list_of_ddicts == list(new_list_of_ddicts)


def test_dataframe_to_dicts():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=orig_list_of_objects)
        expected_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]

        new_list_of_dicts = to_dicts(df, model_directory=model_directory_path)
        assert expected_list_of_dicts == list(new_list_of_dicts)


def test_dotnotation_dicts_to_dataframe():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        orig_list_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]
        expected_df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=orig_list_of_objects)

        created_df = OtlmowConverter.to_dataframe(subject=orig_list_of_ddicts, model_directory=model_directory_path)
        assert_frame_equal(expected_df, created_df)


def test_dicts_to_dataframe():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        orig_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]
        expected_df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=orig_list_of_objects)

        created_df = OtlmowConverter.to_dataframe(subject=orig_list_of_dicts, model_directory=model_directory_path)
        assert_frame_equal(expected_df, created_df)


def test_file_to_dataframe():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        expected_df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=orig_list_of_objects)
        json_file_path = Path(__file__).parent / 'test_file_to_dataframe.json'
        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=json_file_path,
                                             model_directory=model_directory_path)

        created_df = to_dataframe(json_file_path, model_directory=model_directory_path)
        assert_frame_equal(expected_df, created_df)

        json_file_path.unlink()


def test_dicts_to_dotnotation_dicts():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        orig_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]
        expected_list_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]

        new_list_of_ddicts = to_dotnotation_dicts(orig_list_of_dicts, model_directory=model_directory_path)
        assert expected_list_of_ddicts == list(new_list_of_ddicts)


def test_dotnotation_dicts_to_dicts():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        orig_list_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]
        expected_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]

        new_list_of_dicts = to_dicts(orig_list_of_ddicts, model_directory=model_directory_path)
        assert expected_list_of_dicts == list(new_list_of_dicts)


def test_dataframe_to_dataframe():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        expected_df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=orig_list_of_objects)

        created_df = to_dataframe(expected_df, model_directory=model_directory_path)
        assert_frame_equal(expected_df, created_df)


def test_dicts_to_dicts():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        orig_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]

        new_list_of_dicts = to_dicts(orig_list_of_dicts, model_directory=model_directory_path)
        assert orig_list_of_dicts == list(new_list_of_dicts)


def test_dotnotation_dicts_to_dotnotation_dicts():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        orig_list_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]

        new_list_of_ddicts = to_dotnotation_dicts(orig_list_of_ddicts, model_directory=model_directory_path)
        assert orig_list_of_ddicts == list(new_list_of_ddicts)


def test_file_to_dotnotation_dicts():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        json_file_path = Path(__file__).parent / 'test_file_to_dotnotation_dicts.json'
        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=json_file_path,
                                             model_directory=model_directory_path)

        new_list_of_ddicts = list(to_dotnotation_dicts(subject=json_file_path, model_directory=model_directory_path))

        assert new_list_of_ddicts == [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]
        json_file_path.unlink()


def test_file_to_dicts():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        json_file_path = Path(__file__).parent / 'test_file_to_dicts.json'
        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=json_file_path,
                                             model_directory=model_directory_path)

        new_list_of_dicts = list(to_dicts(subject=json_file_path, model_directory=model_directory_path))

        assert new_list_of_dicts == [o.to_dict() for o in orig_list_of_objects]
        json_file_path.unlink()


def test_objects_to_dataframe():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        expected_df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=orig_list_of_objects)
        created_df = to_dataframe(orig_list_of_objects, model_directory=model_directory_path)
        assert_frame_equal(expected_df, created_df)


def test_objects_to_dicts():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        expected_dicts = [o.to_dict() for o in orig_list_of_objects]
        new_list_of_dicts = list(to_dicts(orig_list_of_objects, model_directory=model_directory_path))
        assert new_list_of_dicts == expected_dicts


def test_objects_to_dotnotation_dicts():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        expected_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]
        new_list_of_ddicts = to_dotnotation_dicts(orig_list_of_objects, model_directory=model_directory_path)
        assert list(new_list_of_ddicts) == expected_ddicts


def test_dataframe_to_file():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=orig_list_of_objects)
        excel_file_path = Path(__file__).parent / 'test_dataframe_to_file.xlsx'
        json_file_path = Path(__file__).parent / 'test_dataframe_to_file.json'
        csv_file_path = Path(__file__).parent / 'test_dataframe_to_file.csv'
        csv_file_path_2 = Path(__file__).parent / 'test_dataframe_to_file_onderdeel_AllCasesTestClass.csv'
        csv_file_path_3 = Path(__file__).parent / 'test_dataframe_to_file_onderdeel_AnotherTestClass.csv'

        geojson_file_path = Path(__file__).parent / 'test_dataframe_to_file.geojson'

        created_file_paths = OtlmowConverter.to_file(subject=df, file_path=excel_file_path, model_directory=model_directory_path)
        assert created_file_paths == (excel_file_path,)
        from_excel_objects = OtlmowConverter.from_file_to_objects(excel_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_excel_objects)

        created_file_paths = OtlmowConverter.to_file(subject=df, file_path=json_file_path, model_directory=model_directory_path)
        assert created_file_paths == (json_file_path,)
        from_json_objects = OtlmowConverter.from_file_to_objects(json_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_json_objects)

        created_file_paths = OtlmowConverter.to_file(subject=df, file_path=csv_file_path, model_directory=model_directory_path)
        assert created_file_paths == (csv_file_path_2, csv_file_path_3)
        from_csv_objects_2 = OtlmowConverter.from_file_to_objects(csv_file_path_2, model_directory=model_directory_path)
        from_csv_objects_3 = OtlmowConverter.from_file_to_objects(csv_file_path_3, model_directory=model_directory_path)
        combined_list = list(from_csv_objects_2) + list(from_csv_objects_3)
        assert orig_list_of_objects == combined_list

        created_file_paths = OtlmowConverter.to_file(subject=df, file_path=geojson_file_path, model_directory=model_directory_path)
        assert created_file_paths == (geojson_file_path,)
        from_geojson_objects = OtlmowConverter.from_file_to_objects(geojson_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_geojson_objects)

        excel_file_path.unlink()
        json_file_path.unlink()
        csv_file_path_2.unlink()
        csv_file_path_3.unlink()
        geojson_file_path.unlink()


def test_dotnotation_dicts_to_file(recwarn):
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        orig_list_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]
        excel_file_path = Path(__file__).parent / 'test_dotnotation_dicts_to_file.xlsx'
        json_file_path = Path(__file__).parent / 'test_dotnotation_dicts_to_file.json'
        csv_file_path = Path(__file__).parent / 'test_dotnotation_dicts_to_file.csv'
        csv_file_path_2 = Path(__file__).parent / 'test_dotnotation_dicts_to_file_onderdeel_AllCasesTestClass.csv'
        csv_file_path_3 = Path(__file__).parent / 'test_dotnotation_dicts_to_file_onderdeel_AnotherTestClass.csv'
        geojson_file_path = Path(__file__).parent / 'test_dotnotation_dicts_to_file.geojson'

        OtlmowConverter.to_file(subject=orig_list_of_ddicts, file_path=excel_file_path, model_directory=model_directory_path)
        from_excel_objects = OtlmowConverter.from_file_to_objects(excel_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_excel_objects)

        OtlmowConverter.to_file(subject=orig_list_of_ddicts, file_path=json_file_path, model_directory=model_directory_path)
        from_json_objects = OtlmowConverter.from_file_to_objects(json_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_json_objects)

        OtlmowConverter.to_file(subject=orig_list_of_ddicts, file_path=csv_file_path, model_directory=model_directory_path)
        from_csv_objects_2 = OtlmowConverter.from_file_to_objects(csv_file_path_2, model_directory=model_directory_path)
        from_csv_objects_3 = OtlmowConverter.from_file_to_objects(csv_file_path_3, model_directory=model_directory_path)
        combined_list = list(from_csv_objects_2) + list(from_csv_objects_3)
        assert orig_list_of_objects == combined_list

        OtlmowConverter.to_file(subject=orig_list_of_ddicts, file_path=geojson_file_path,
                                model_directory=model_directory_path)
        from_geojson_objects = OtlmowConverter.from_file_to_objects(geojson_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_geojson_objects)

        excel_file_path.unlink()
        json_file_path.unlink()
        csv_file_path_2.unlink()
        csv_file_path_3.unlink()
        geojson_file_path.unlink()


def test_file_to_file():
    with pytest.warns(NonStandardAttributeWarning):
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

        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=excel_file_path,
                                             model_directory=model_directory_path)
        to_file(subject=excel_file_path, file_path=created_excel_file_path, model_directory=model_directory_path)
        imported_excel_file = OtlmowConverter.from_file_to_objects(excel_file_path, model_directory=model_directory_path)
        imported_created_excel_file = OtlmowConverter.from_file_to_objects(created_excel_file_path,
                                                                           model_directory=model_directory_path)
        assert list(imported_excel_file) == list(imported_created_excel_file)

        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=json_file_path,
                                                model_directory=model_directory_path)
        to_file(subject=json_file_path, file_path=created_json_file_path, model_directory=model_directory_path)
        imported_json_file = OtlmowConverter.from_file_to_objects(json_file_path, model_directory=model_directory_path)
        imported_created_json_file = OtlmowConverter.from_file_to_objects(created_json_file_path,
                                                                          model_directory=model_directory_path)
        assert list(imported_json_file) == list(imported_created_json_file)

        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=csv_file_path,
                                             model_directory=model_directory_path)
        to_file(subject=csv_file_path_2, file_path=created_csv_file_path, model_directory=model_directory_path)
        to_file(subject=csv_file_path_3, file_path=created_csv_file_path, model_directory=model_directory_path)
        imported_csv_file_2 = to_objects(csv_file_path_2, model_directory=model_directory_path)
        imported_csv_file_3 = to_objects(csv_file_path_3, model_directory=model_directory_path)
        imported_created_csv_file_2 = to_objects(created_csv_file_path_2, model_directory=model_directory_path)
        imported_created_csv_file_3 = to_objects(created_csv_file_path_3, model_directory=model_directory_path)
        combined_list = list(imported_csv_file_2) + list(imported_csv_file_3)
        combined_created_list = list(imported_created_csv_file_2) + list(imported_created_csv_file_3)
        assert combined_list == combined_created_list

        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=geojson_file_path,
                                             model_directory=model_directory_path)
        to_file(subject=geojson_file_path, file_path=created_geojson_file_path, model_directory=model_directory_path)
        imported_geojson_file = OtlmowConverter.from_file_to_objects(geojson_file_path, model_directory=model_directory_path)
        imported_created_geojson_file = OtlmowConverter.from_file_to_objects(created_geojson_file_path,
                                                                             model_directory=model_directory_path)
        assert list(imported_geojson_file) == list(imported_created_geojson_file)

        excel_file_path.unlink()
        created_excel_file_path.unlink()
        json_file_path.unlink()
        created_json_file_path.unlink()
        csv_file_path_2.unlink()
        csv_file_path_3.unlink()
        created_csv_file_path_2.unlink()
        created_csv_file_path_3.unlink()
        geojson_file_path.unlink()
        created_geojson_file_path.unlink()


def test_objects_to_file():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        excel_file_path = Path(__file__).parent / 'test_objects_to_file.xlsx'
        json_file_path = Path(__file__).parent / 'test_objects_to_file.json'
        csv_file_path = Path(__file__).parent / 'test_objects_to_file.csv'
        csv_file_path_2 = Path(__file__).parent / 'test_objects_to_file_onderdeel_AllCasesTestClass.csv'
        csv_file_path_3 = Path(__file__).parent / 'test_objects_to_file_onderdeel_AnotherTestClass.csv'
        geojson_file_path = Path(__file__).parent / 'test_objects_to_file.geojson'

        OtlmowConverter.to_file(subject=orig_list_of_objects, file_path=excel_file_path)
        from_excel_objects = OtlmowConverter.from_file_to_objects(excel_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_excel_objects)

        OtlmowConverter.to_file(subject=orig_list_of_objects, file_path=json_file_path)
        from_json_objects = OtlmowConverter.from_file_to_objects(json_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_json_objects)

        OtlmowConverter.to_file(subject=orig_list_of_objects, file_path=csv_file_path)
        from_csv_objects_2 = OtlmowConverter.from_file_to_objects(csv_file_path_2, model_directory=model_directory_path)
        from_csv_objects_3 = OtlmowConverter.from_file_to_objects(csv_file_path_3, model_directory=model_directory_path)
        combined_list = list(from_csv_objects_2) + list(from_csv_objects_3)
        assert orig_list_of_objects == combined_list

        OtlmowConverter.to_file(subject=orig_list_of_objects, file_path=geojson_file_path)
        from_geojson_objects = OtlmowConverter.from_file_to_objects(geojson_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_geojson_objects)

        excel_file_path.unlink()
        json_file_path.unlink()
        csv_file_path_2.unlink()
        csv_file_path_3.unlink()
        geojson_file_path.unlink()


def test_dicts_to_file():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        orig_list_of_dicts = [o.to_dict() for o in orig_list_of_objects]
        excel_file_path = Path(__file__).parent / 'test_dicts_to_file.xlsx'
        json_file_path = Path(__file__).parent / 'test_dicts_to_file.json'
        csv_file_path = Path(__file__).parent / 'test_dicts_to_file.csv'
        csv_file_path_2 = Path(__file__).parent / 'test_dicts_to_file_onderdeel_AllCasesTestClass.csv'
        csv_file_path_3 = Path(__file__).parent / 'test_dicts_to_file_onderdeel_AnotherTestClass.csv'
        geojson_file_path = Path(__file__).parent / 'test_dicts_to_file.geojson'

        OtlmowConverter.to_file(subject=orig_list_of_dicts, file_path=excel_file_path, model_directory=model_directory_path)
        from_excel_objects = OtlmowConverter.from_file_to_objects(excel_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_excel_objects)

        OtlmowConverter.to_file(subject=orig_list_of_dicts, file_path=json_file_path, model_directory=model_directory_path)
        from_json_objects = OtlmowConverter.from_file_to_objects(json_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_json_objects)

        OtlmowConverter.to_file(subject=orig_list_of_dicts, file_path=csv_file_path, model_directory=model_directory_path)
        from_csv_objects_2 = OtlmowConverter.from_file_to_objects(csv_file_path_2, model_directory=model_directory_path)
        from_csv_objects_3 = OtlmowConverter.from_file_to_objects(csv_file_path_3, model_directory=model_directory_path)
        combined_list = list(from_csv_objects_2) + list(from_csv_objects_3)
        assert orig_list_of_objects == combined_list

        OtlmowConverter.to_file(subject=orig_list_of_dicts, file_path=geojson_file_path,
                                model_directory=model_directory_path)
        from_geojson_objects = OtlmowConverter.from_file_to_objects(geojson_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_geojson_objects)

        excel_file_path.unlink()
        json_file_path.unlink()
        csv_file_path_2.unlink()
        csv_file_path_3.unlink()
        geojson_file_path.unlink()


def test_file_to_objects():
    with pytest.warns(NonStandardAttributeWarning):
    # sourcery skip: extract-duplicate-method
        excel_file_path = Path(__file__).parent / 'test_file_to_objects.xlsx'
        json_file_path = Path(__file__).parent / 'test_file_to_objects.json'
        csv_file_path = Path(__file__).parent / 'test_file_to_objects.csv'
        csv_file_path_2 = Path(__file__).parent / 'test_file_to_objects_onderdeel_AllCasesTestClass.csv'
        csv_file_path_3 = Path(__file__).parent / 'test_file_to_objects_onderdeel_AnotherTestClass.csv'
        geojson_file_path = Path(__file__).parent / 'test_file_to_objects.geojson'

        orig_list_of_objects = return_test_objects()

        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=csv_file_path)
        from_csv_objects_2 = to_objects(csv_file_path_2, model_directory=model_directory_path)
        from_csv_objects_3 = to_objects(csv_file_path_3, model_directory=model_directory_path)
        combined_list = list(from_csv_objects_2) + list(from_csv_objects_3)
        assert orig_list_of_objects == combined_list

        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=excel_file_path)
        from_excel_objects = to_objects(excel_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_excel_objects)

        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=json_file_path)
        from_json_objects = to_objects(json_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_json_objects)

        OtlmowConverter.from_objects_to_file(sequence_of_objects=orig_list_of_objects, file_path=geojson_file_path)
        from_geojson_objects = to_objects(geojson_file_path, model_directory=model_directory_path)
        assert orig_list_of_objects == list(from_geojson_objects)

        excel_file_path.unlink()
        json_file_path.unlink()
        csv_file_path_2.unlink()
        csv_file_path_3.unlink()
        geojson_file_path.unlink()


def test_objects_to_objects():
    orig_list_of_objects = return_test_objects()
    new_list_of_objects = to_objects(orig_list_of_objects, model_directory=model_directory_path)
    assert orig_list_of_objects == list(new_list_of_objects)


def test_dicts_to_objects():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        sequence_of_dicts = [o.to_dict() for o in orig_list_of_objects]
        new_list_of_objects = to_objects(sequence_of_dicts, model_directory=model_directory_path)
        assert orig_list_of_objects == list(new_list_of_objects)


def test_dotnotation_dicts_to_objects():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        sequence_of_ddicts = [DotnotationDictConverter.to_dict(o) for o in orig_list_of_objects]
        new_list_of_objects = to_objects(sequence_of_ddicts, model_directory=model_directory_path)
        assert orig_list_of_objects == list(new_list_of_objects)


def test_dataframe_to_objects():
    with pytest.warns(NonStandardAttributeWarning):
        orig_list_of_objects = return_test_objects()
        df = PandasConverter.convert_objects_to_single_dataframe(list_of_objects=orig_list_of_objects)
        new_list_of_objects = to_objects(df, model_directory=model_directory_path)
        assert orig_list_of_objects == list(new_list_of_objects)
