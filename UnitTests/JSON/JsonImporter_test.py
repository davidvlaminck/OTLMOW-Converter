import os
from datetime import date, datetime, time
from pathlib import Path

import pytest

from otlmow_converter.FileFormats.JsonImporter import JsonImporter

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

model_directory_path = Path(__file__).parent.parent / 'TestModel'


def test_load_test_unnested_attributes(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes.json'

    objects = JsonImporter.to_objects(filepath=file_location, model_directory=model_directory_path)
    assert len(recwarn.list) == 0

    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == '0000-0000'
    assert not instance.testBooleanField
    assert instance.testDateField == date(2019, 9, 20)
    assert instance.testDateTimeField == datetime(2001, 12, 15, 22, 22, 15, 123456)
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
    assert instance.testTimeField == time(11, 5, 26)
    assert instance.geometry == 'POINT Z (200000 200000 0)'


@pytest.mark.asyncio(loop_scope="function")
async def test_load_test_unnested_attributes_async(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes.json'

    objects = await JsonImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)
    assert len(recwarn.list) == 0

    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == '0000-0000'
    assert not instance.testBooleanField
    assert instance.testDateField == date(2019, 9, 20)
    assert instance.testDateTimeField == datetime(2001, 12, 15, 22, 22, 15, 123456)
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
    assert instance.testTimeField == time(11, 5, 26)
    assert instance.geometry == 'POINT Z (200000 200000 0)'



@pytest.mark.asyncio(loop_scope="function")
async def test_load_test_nested_attributes_1_level_async(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_1.json'

    objects = await JsonImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)
    assert len(recwarn.list) == 0

    assert len(objects) == 1

    instance = objects[0]
    assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
    assert instance.assetId.identificator == '0000'
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


@pytest.mark.asyncio(loop_scope="function")
async def test_load_test_nested_attributes_2_levels(recwarn):
    file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_2.json'

    objects = await JsonImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)
    assert len(recwarn.list) == 0

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


@pytest.mark.asyncio(loop_scope="function")
async def test_load_test_non_conform(recwarn, subtests):
    file_location = Path(__file__).parent / 'Testfiles' / 'non_conform_attributes.json'

    with subtests.test(msg="default behaviour"):
        recwarn.clear()
        objects = await JsonImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path)
        assert len(recwarn.list) == 1

        assert len(objects) == 1

        instance = objects[0]
        assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
        assert instance.assetId.identificator == '0000-0000'
        assert not instance.testBooleanField
        assert instance.non_conform_attribute == 'non_conform_value'

    with subtests.test(msg='non conform not allowed'):
        with pytest.raises(ValueError):
            await JsonImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path,
                                    allow_non_otl_conform_attributes=False)

    with subtests.test(msg="allowed, no warnings"):
        recwarn.clear()
        objects = await JsonImporter.to_objects_async(filepath=file_location, model_directory=model_directory_path,
                                          warn_for_non_otl_conform_attributes=False)
        assert len(recwarn.list) == 0

        assert len(objects) == 1

        instance = objects[0]
        assert instance.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'
        assert instance.assetId.identificator == '0000-0000'
        assert not instance.testBooleanField
        assert instance.non_conform_attribute == 'non_conform_value'
