import unittest
from datetime import date, datetime, time
from pathlib import Path

from otlmow_model.Classes.Onderdeel.Verkeersregelaar import Verkeersregelaar

from otlmow_converter.FileFormats.CsvImporter import CsvImporter
from otlmow_converter.OtlmowConverter import OtlmowConverter


class CsvImporterTests(unittest.TestCase):
    def test_init_importer_only_load_with_settings(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        otl_facility = OtlmowConverter(settings_path=settings_file_location)

        with self.subTest('load with correct settings'):
            importer = CsvImporter(settings=otl_facility.settings)
            self.assertIsNotNone(importer)

        with self.subTest('load without settings'):
            with self.assertRaises(ValueError):
                CsvImporter(settings=None)

        with self.subTest('load with incorrect settings (no file_formats)'):
            with self.assertRaises(ValueError):
                CsvImporter(settings={"auth_options": [{}]})

        with self.subTest('load with incorrect settings (file_formats but no csv)'):
            with self.assertRaises(ValueError):
                CsvImporter(settings={"file_formats": [{}]})

    def test_load_test_file_multiple_types(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        file_location = Path(__file__).parent / 'export_multiple_types.csv'
        otl_facility = OtlmowConverter(settings_path=settings_file_location)
        objects = otl_facility.create_assets_from_file(file_location)

        self.assertEqual(15, len(objects))

    def test_load_test_file(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        otl_facility = OtlmowConverter(settings_path=settings_file_location)
        importer = CsvImporter(settings=otl_facility.settings)
        file_location = Path(__file__).parent / 'test_file_VR.csv'
        importer.import_file(file_location)
        self.assertEqual(187, len(importer.data))
        self.assertEqual(27, len(importer.headers))

    def test_create_objects_from_data(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        otl_facility = OtlmowConverter(settings_path=settings_file_location)
        importer = CsvImporter(settings=otl_facility.settings)
        datastring = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Verkeersregelaar;1433df2f-5dc8-467b-94f4-efceb4581c68-b25kZXJkZWVsI1ZlcmtlZXJzcmVnZWxhYXI;AWV;;;;centraal|klok;2021-06-09;;;;802C5;MACQ;true;aansluit_802C5.pdf;application-pdf;/eminfra/core/api/otl/assets/1433df2f-5dc8-467b-94f4-efceb4581c68-b25kZXJkZWVsI1ZlcmtlZXJzcmVnZWxhYXI/documenten/ed288304-0f02-479f-af74-28d2fc55e5fe;;;civa-2020;;ccol;;;;;;;240.0;in-gebruik;42;2020-10-09;V016027v06;POINT Z (146955.19 181631.1 59.17)'
        datastring2 = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Verkeersregelaar;176c849f-f386-4a07-9493-cb5100ba9830-b25kZXJkZWVsI1ZlcmtlZXJzcmVnZWxhYXI;AWV;;;;klok;2022-02-19;;;;605C7|605C7;MACQ | TRAFIROAD;true;V15.816_v11_605C7.pdf;application-pdf;https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Verkeersregelaar.kabelaansluitschema;yunex;sx;;;StrideTT;type-1;;;V15.816_v11_605C7.pdf;application-pdf;https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Verkeersregelaar.technischeDocumentatie;240.0;in-gebruik;42;2021-09-16;V015816v11;POINT Z (145670.97 164665.43 21)'
        importer.data = [datastring.split(';'), datastring2.split(';')]
        headerstring = 'typeURI;assetId.identificator;assetId.toegekendDoor;bron.typeURI;bronAssetId.identificator;bronAssetId.toegekendDoor;coordinatiewijze[];datumOprichtingObject;doel.typeURI;doelAssetId.identificator;doelAssetId.toegekendDoor;externeReferentie[].externReferentienummer;externeReferentie[].externePartij;isActief;kabelaansluitschema.bestandsnaam;kabelaansluitschema.mimeType;kabelaansluitschema.uri;merk;modelnaam;naam;notitie;programmeertool;regelaartype;rol;standaardBestekPostNummer[];technischeDocumentatie.bestandsnaam;technischeDocumentatie.mimeType;technischeDocumentatie.uri;theoretischeLevensduur;toestand;voltageLampen;vplanDatum;vplanNummer;geometry'
        importer.headers = headerstring.split(';')

        self.assertEqual(2, len(importer.data))
        self.assertEqual(34, len(importer.headers))

        objects = importer.create_objects_from_data()

        self.assertTrue(isinstance(objects, list))
        self.assertEqual(2, len(objects))
        self.assertTrue(isinstance(objects[0], Verkeersregelaar))
        self.assertEqual('centraal', objects[0].coordinatiewijze[0])
        self.assertEqual('klok', objects[0].coordinatiewijze[1])
        self.assertEqual('605C7', objects[1].externeReferentie[0].externReferentienummer)
        self.assertEqual('605C7', objects[1].externeReferentie[1].externReferentienummer)
        self.assertEqual('MACQ ', objects[1].externeReferentie[0].externePartij)
        self.assertEqual(' TRAFIROAD', objects[1].externeReferentie[1].externePartij)

    def test_load_test_unnested_attributes(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = CsvImporter(settings=converter.settings)
        file_location = Path(__file__).parent / 'Testfiles' / 'unnested_attributes.csv'
        objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
        self.assertEqual(1, len(objects))
        self.assertEqual(17, len(importer.headers))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)
        self.assertEqual(False, instance.testBooleanField)
        self.assertEqual(date(2019, 9, 20), instance.testDateField)
        self.assertEqual(datetime(2001, 12, 15, 22, 22, 15), instance.testDateTimeField)
        self.assertEqual(79.07, instance.testDecimalField)
        self.assertListEqual([10.0, 20.0], instance.testDecimalFieldMetKard)
        self.assertEqual('string1', instance.testEenvoudigType.waarde)
        self.assertEqual('string1', instance.testEenvoudigTypeMetKard[0].waarde)
        self.assertEqual('string2', instance.testEenvoudigTypeMetKard[1].waarde)
        self.assertEqual(-55, instance.testIntegerField)
        self.assertListEqual([76, 2], instance.testIntegerFieldMetKard)
        self.assertEqual('waarde-4', instance.testKeuzelijst)
        self.assertListEqual(['waarde-4', 'waarde-3'], instance.testKeuzelijstMetKard)
        self.assertEqual(98.21, instance.testKwantWrd.waarde)
        self.assertEqual(10.0, instance.testKwantWrdMetKard[0].waarde)
        self.assertEqual(20.0, instance.testKwantWrdMetKard[1].waarde)
        self.assertEqual('oFfeDLp', instance.testStringField)
        self.assertEqual('string1', instance.testStringFieldMetKard[0])
        self.assertEqual('string2', instance.testStringFieldMetKard[1])
        self.assertEqual(time(11, 5, 26), instance.testTimeField)

    def test_load_test_ested_attributes_1_level(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = CsvImporter(settings=converter.settings)
        file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_1.csv'

        with self.assertLogs(level='WARNING') as log:
            objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
            self.assertEqual(len(log.output), 2)

        self.assertEqual(1, len(objects))
        self.assertEqual(15, len(importer.headers))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)
        self.assertEqual('YKAzZDhhdTXqkD', instance.assetId.identificator)
        self.assertEqual('DGcQxwCGiBlR', instance.assetId.toegekendDoor)
        self.assertEqual(True, instance.testComplexType.testBooleanField)
        self.assertEqual(65.14, instance.testComplexType.testKwantWrd.waarde)
        self.assertEqual(10.0, instance.testComplexType.testKwantWrdMetKard[0].waarde)
        self.assertEqual(20.0, instance.testComplexType.testKwantWrdMetKard[1].waarde)
        self.assertEqual('KmCtMXM', instance.testComplexType.testStringField)
        self.assertEqual('string1', instance.testComplexType.testStringFieldMetKard[0])
        self.assertEqual('string2', instance.testComplexType.testStringFieldMetKard[1])
        self.assertEqual(True, instance.testComplexTypeMetKard[0].testBooleanField)
        self.assertEqual(False, instance.testComplexTypeMetKard[1].testBooleanField)
        self.assertEqual(10.0, instance.testComplexTypeMetKard[0].testKwantWrd.waarde)
        self.assertEqual(20.0, instance.testComplexTypeMetKard[1].testKwantWrd.waarde)
        self.assertEqual(None, instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde)
        self.assertEqual(None, instance.testComplexTypeMetKard[0].testKwantWrdMetKard[0].waarde)
        self.assertEqual('string1', instance.testComplexTypeMetKard[0].testStringField)
        self.assertEqual('string2', instance.testComplexTypeMetKard[1].testStringField)
        self.assertEqual('RWKofW', instance.testUnionType.unionString)
        self.assertEqual(None, instance.testUnionType.unionKwantWrd.waarde)
        self.assertEqual(10.0, instance.testUnionTypeMetKard[0].unionKwantWrd.waarde)
        self.assertEqual(20.0, instance.testUnionTypeMetKard[1].unionKwantWrd.waarde)

    def test_load_test_ested_attributes_2_levels(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        converter = OtlmowConverter(settings_path=settings_file_location)
        importer = CsvImporter(settings=converter.settings)
        file_location = Path(__file__).parent / 'Testfiles' / 'nested_attributes_2.csv'

        with self.assertLogs(level='WARNING') as log:
            objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
            self.assertEqual(len(log.output), 2)

        self.assertEqual(1, len(objects))
        self.assertEqual(9, len(importer.headers))

        instance = objects[0]
        self.assertEqual('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', instance.typeURI)
        self.assertEqual(76.8, instance.testComplexType.testComplexType2.testKwantWrd.waarde)
        self.assertEqual('GZBzgRhOrQvfZaN', instance.testComplexType.testComplexType2.testStringField)
        self.assertEqual(10.0, instance.testComplexType.testComplexType2MetKard[0].testKwantWrd.waarde)
        self.assertEqual(20.0, instance.testComplexType.testComplexType2MetKard[1].testKwantWrd.waarde)
        self.assertEqual('string1', instance.testComplexType.testComplexType2MetKard[0].testStringField)
        self.assertEqual('string2', instance.testComplexType.testComplexType2MetKard[1].testStringField)
        self.assertEqual(10.0, instance.testComplexTypeMetKard[0].testComplexType2.testKwantWrd.waarde)
        self.assertEqual(20.0, instance.testComplexTypeMetKard[1].testComplexType2.testKwantWrd.waarde)
        self.assertEqual('string1', instance.testComplexTypeMetKard[0].testComplexType2.testStringField)
        self.assertEqual('string2', instance.testComplexTypeMetKard[1].testComplexType2.testStringField)
        self.assertEqual(None, instance.testComplexTypeMetKard[0].testComplexType2MetKard[0].testKwantWrd.waarde)
        self.assertEqual(None, instance.testComplexTypeMetKard[0].testComplexType2MetKard[0].testStringField)

    def test_load_test_subset_file(self):
        settings_file_location = Path(__file__).parent.parent / 'settings_OTLMOW.json'
        otl_facility = OtlmowConverter(settings_path=settings_file_location)
        importer = CsvImporter(settings=otl_facility.settings)
        file_location = Path(__file__).parent / 'template_file_text_onderdeel_AllCasesTestClass.csv'

        with self.assertLogs(level='WARNING') as log:
            objects = importer.import_file(filepath=file_location, class_directory='UnitTests.TestClasses.Classes')
            self.assertEqual(len(log.output), 4)

        self.assertEqual(1, len(objects))
        self.assertEqual(39, len(importer.headers))
