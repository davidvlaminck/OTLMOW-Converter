import unittest
from datetime import date, datetime, time

from otlmow_model.Classes.Onderdeel.Bevestiging import Bevestiging
from rdflib import RDF, URIRef, Literal

from UnitTests.TestClasses.Classes.Onderdeel.AllCasesTestClass import AllCasesTestClass
from UnitTests.TestClasses.Classes.Onderdeel.AnotherTestClass import AnotherTestClass
from otlmow_converter.FileFormats.RDFExporter import RDFExporter
from otlmow_converter.RelationCreator import create_relation


class RDFExporterTests(unittest.TestCase):
    def test_export_relation(self):
        exporter = RDFExporter(dotnotation_settings={'waarde_shortcut_applicable': False})

        instance = AllCasesTestClass()
        instance.assetId.identificator = '0000'

        instance2 = AnotherTestClass()
        instance2.assetId.identificator = '0001'

        relation = create_relation(instance, instance2, relation_type=Bevestiging)

        graph = exporter.create_graph([instance, instance2, relation])
        for s, p, o in graph:
            print(f'{s} {p} {o}')

    def test_export_unnested_attributes(self):
        exporter = RDFExporter(dotnotation_settings={'waarde_shortcut_applicable': False})

        instance = AllCasesTestClass()
        instance.assetId.identificator = '0000'
        instance.testBooleanField = False
        instance.testDecimalField = 79.07
        instance.testIntegerField = -55
        instance.testDateField = date(2019, 9, 20)
        instance.testTimeField = time(11, 5, 26)
        instance.testStringField = 'oFfeDLp'
        instance.testDateTimeField = datetime(2001, 12, 15, 22, 22, 15)

        instance.testKeuzelijst = 'waarde-4'

        instance.testIntegerFieldMetKard = [76, 2]
        instance.testDecimalFieldMetKard = [10.0, 20.0]
        instance.testStringFieldMetKard = ['string1', 'string2']

        instance.testKeuzelijstMetKard = ['waarde-4', 'waarde-3']

        graph = exporter.create_graph([instance])

        subj = graph.value(predicate=RDF.type,
                           object=URIRef('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'),
                           any=False)
        self.assertIsNotNone(subj)

        for expected_value, expected_type, attribute_uri in [
            ('false', 'http://www.w3.org/2001/XMLSchema#boolean', 'testBooleanField'),
            ('79.07', 'http://www.w3.org/2001/XMLSchema#decimal', 'testDecimalField'),
            ('-55', 'http://www.w3.org/2001/XMLSchema#integer', 'testIntegerField'),
            ('2019-09-20', 'http://www.w3.org/2001/XMLSchema#date', 'testDateField'),
            ('11:05:26', 'http://www.w3.org/2001/XMLSchema#time', 'testTimeField'),
            ('2001-12-15T22:22:15', 'http://www.w3.org/2001/XMLSchema#dateTime', 'testDateTimeField'),
            ('oFfeDLp', None, 'testStringField')
        ]:
            attribute_uri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.' + attribute_uri
            with self.subTest(f'testing single literal value: {attribute_uri}'):
                value = graph.value(subject=subj, predicate=URIRef(attribute_uri), any=False)
                self.assertEqual(Literal(expected_value, datatype=expected_type), value)

        with self.subTest(f'testing single URI value: testKeuzelijst'):
            value = graph.value(subject=subj, predicate=URIRef('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKeuzelijst'), any=False)
            self.assertEqual(URIRef('https://wegenenverkeer.data.vlaanderen.be/id/concept/KlTestKeuzelijst/waarde-4'), value)

        for expected_value, expected_type, attribute_uri in [
            ([76, 2], 'http://www.w3.org/2001/XMLSchema#integer', 'testIntegerFieldMetKard'),
            ([76, 2], 'http://www.w3.org/2001/XMLSchema#integer', 'testIntegerFieldMetKard'),
            ([10.0, 20.0], 'http://www.w3.org/2001/XMLSchema#decimal', 'testDecimalFieldMetKard'),
        ]:
            attribute_uri = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.' + attribute_uri
            with self.subTest(f'testing multiple literal value: {attribute_uri}'):
                values = list(graph.objects(subject=subj, predicate=URIRef(attribute_uri)))
                for index, value in enumerate(values):
                    self.assertEqual(Literal(expected_value[index], datatype=expected_type), value)

        with self.subTest(f'testing multiple URI value: testKeuzelijstMetKard'):
            values = list(graph.objects(subject=subj, predicate=URIRef('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKeuzelijstMetKard')))
            expected_values = [URIRef('https://wegenenverkeer.data.vlaanderen.be/id/concept/KlTestKeuzelijst/waarde-4'),
                               URIRef('https://wegenenverkeer.data.vlaanderen.be/id/concept/KlTestKeuzelijst/waarde-3')]
            for index, value in enumerate(values):
                self.assertEqual(expected_values[index], value)

    def test_export_nested_attributes_level_1(self):
        exporter = RDFExporter(dotnotation_settings={'waarde_shortcut_applicable': False})

        instance = AllCasesTestClass()
        instance.assetId.identificator = '0000'

        instance.testEenvoudigType.waarde = 'string1'
        instance._testEenvoudigTypeMetKard.add_empty_value()
        instance._testEenvoudigTypeMetKard.add_empty_value()
        instance.testEenvoudigTypeMetKard[0].waarde = 'string1'
        instance.testEenvoudigTypeMetKard[1].waarde = 'string2'

        instance.testKwantWrd.waarde = 98.21
        instance._testKwantWrdMetKard.add_empty_value()
        instance._testKwantWrdMetKard.add_empty_value()
        instance.testKwantWrdMetKard[0].waarde = 10.0
        instance.testKwantWrdMetKard[1].waarde = 20.0

        instance.testComplexType.testBooleanField = True
        instance.testComplexType.testStringField = 'KmCtMXM'
        instance.testComplexType.testStringFieldMetKard = ['string1', 'string2']

        instance._testComplexTypeMetKard.add_empty_value()
        instance._testComplexTypeMetKard.add_empty_value()
        instance.testComplexTypeMetKard[0].testBooleanField = True
        instance.testComplexTypeMetKard[1].testBooleanField = False
        instance.testComplexTypeMetKard[0].testStringField = 'string1'
        instance.testComplexTypeMetKard[1].testStringField = 'string2'

        instance.testComplexTypeMetKard[0].testStringFieldMetKard = ['1.1', '1.2']
        instance.testComplexTypeMetKard[1].testStringFieldMetKard = ['2.1', '2.2']

        instance.testUnionType.unionString = 'RWKofW'

        graph = exporter.create_graph([instance])

        subj = graph.value(predicate=RDF.type,
                           object=URIRef('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'),
                           any=False)
        self.assertIsNotNone(subj)

        for expected_values, uri1, uri2 in [
            ([Literal('string1')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testEenvoudigType',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DteTestEenvoudigType.waarde'),
            ([Literal('0000')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.assetId',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator.identificator'),
            ([Literal('string1'), Literal('string2')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testEenvoudigTypeMetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DteTestEenvoudigType.waarde'),
            ([Literal('98.21', datatype='http://www.w3.org/2001/XMLSchema#decimal')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKwantWrd',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde'),
            ([Literal('10.0', datatype='http://www.w3.org/2001/XMLSchema#decimal'),
              Literal('20.0', datatype='http://www.w3.org/2001/XMLSchema#decimal')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testKwantWrdMetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde'),
            ([Literal('true', datatype='http://www.w3.org/2001/XMLSchema#boolean')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexType',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testBooleanField'),
            ([Literal('KmCtMXM')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexType',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testStringField'),
            ([Literal('string1'), Literal('string2')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexType',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testStringFieldMetKard'),
            ([Literal('true', datatype='http://www.w3.org/2001/XMLSchema#boolean'),
              Literal('false', datatype='http://www.w3.org/2001/XMLSchema#boolean')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexTypeMetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testBooleanField'),
            ([Literal('string1'), Literal('string2')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexTypeMetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testStringField'),
            ([Literal('1.1'), Literal('1.2'), Literal('2.1'), Literal('2.2')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexTypeMetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testStringFieldMetKard'),
            ([Literal('RWKofW')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testUnionType',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtuTestUnionType.unionString'),
        ]:
            with self.subTest(f'testing complex value level 1: {uri1}'):
                query = """SELECT ?o WHERE { ?s ?p1 ?c .
                                             ?c ?p2 ?o}"""
                query = query.replace('?s', '<' + str(subj) + '>').replace('?p1', '<' + uri1 + '>').\
                    replace('?p2', '<' + uri2 + '>')

                q_res = graph.query(query)

                for index, row in enumerate(q_res):
                    self.assertEqual(expected_values[index], row.o)

    def test_export_nested_attributes_level_higher(self):
        exporter = RDFExporter(dotnotation_settings={'waarde_shortcut_applicable': False})

        instance = AllCasesTestClass()
        instance.assetId.identificator = '0000'

        instance.testComplexType.testKwantWrd.waarde = 65.14
        instance.testComplexType._testKwantWrdMetKard.add_empty_value()
        instance.testComplexType._testKwantWrdMetKard.add_empty_value()
        instance.testComplexType.testKwantWrdMetKard[0].waarde = 10.0
        instance.testComplexType.testKwantWrdMetKard[1].waarde = 20.0

        instance.testComplexType.testComplexType2.testKwantWrd.waarde = 76.8
        instance.testComplexType.testComplexType2.testStringField = 'GZBzgRhOrQvfZaN'
        instance.testComplexType._testComplexType2MetKard.add_empty_value()
        instance.testComplexType._testComplexType2MetKard.add_empty_value()
        instance.testComplexType.testComplexType2MetKard[0].testKwantWrd.waarde = 10.0
        instance.testComplexType.testComplexType2MetKard[1].testKwantWrd.waarde = 20.0
        instance.testComplexType.testComplexType2MetKard[0].testStringField = 'string1'
        instance.testComplexType.testComplexType2MetKard[1].testStringField = 'string2'

        instance._testComplexTypeMetKard.add_empty_value()
        instance._testComplexTypeMetKard.add_empty_value()
        instance.testComplexTypeMetKard[0].testComplexType2.testKwantWrd.waarde = 10.0 # TODO
        instance.testComplexTypeMetKard[1].testComplexType2.testKwantWrd.waarde = 20.0 # TODO
        instance.testComplexTypeMetKard[0].testComplexType2.testStringField = 'string1'
        instance.testComplexTypeMetKard[1].testComplexType2.testStringField = 'string2'

        instance.testComplexTypeMetKard[0]._testComplexType2MetKard.add_empty_value()
        instance.testComplexTypeMetKard[0]._testComplexType2MetKard.add_empty_value()
        instance.testComplexTypeMetKard[1]._testComplexType2MetKard.add_empty_value()
        instance.testComplexTypeMetKard[1]._testComplexType2MetKard.add_empty_value()
        instance.testComplexTypeMetKard[0].testComplexType2MetKard[0].testStringField = '1.1'
        instance.testComplexTypeMetKard[0].testComplexType2MetKard[1].testStringField = '1.2'
        instance.testComplexTypeMetKard[1].testComplexType2MetKard[0].testStringField = '2.1'
        instance.testComplexTypeMetKard[1].testComplexType2MetKard[1].testStringField = '2.2'

        instance.testComplexTypeMetKard[0].testKwantWrd.waarde = 10.0
        instance.testComplexTypeMetKard[1].testKwantWrd.waarde = 20.0

        instance._testUnionTypeMetKard.add_empty_value()
        instance._testUnionTypeMetKard.add_empty_value()
        instance.testUnionTypeMetKard[0].unionKwantWrd.waarde = 10.0
        instance.testUnionTypeMetKard[1].unionKwantWrd.waarde = 20.0

        graph = exporter.create_graph([instance])

        subj = graph.value(predicate=RDF.type,
                           object=URIRef('https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass'),
                           any=False)
        self.assertIsNotNone(subj)

        for expected_values, uri1, uri2, uri3 in [
            ([Literal('65.14', datatype='http://www.w3.org/2001/XMLSchema#decimal')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexType',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testKwantWrd',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde'),
            ([Literal('10.0', datatype='http://www.w3.org/2001/XMLSchema#decimal'),
              Literal('20.0', datatype='http://www.w3.org/2001/XMLSchema#decimal')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexType',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testKwantWrdMetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde'),
            ([Literal('GZBzgRhOrQvfZaN')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexType',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testComplexType2',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType2.testStringField'),
            ([Literal('string1'), Literal('string2')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexType',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testComplexType2MetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType2.testStringField'),
            ([Literal('string1'), Literal('string2')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexTypeMetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testComplexType2',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType2.testStringField'),
            ([Literal('1.1'), Literal('1.2'), Literal('2.1'), Literal('2.2')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexTypeMetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testComplexType2MetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType2.testStringField'),
            ([Literal('10.0', datatype='http://www.w3.org/2001/XMLSchema#decimal'),
              Literal('20.0', datatype='http://www.w3.org/2001/XMLSchema#decimal')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexTypeMetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testKwantWrd',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde'),
            ([Literal('10.0', datatype='http://www.w3.org/2001/XMLSchema#decimal'),
              Literal('20.0', datatype='http://www.w3.org/2001/XMLSchema#decimal')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testUnionTypeMetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtuUnionType.testKwantWrd',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde'),
        ]:
            with self.subTest(f'testing complex values level 2: {uri1}'):
                query = """SELECT ?o WHERE { ?s ?p1 ?c1 .
                                     ?c1 ?p2 ?c2 .
                                     ?c2 ?p3 ?o .}"""
                query = query.replace('?s', '<' + str(subj) + '>').replace('?p1', '<' + uri1 + '>').\
                    replace('?p2', '<' + uri2 + '>').replace('?p3', '<' + uri3 + '>')

                q_res = graph.query(query)

                for index, row in enumerate(q_res):
                    self.assertEqual(expected_values[index], row.o)

        for expected_values, uri1, uri2, uri3, uri4 in [
            ([Literal('76.8', datatype='http://www.w3.org/2001/XMLSchema#decimal')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexType',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testComplexType2',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType2.testKwantWrd',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde'),
            ([Literal('10.0', datatype='http://www.w3.org/2001/XMLSchema#decimal'),
              Literal('20.0', datatype='http://www.w3.org/2001/XMLSchema#decimal')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexType',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testComplexType2MetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType2.testKwantWrd',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde'),
            ([Literal('10.0', datatype='http://www.w3.org/2001/XMLSchema#decimal'),
              Literal('20.0', datatype='http://www.w3.org/2001/XMLSchema#decimal')],
             'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass.testComplexTypeMetKard',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testComplexType2',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType2.testKwantWrd',
             'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdTest.waarde'),
        ]:
            with self.subTest(f'testing complex values level 3: {uri1}'):
                query = """SELECT ?o WHERE { ?s ?p1 ?c1 .
                                     ?c1 ?p2 ?c2 .
                                     ?c2 ?p3 ?c3 .
                                     ?c3 ?p4 ?o .}"""
                query = query.replace('?s', '<' + str(subj) + '>').replace('?p1', '<' + uri1 + '>'). \
                    replace('?p2', '<' + uri2 + '>').replace('?p3', '<' + uri3 + '>').replace('?p4', '<' + uri4 + '>')

                q_res = graph.query(query)

                for index, row in enumerate(q_res):
                    self.assertEqual(expected_values[index], row.o)
