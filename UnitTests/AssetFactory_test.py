import datetime
from pathlib import Path

from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestModel.OtlmowModel.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.AssetFactory import AssetFactory


def test_create_otl_object_using_other_otl_object_as_template_using_attribute_list():
    another_test_class = AnotherTestClass()
    another_test_class.notitie = 'notitie'
    another_test_class.datumOprichtingObject = datetime.date(2020, 1, 1)

    attribute_list = {a.naam for a in another_test_class}
    attribute_list.remove('deprecatedString')

    result_asset = AssetFactory.create_otl_object_using_other_otl_object_as_template(
        orig_otl_object=another_test_class, typeURI=AllCasesTestClass.typeURI, fields_to_copy=attribute_list,
        model_directory=Path(__file__).parent / 'TestModel')

    input_dict = another_test_class.create_dict_from_asset()
    input_type_uri = input_dict.pop('typeURI')

    result_dict = result_asset.create_dict_from_asset()
    result_type_uri = result_dict.pop('typeURI')

    assert result_type_uri == AllCasesTestClass.typeURI
    assert input_type_uri == AnotherTestClass.typeURI
    assert result_dict == input_dict
