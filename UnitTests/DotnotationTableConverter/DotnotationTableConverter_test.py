from pathlib import Path
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import dynamic_create_instance_from_uri
from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter

model_directory_path = Path(__file__).parent.parent / 'TestModel'

DotnotationTableConverter()

def test_get_tables_per_type_from_data(subtests):
    """Test the function get_tables_per_type_from_data conversion
    """
    with subtests.test(msg='Test OTL Asset convertion to DotnotationTable'):
        camera_instance = dynamic_create_instance_from_uri('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Camera')
        camera_instance.fill_with_dummy_data()
        sequence_of_objects = [camera_instance]

        test_dictionary = DotnotationTableConverter.get_tables_per_type_from_data(sequence_of_objects=sequence_of_objects)

        assert test_dictionary['onderdeel#Camera'][1]['typeURI'] == camera_instance.typeURI

    with subtests.test(msg='Test OTL Relation convertion to DotnotationTable'):
        relation_instance = dynamic_create_instance_from_uri('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging')
        relation_instance.fill_with_dummy_data()
        sequence_of_objects = [relation_instance]

        test_dictionary = DotnotationTableConverter.get_tables_per_type_from_data(sequence_of_objects=sequence_of_objects)

        assert test_dictionary['onderdeel#Bevestiging'][1]['typeURI'] == relation_instance.typeURI

    with subtests.test(msg='Test OTL Agent convertion to DotnotationTable'):
        agent_instance = dynamic_create_instance_from_uri('http://purl.org/dc/terms/Agent')
        agent_instance.naam = 'dummyNaam'
        sequence_of_objects = [agent_instance]

        test_dictionary = DotnotationTableConverter.get_tables_per_type_from_data(sequence_of_objects=sequence_of_objects)

        assert test_dictionary['Agent'][1]['typeURI'] == agent_instance.typeURI
        assert test_dictionary['Agent'][1]['naam'] == agent_instance.naam
