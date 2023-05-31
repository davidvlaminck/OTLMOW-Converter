from datetime import date, datetime, time

import pytest
from otlmow_model.Classes.Installatie.Wegberm import Wegberm
from otlmow_model.Classes.Onderdeel.ExterneDetectie import ExterneDetectie
from otlmow_model.Classes.Onderdeel.HeeftBetrokkene import HeeftBetrokkene
from otlmow_model.Classes.Onderdeel.Netwerkpoort import Netwerkpoort
from otlmow_model.Classes.Onderdeel.Verkeersregelaar import Verkeersregelaar

from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.JsonDecoder import JsonDecoder

# TODO: refactor to only use AllCasesTestClass
# TODO: refactor to reduce warnings
jsonDataCase1 = """[{
"assetId": {
  "identificator": "000a35d5-c4a5-4a36-8620-62c99e053ba0-b25kZXJkZWVsI05ldHdlcmtwb29ydA",
  "toegekendDoor": "AWV"
},
"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Netwerkpoort",
"isActief": true,
"naam": "Poort_2625",
"toestand": "in-ontwerp",
"beschrijvingFabrikant": "test",
"nNILANCapaciteit": 155
}]"""
jsonDataCase2 = """[{
"assetId": {
  "identificator": "4be83a8f-ab97-44c7-8dc6-1666c8dfb68e-b25kZXJkZWVsI0hlZWZ0QmV0cm9ra2VuZQ"
},
"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBetrokkene",
"bronAssetId": {
  "identificator": "000a35d5-c4a5-4a36-8620-62c99e053ba0-b25kZXJkZWVsI05ldHdlcmtwb29ydA"
},
"doelAssetId": {
  "identificator": "5434ffca-8bdc-445a-a4ba-b395c87dec30-cHVybDpBZ2VudA"
},
"bron": {
  "typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Netwerkpoort"
},
"doel": {
  "typeURI": "http://purl.org/dc/terms/Agent"
},
"rol": "toezichter",
"specifiekeContactinfo": [],
"isActief": true
}]"""
jsonDataCase3 = """[{
"assetId" : {
"identificator" : "842cc8b2-3117-4757-a11a-1f0344b159e4-aW5zdGFsbGF0aWUjV2VnYmVybQ",
"toegekendDoor" : "AWV"
},
"typeURI" : "https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Wegberm",
"niveau" : 1.1,
"breedte" : 2,
"toestand" : "in-ontwerp",
"oppervlakte" : 50.2,
"isActief" : true
}]"""
jsonDataCase4 = """[{
"assetId" : {
"identificator" : "f184a415-10c3-465a-85d0-5e3495e7c57f-b25kZXJkZWVsI1ZlcmtlZXJzcmVnZWxhYXI",
"toegekendDoor" : "AWV"
},
"typeURI" : "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Verkeersregelaar",
"vplanNummer" : "V015254v11",
"coordinatiewijze" : [ "centraal", "pulsen" ],
"toestand" : "in-gebruik",
"kabelaansluitschema" : {
"uri" : "/eminfra/core/api/otl/assets/f184a415-10c3-465a-85d0-5e3495e7c57f-b25kZXJkZWVsI1ZlcmtlZXJzcmVnZWxhYXI/documenten/e4457b0f-5e08-4157-a01a-b955e6a4186f",
"bestandsnaam" : "00_input.json"
},
"isActief" : true,
"voltageLampen" : "230",
"vplanDatum" : "2020-04-22",
"datumOprichtingObject" : "2020-03-14",
"technischeDocumentatie" : {
"uri" : "/eminfra/core/api/otl/assets/f184a415-10c3-465a-85d0-5e3495e7c57f-b25kZXJkZWVsI1ZlcmtlZXJzcmVnZWxhYXI/documenten/3771787b-889d-4c81-8cfa-99718f81db4a",
"bestandsnaam" : "Cooper.jpg"
},
"programmeertool" : "fwispbnxlo",
"externeReferentie" : [ {    "externePartij" : "bij externe partij 2",    "externReferentienummer" : "externe referentie 2"  }, {    "externePartij" : "bij externe partij 1",    "externReferentienummer" : "externe referentie 1"  } ],
"regelaartype" : "type-1",
"notitie" : "test 123",
"naam" : "Gevondenproficiat",
"geometry" : "POINT Z (155377.8 211520.7 0)"
}]"""
jsonDataCase5 = """{
"assetId" : {
"identificator" : "ae6c5f35-930d-47a3-b67f-a5ff40c6e0fe-b25kZXJkZWVsI1NsYWdib29ta29sb20",
"toegekendDoor" : "AWV"
},
"typeURI" : "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Slagboomkolom",
"toestand" : "in-gebruik",
"isActief" : true,
"geometry" : "POINT Z (61716.3 209331.2 0)"
}"""
jsonDataCase6 = """[{
"assetId" : {
"identificator" : "7102cbba-4391-4d7c-a2d1-8873eac3eee8-b25kZXJkZWVsI0V4dGVybmVEZXRlY3RpZQ",
"toegekendDoor" : "AWV"
},
"typeURI" : "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#ExterneDetectie",
"isActief" : true,
"contactpersoon" : {
"adres" : [ {
  "gemeente" : "aalter",
  "straatnaam" : "teststraat"
} ],
"voornaam" : "test_voornaam",
"achternaam" : "test_achternaam"
},
"toestand" : "in-ontwerp",
"naam" : "test_ExterneDetectie"
}]"""


