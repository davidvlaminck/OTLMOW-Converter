from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from otlmow_converter.FileFormats.DictDecoder import get_attribute_by_name, get_attribute_by_uri


def test_get_attribute_by_name_simple():
    instance = AllCasesTestClass()
    attr = get_attribute_by_name(instance, key='toestand', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMToestand.toestand'


def test_get_attribute_by_name_complex():
    instance = AllCasesTestClass()
    attr = get_attribute_by_name(instance, key='assetId', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.assetId'


def test_get_attribute_by_name_union():
    instance = AllCasesTestClass()
    attr = get_attribute_by_name(instance, key='testUnionType', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testUnionType'


def test_get_attribute_by_name_kwant_wrd_shortcut_True():
    instance = AllCasesTestClass()
    instance.testKwantWrd.waarde = 1.2
    attr = get_attribute_by_name(instance, key='testKwantWrd', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde'


def test_get_attribute_by_name_kwant_wrd_shortcut_False():
    instance = AllCasesTestClass()
    instance.testKwantWrd.waarde = 1.2
    attr = get_attribute_by_name(instance, key='testKwantWrd', waarde_shortcut=False)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKwantWrd'


def test_get_attribute_by_name_dte_kard_shortcut_True():
    instance = AllCasesTestClass()
    instance.testEenvoudigTypeMetKard[0].waarde = '1'
    attr = get_attribute_by_name(instance, key='testEenvoudigTypeMetKard', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DteTestEenvoudigType.waarde'


def test_get_attribute_by_name_dte_kard_shortcut_False():
    instance = AllCasesTestClass()
    instance.testEenvoudigTypeMetKard[0].waarde = '1'
    attr = get_attribute_by_name(instance, key='testEenvoudigTypeMetKard', waarde_shortcut=False)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testEenvoudigTypeMetKard'


def test_get_attribute_by_name_complex_kard():
    instance = AllCasesTestClass()
    instance.testComplexTypeMetKard[0].testStringField = '1'
    attr = get_attribute_by_name(instance, key='testComplexTypeMetKard', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexTypeMetKard'


def test_get_attribute_by_uri_simple():
    instance = AllCasesTestClass()
    attr = get_attribute_by_uri(instance, key='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMToestand.toestand', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMToestand.toestand'


def test_get_attribute_by_uri_complex():
    instance = AllCasesTestClass()
    attr = get_attribute_by_uri(instance, key='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.assetId', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.assetId'


def test_get_attribute_by_uri_union():
    instance = AllCasesTestClass()
    attr = get_attribute_by_uri(instance, key='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testUnionType', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testUnionType'


def test_get_attribute_by_uri_kwant_wrd_shortcut_True():
    instance = AllCasesTestClass()
    instance.testKwantWrd.waarde = 1.2
    attr = get_attribute_by_uri(instance, key='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKwantWrd', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde'


def test_get_attribute_by_uri_kwant_wrd_shortcut_False():
    instance = AllCasesTestClass()
    instance.testKwantWrd.waarde = 1.2
    attr = get_attribute_by_uri(instance, key='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKwantWrd', waarde_shortcut=False)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKwantWrd'


def test_get_attribute_by_uri_dte_kard_shortcut_True():
    instance = AllCasesTestClass()
    instance.testEenvoudigTypeMetKard[0].waarde = '1'
    attr = get_attribute_by_uri(instance, key='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testEenvoudigTypeMetKard', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DteTestEenvoudigType.waarde'


def test_get_attribute_by_uri_dte_kard_shortcut_False():
    instance = AllCasesTestClass()
    instance.testEenvoudigTypeMetKard[0].waarde = '1'
    attr = get_attribute_by_uri(instance, key='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testEenvoudigTypeMetKard', waarde_shortcut=False)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testEenvoudigTypeMetKard'


def test_get_attribute_by_uri_complex_kard():
    instance = AllCasesTestClass()
    instance.testComplexTypeMetKard[0].testStringField = '1'
    attr = get_attribute_by_uri(instance, key='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexTypeMetKard', waarde_shortcut=True)
    assert attr is not None
    assert attr.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexTypeMetKard'