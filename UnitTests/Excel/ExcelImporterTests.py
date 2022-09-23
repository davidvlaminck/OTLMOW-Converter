import os
import unittest
from pathlib import Path

import pandas
from otlmow_model.Classes.Onderdeel.Verkeersregelaar import Verkeersregelaar

from otlmow_converter.FileFormats.ExcelImporter import ExcelImporter
from otlmow_converter.OtlmowConverter import OtlmowConverter

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class ExcelImporterTests(unittest.TestCase):
    def test_init_importer_only_load_with_settings(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        settings_file_location = f'{base_dir}/../settings_OTLMOW.json'
        otl_facility = OtlmowConverter(logfile='', settings_path=settings_file_location)

        with self.subTest('load with correct settings'):
            importer = ExcelImporter(settings=otl_facility.settings)
            self.assertIsNotNone(importer)

        with self.subTest('load without settings'):
            with self.assertRaises(ValueError):
                ExcelImporter(settings=None)

        with self.subTest('load with incorrect settings (no file_formats)'):
            with self.assertRaises(ValueError):
                ExcelImporter(settings={"auth_options": [{}]})

        with self.subTest('load with incorrect settings (file_formats but no xls)'):
            with self.assertRaises(ValueError):
                ExcelImporter(settings={"file_formats": [{}]})

    def test_load_test_file(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        settings_file_location = f'{base_dir}/../settings_OTLMOW.json'
        otl_facility = OtlmowConverter(logfile='', settings_path=settings_file_location)
        importer = ExcelImporter(settings=otl_facility.settings)
        file_location = os.path.abspath(os.path.join(os.sep, ROOT_DIR, 'test_file_VR.xlsx'))
        importer.import_file(Path(file_location))
        objects = importer.create_objects_from_data()
        self.assertEqual(132, len(objects))
        vrs = list(filter(lambda x: Verkeersregelaar.typeURI in x.typeURI, objects))
        self.assertEqual(1, len(vrs))
        self.assertEqual('externe referentie / 2', vrs[0].externeReferentie[0].externReferentienummer)
        self.assertEqual('externe referentie 1', vrs[0].externeReferentie[1].externReferentienummer)
        self.assertEqual('-', vrs[0].externeReferentie[0].externePartij)
        self.assertEqual('bij externe partij 1', vrs[0].externeReferentie[1].externePartij)

    def test_create_objects_from_data(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        settings_file_location = f'{base_dir}/../settings_OTLMOW.json'
        otl_facility = OtlmowConverter(logfile='', settings_path=settings_file_location)
        importer = ExcelImporter(settings=otl_facility.settings)

        df = pandas.DataFrame(columns='typeURI	assetId.identificator	assetId.toegekendDoor	coordinatiewijze[]	datumOprichtingObject	externeReferentie[].externReferentienummer	externeReferentie[].externePartij	isActief	kabelaansluitschema.bestandsnaam	kabelaansluitschema.uri	naam	notitie	programmeertool	regelaartype	technischeDocumentatie.bestandsnaam	technischeDocumentatie.uri	toestand	voltageLampen	vplanDatum	vplanNummer	geometry'.split('\t'),
                              data=[['https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Verkeersregelaar','f184a415-10c3-465a-85d0-5e3495e7c57f-b25kZXJkZWVsI1ZlcmtlZXJzcmVnZWxhYXI','AWV','centraal|pulsen','2020-03-14','externe referentie / 2|externe referentie 1','-|bij externe partij 1','true','5_zon_maan_aarde.pdf','/eminfra/core/api/otl/assets/f184a415-10c3-465a-85d0-5e3495e7c57f-b25kZXJkZWVsI1ZlcmtlZXJzcmVnZWxhYXI/documenten/182512e8-d527-4f36-b823-cf8b4a0fdea8','Gevonden_demo_OTL','test woppa coach','fwispbnxlo','type-1','Volbeat_1 (19).jpg','/eminfra/core/api/otl/assets/f184a415-10c3-465a-85d0-5e3495e7c57f-b25kZXJkZWVsI1ZlcmtlZXJzcmVnZWxhYXI/documenten/6b6c0872-2305-436d-8255-8675e186716c','in-gebruik','230','2020-04-22','V015254v11','POINT Z (155377.8 211520.7 0)']])
        importer.data = {'Verkeersregelaar': df}

        self.assertEqual(1, len(importer.data.items()))

        objects = importer.create_objects_from_data()

        self.assertTrue(isinstance(objects, list))
        self.assertEqual(1, len(objects))
        self.assertTrue(isinstance(objects[0], Verkeersregelaar))
        self.assertEqual('centraal', objects[0].coordinatiewijze[0])
        self.assertEqual('pulsen', objects[0].coordinatiewijze[1])