def set_up_decoder():
    return JsonDecoder(
        settings={'file_formats': [{"name": "json", "dotnotation": {
            "waarde_shortcut": True,
            "separator": '.',
            'cardinality_indicator': '[]'
        }}]})


def test_invalid_typeURI():
    davie_decoder = set_up_decoder()
    with pytest.raises(ValueError):
        davie_decoder.decode_json_string('[{"typeURI": "https://invalid.uri.com"}]',
                                         classes_directory='UnitTests.TestClasses.Classes')


def test_decode_invalid_attribute():
    davie_decoder = set_up_decoder()
    with pytest.raises(AttributeError):
        davie_decoder.decode_json_string(
            '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", "invalid_attribute": "some value"}]',
            classes_directory='UnitTests.TestClasses.Classes')


def test_decode_empty_value():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", "toestand": ""}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert AllCasesTestClass.typeURI == lijst_objecten[0].typeURI
    assert isinstance(lijst_objecten[0], AllCasesTestClass)
    assert lijst_objecten[0].toestand is None


def test_decode_Stringfield():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", "testStringField": "string"}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testStringField == 'string'


def test_decode_StringfieldMetKard():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", '
        '"testStringFieldMetKard": ["string", "string2"]}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testStringFieldMetKard == ["string", "string2"]


def test_decode_DecimalNumberField():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", "testDecimalField": 2.5}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testDecimalField == 2.5


def test_decode_TimeField():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", '
        '"testTimeField": "22:22:22"}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testTimeField == time(hour=22, minute=22, second=22)


def test_decode_DateTimeField():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", '
        '"testDateTimeField": "2022-2-2 22:22:22"}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testDateTimeField == datetime(year=2022, month=2, day=2, hour=22, minute=22, second=22)


def test_decode_DateField():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", "testDateField": "2022-2-2"}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testDateField == date(year=2022, month=2, day=2)


def test_decode_testKwantWrd():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", "testKwantWrd": 3.5}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testKwantWrd.waarde == 3.5


def test_decode_testKwantWrd_waarde_shortcut_false():
    davie_decoder = set_up_decoder()
    davie_decoder.settings['dotnotation']['waarde_shortcut_applicable'] = False
    davie_decoder = JsonDecoder(
        settings={'file_formats': [{"name": "json", "dotnotation": {"waarde_shortcut": False}}]})
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", '
        '"testKwantWrd": { "waarde": 3.5}}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testKwantWrd.waarde == 3.5


def test_decode_testKwantWrdMetKard():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", '
        '"testKwantWrdMetKard": [4.5, 6.5]}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testKwantWrdMetKard[0].waarde == 4.5
    assert lijst_objecten[0].testKwantWrdMetKard[1].waarde == 6.5


def test_decode_UnionType():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", '
        '"testUnionType" : {"unionString": "string"}}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testUnionType.unionString == 'string'


def test_decode_ComplexType():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", '
        '"testComplexType" : {"testStringField": "string"}}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testComplexType.testStringField == 'string'


def test_decode_ComplexTypeMetKard():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", '
        '"testComplexTypeMetKard" : [{"testStringField": "string"}, {"testBooleanField": true}]}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testComplexTypeMetKard[0].testStringField == 'string'
    assert lijst_objecten[0].testComplexTypeMetKard[1].testBooleanField


