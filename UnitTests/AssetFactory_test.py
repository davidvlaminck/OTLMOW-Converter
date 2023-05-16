from otlmow_model.Classes.Onderdeel.Exoten import Exoten
from otlmow_model.Classes.Onderdeel.InvasieveExoten import InvasieveExoten

from otlmow_converter.AssetFactory import AssetFactory


def test_create_otl_object_using_other_otl_object_as_template_using_attribute_list():
    exoten = Exoten()
    exoten.heeftObstakels = True
    exoten.breedte.waarde = 2.0

    attribute_list = [a.naam for a in InvasieveExoten()]
    result = AssetFactory.create_otl_object_using_other_otl_object_as_template(
        orig_otl_object=exoten, typeURI=InvasieveExoten.typeURI, fields_to_copy=attribute_list)

    input_dict = exoten.create_dict_from_asset()
    input_type_uri = input_dict.pop('typeURI')

    result_dict = result.create_dict_from_asset()
    result_type_uri = result_dict.pop('typeURI')

    assert result_type_uri == InvasieveExoten.typeURI
    assert input_type_uri == Exoten.typeURI
    assert result_dict == input_dict