def test_decode_ComplexType2():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(
        '[{"typeURI": "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass", '
        '"testComplexType" : {"testComplexType2" : {"testStringField": "string"}}}]',
        classes_directory='UnitTests.TestClasses.Classes')
    assert lijst_objecten[0].testComplexType.testComplexType2.testStringField == 'string'


def test_decode_Davie_json_case_1_and_assert_fields(subtests):
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(jsonDataCase1)
    assert len(lijst_objecten) == 1
    assert isinstance(lijst_objecten[0], Netwerkpoort)

    with subtests.test(msg='Assert IntField'):
        assert lijst_objecten[0].nNILANCapaciteit == 155

    with subtests.test(msg='Assert StringField'):
        assert lijst_objecten[0].naam == 'Poort_2625'

    with subtests.test(msg='Assert KeuzelijstField'):
        assert lijst_objecten[0].toestand == 'in-ontwerp'

    with subtests.test(msg='Assert ComplexField'):
        assert lijst_objecten[0].assetId.identificator == '000a35d5-c4a5-4a36-8620-62c99e053ba0-b25kZXJkZWVsI05ldHdlcmtwb29ydA'
        assert lijst_objecten[0].assetId.toegekendDoor == 'AWV'


def test_decode_Davie_json_case_2_and_assert_fields():
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(jsonDataCase2)
    assert len(lijst_objecten) == 1
    assert isinstance(lijst_objecten[0], HeeftBetrokkene)

    assert lijst_objecten[0].assetId.identificator == '4be83a8f-ab97-44c7-8dc6-1666c8dfb68e-b25kZXJkZWVsI0hlZWZ0QmV0cm9ra2VuZQ'
    assert lijst_objecten[0].bronAssetId.identificator == '000a35d5-c4a5-4a36-8620-62c99e053ba0-b25kZXJkZWVsI05ldHdlcmtwb29ydA'
    assert lijst_objecten[0].doelAssetId.identificator == '5434ffca-8bdc-445a-a4ba-b395c87dec30-cHVybDpBZ2VudA'
    assert lijst_objecten[0].rol == 'toezichter'
    assert lijst_objecten[0].isActief


def test_decode_Davie_json_case_3_and_assert_fields(subtests):
    davie_decoder = set_up_decoder()
    lijstObjecten = davie_decoder.decode_json_string(jsonDataCase3)
    assert len(lijstObjecten) == 1
    assert isinstance(lijstObjecten[0], Wegberm)

    with subtests.test(msg='Assert DecimalFloatField'):
        assert lijstObjecten[0].niveau == 1.1

    with subtests.test(msg='Assert KwantWrdInMeter'):
        assert lijstObjecten[0].breedte.waarde == 2.0


def test_decode_Davie_json_case_4_and_assert_fields(subtests):
    davie_decoder = set_up_decoder()
    lijst_objecten = davie_decoder.decode_json_string(jsonDataCase4)
    assert len(lijst_objecten) == 1
    assert isinstance(lijst_objecten[0], Verkeersregelaar)

    with subtests.test(msg='Assert KardinaliteitField met KeuzelijstField'):
        assert isinstance(lijst_objecten[0].coordinatiewijze, list)
        assert lijst_objecten[0].coordinatiewijze[0] == 'centraal'
        assert lijst_objecten[0].coordinatiewijze[1] == 'pulsen'

    with subtests.test(msg='Assert KardinaliteitField met ComplexField'):
        assert isinstance(lijst_objecten[0].externeReferentie, list)
        assert lijst_objecten[0].externeReferentie[0].externePartij == 'bij externe partij 2'
        assert lijst_objecten[0].externeReferentie[0].externReferentienummer == 'externe referentie 2'
        assert lijst_objecten[0].externeReferentie[1].externePartij == 'bij externe partij 1'
        assert lijst_objecten[0].externeReferentie[1].externReferentienummer == 'externe referentie 1'


def test_decode_Davie_json_case_6_and_assert_fields_kard_complex_in_complex():
    davie_decoder = set_up_decoder()
    lijstObjecten = davie_decoder.decode_json_string(jsonDataCase6)
    assert len(lijstObjecten) == 1
    assert isinstance(lijstObjecten[0], ExterneDetectie)
    assert lijstObjecten[0].contactpersoon.voornaam == 'test_voornaam'
    assert lijstObjecten[0].contactpersoon.achternaam == 'test_achternaam'

    assert lijstObjecten[0].contactpersoon.adres[0].gemeente == 'aalter'
    assert lijstObjecten[0].contactpersoon.adres[0].straatnaam == 'teststraat'
