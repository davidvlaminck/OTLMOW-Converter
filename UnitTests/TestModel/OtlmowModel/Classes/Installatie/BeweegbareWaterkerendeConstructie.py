# coding=utf-8
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut

from otlmow_model.OtlmowModel.BaseClasses.BooleanField import BooleanField
from otlmow_model.OtlmowModel.Classes.Abstracten.ConstructiefObject import ConstructiefObject
from otlmow_model.OtlmowModel.Datatypes.DtcAfmetingBxlInCm import DtcAfmetingBxlInCm, DtcAfmetingBxlInCmWaarden
from otlmow_model.OtlmowModel.Datatypes.DtcAfmetingBxlxhInM import DtcAfmetingBxlxhInM, DtcAfmetingBxlxhInMWaarden
from otlmow_model.OtlmowModel.Datatypes.DtcTypeBWC import DtcTypeBWC, DtcTypeBWCWaarden
from otlmow_model.OtlmowModel.Datatypes.KlMateriaalBWCTWC import KlMateriaalBWCTWC
from otlmow_model.OtlmowModel.Datatypes.KwantWrdInMeterTAW import KwantWrdInMeterTAW, KwantWrdInMeterTAWWaarden
from otlmow_model.OtlmowModel.Datatypes.KwantWrdInTon import KwantWrdInTon, KwantWrdInTonWaarden

from otlmow_model.OtlmowModel.GeometrieTypes.VlakGeometrie import VlakGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class BeweegbareWaterkerendeConstructie(ConstructiefObject, VlakGeometrie):
    """Beweegbare constructie om een waterpeilverschil te keren"""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        super().__init__()

        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#AanhorigheidSluisStuw')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#BekledingComponent')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Inloopbehuizing')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#KabelgeleidingEnLeidingBevestiging')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Kast')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#NietWeggebondenDetectie')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Seinlantaarn')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Ventilatie')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Verkeersbord')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Verlichtingstoestel')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Waarschuwingslantaarn')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#ZenderOntvangerToegang')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Binnenverlichtingstoestel')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HoortBij', target='https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#Constructiehoofd')

        self._afmetingenMangat = OTLAttribuut(field=DtcAfmetingBxlInCm,
                                              naam='afmetingenMangat',
                                              label='afmetingen mangat',
                                              objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.afmetingenMangat',
                                              definition='De afmeting van het mangat in centimeter.',
                                              owner=self)

        self._basisAfmeting = OTLAttribuut(field=DtcAfmetingBxlxhInM,
                                           naam='basisAfmeting',
                                           label='basis afmeting',
                                           objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.basisAfmeting',
                                           definition='Breedte en hoogte van een beweegbare waterkerende constructie uitgedrukt in meter.',
                                           owner=self)

        self._gewicht = OTLAttribuut(field=KwantWrdInTon,
                                     naam='gewicht',
                                     label='gewicht',
                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.gewicht',
                                     definition='Het gewicht van de beweegbare waterkerende constructie, uitgedrukt in ton.',
                                     owner=self)

        self._heeftDraaischelpen = OTLAttribuut(field=BooleanField,
                                                naam='heeftDraaischelpen',
                                                label='heeft draaischelpen',
                                                objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.heeftDraaischelpen',
                                                definition='Geeft aan of er draaischelpen aanwezig zijn.',
                                                owner=self)

        self._heeftHijsogen = OTLAttribuut(field=BooleanField,
                                           naam='heeftHijsogen',
                                           label='heeft hijsogen',
                                           objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.heeftHijsogen',
                                           definition='Geeft aan of er hijsogen aanwezig zijn.',
                                           owner=self)

        self._heeftOpboutbareDraaischelpen = OTLAttribuut(field=BooleanField,
                                                          naam='heeftOpboutbareDraaischelpen',
                                                          label='heeft opboutbare draaischelpen',
                                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.heeftOpboutbareDraaischelpen',
                                                          definition='Geeft aan of er opboutbare draaischelpen aanwezig zijn.',
                                                          owner=self)

        self._heeftOpboutbareHijsogen = OTLAttribuut(field=BooleanField,
                                                     naam='heeftOpboutbareHijsogen',
                                                     label='heeft opboutbare hijsogen',
                                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.heeftOpboutbareHijsogen',
                                                     definition='Geeft aan of er opboutbare hijsogen aanwezig zijn.',
                                                     owner=self)

        self._heeftPompput = OTLAttribuut(field=BooleanField,
                                          naam='heeftPompput',
                                          label='heeft pompput',
                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.heeftPompput',
                                          definition='Geeft aan of in de beweegbare waterkerende constructie een pompput aanwezig is.',
                                          owner=self)

        self._isHoogtebeperkingAanwezig = OTLAttribuut(field=BooleanField,
                                                       naam='isHoogtebeperkingAanwezig',
                                                       label='is hoogtebeperking aanwezig',
                                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.isHoogtebeperkingAanwezig',
                                                       definition='Geeft aan of er een hoogte beperking aanwezig is.',
                                                       owner=self)

        self._isMangatAanwezig = OTLAttribuut(field=BooleanField,
                                              naam='isMangatAanwezig',
                                              label='is mangat aanwezig',
                                              objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.isMangatAanwezig',
                                              definition='Geeft aan of er een mangat aanwezig is.',
                                              owner=self)

        self._isNivelleerOfSpuivoorzieningAanwezig = OTLAttribuut(field=BooleanField,
                                                                  naam='isNivelleerOfSpuivoorzieningAanwezig',
                                                                  label='is nivelleer of spuivoorziening aanwezig',
                                                                  objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.isNivelleerOfSpuivoorzieningAanwezig',
                                                                  definition='Geeft aan of er nivelleer -of spuivoorzieningen aanwezig zijn.',
                                                                  owner=self)

        self._kruinpeil = OTLAttribuut(field=KwantWrdInMeterTAW,
                                       naam='kruinpeil',
                                       label='kruinpeil',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.kruinpeil',
                                       definition='Het hoogste punt van de constructie waar het water normaliter niet overheen mag stromen om overstromingen te voorkomen.',
                                       owner=self)

        self._materiaal = OTLAttribuut(field=KlMateriaalBWCTWC,
                                       naam='materiaal',
                                       label='materiaal',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.materiaal',
                                       definition='Geeft de verschillende mogelijkheden aan om te weten vanuit welk materiaal de beweegbare waterkerende constructie is uitgevoerd.',
                                       owner=self)

        self._niveauHoogtebeperking = OTLAttribuut(field=KwantWrdInMeterTAW,
                                                   naam='niveauHoogtebeperking',
                                                   label='niveau hoogtebeperking',
                                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.niveauHoogtebeperking',
                                                   definition='Het niveau van de hoogte beperking, uitgedrukt in meter TAW.',
                                                   owner=self)

        self._typeBeweegbareconstructie = OTLAttribuut(field=DtcTypeBWC,
                                                       naam='typeBeweegbareconstructie',
                                                       label='type beweegbareconstructie',
                                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#BeweegbareWaterkerendeConstructie.typeBeweegbareconstructie',
                                                       definition='Complex datatype om het type beweegbare waterkerende constructie aan te duiden',
                                                       owner=self)

    @property
    def afmetingenMangat(self) -> DtcAfmetingBxlInCmWaarden:
        """De afmeting van het mangat in centimeter."""
        return self._afmetingenMangat.get_waarde()

    @afmetingenMangat.setter
    def afmetingenMangat(self, value):
        self._afmetingenMangat.set_waarde(value, owner=self)

    @property
    def basisAfmeting(self) -> DtcAfmetingBxlxhInMWaarden:
        """Breedte en hoogte van een beweegbare waterkerende constructie uitgedrukt in meter."""
        return self._basisAfmeting.get_waarde()

    @basisAfmeting.setter
    def basisAfmeting(self, value):
        self._basisAfmeting.set_waarde(value, owner=self)

    @property
    def gewicht(self) -> KwantWrdInTonWaarden:
        """Het gewicht van de beweegbare waterkerende constructie, uitgedrukt in ton."""
        return self._gewicht.get_waarde()

    @gewicht.setter
    def gewicht(self, value):
        self._gewicht.set_waarde(value, owner=self)

    @property
    def heeftDraaischelpen(self) -> bool:
        """Geeft aan of er draaischelpen aanwezig zijn."""
        return self._heeftDraaischelpen.get_waarde()

    @heeftDraaischelpen.setter
    def heeftDraaischelpen(self, value):
        self._heeftDraaischelpen.set_waarde(value, owner=self)

    @property
    def heeftHijsogen(self) -> bool:
        """Geeft aan of er hijsogen aanwezig zijn."""
        return self._heeftHijsogen.get_waarde()

    @heeftHijsogen.setter
    def heeftHijsogen(self, value):
        self._heeftHijsogen.set_waarde(value, owner=self)

    @property
    def heeftOpboutbareDraaischelpen(self) -> bool:
        """Geeft aan of er opboutbare draaischelpen aanwezig zijn."""
        return self._heeftOpboutbareDraaischelpen.get_waarde()

    @heeftOpboutbareDraaischelpen.setter
    def heeftOpboutbareDraaischelpen(self, value):
        self._heeftOpboutbareDraaischelpen.set_waarde(value, owner=self)

    @property
    def heeftOpboutbareHijsogen(self) -> bool:
        """Geeft aan of er opboutbare hijsogen aanwezig zijn."""
        return self._heeftOpboutbareHijsogen.get_waarde()

    @heeftOpboutbareHijsogen.setter
    def heeftOpboutbareHijsogen(self, value):
        self._heeftOpboutbareHijsogen.set_waarde(value, owner=self)

    @property
    def heeftPompput(self) -> bool:
        """Geeft aan of in de beweegbare waterkerende constructie een pompput aanwezig is."""
        return self._heeftPompput.get_waarde()

    @heeftPompput.setter
    def heeftPompput(self, value):
        self._heeftPompput.set_waarde(value, owner=self)

    @property
    def isHoogtebeperkingAanwezig(self) -> bool:
        """Geeft aan of er een hoogte beperking aanwezig is."""
        return self._isHoogtebeperkingAanwezig.get_waarde()

    @isHoogtebeperkingAanwezig.setter
    def isHoogtebeperkingAanwezig(self, value):
        self._isHoogtebeperkingAanwezig.set_waarde(value, owner=self)

    @property
    def isMangatAanwezig(self) -> bool:
        """Geeft aan of er een mangat aanwezig is."""
        return self._isMangatAanwezig.get_waarde()

    @isMangatAanwezig.setter
    def isMangatAanwezig(self, value):
        self._isMangatAanwezig.set_waarde(value, owner=self)

    @property
    def isNivelleerOfSpuivoorzieningAanwezig(self) -> bool:
        """Geeft aan of er nivelleer -of spuivoorzieningen aanwezig zijn."""
        return self._isNivelleerOfSpuivoorzieningAanwezig.get_waarde()

    @isNivelleerOfSpuivoorzieningAanwezig.setter
    def isNivelleerOfSpuivoorzieningAanwezig(self, value):
        self._isNivelleerOfSpuivoorzieningAanwezig.set_waarde(value, owner=self)

    @property
    def kruinpeil(self) -> KwantWrdInMeterTAWWaarden:
        """Het hoogste punt van de constructie waar het water normaliter niet overheen mag stromen om overstromingen te voorkomen."""
        return self._kruinpeil.get_waarde()

    @kruinpeil.setter
    def kruinpeil(self, value):
        self._kruinpeil.set_waarde(value, owner=self)

    @property
    def materiaal(self) -> str:
        """Geeft de verschillende mogelijkheden aan om te weten vanuit welk materiaal de beweegbare waterkerende constructie is uitgevoerd."""
        return self._materiaal.get_waarde()

    @materiaal.setter
    def materiaal(self, value):
        self._materiaal.set_waarde(value, owner=self)

    @property
    def niveauHoogtebeperking(self) -> KwantWrdInMeterTAWWaarden:
        """Het niveau van de hoogte beperking, uitgedrukt in meter TAW."""
        return self._niveauHoogtebeperking.get_waarde()

    @niveauHoogtebeperking.setter
    def niveauHoogtebeperking(self, value):
        self._niveauHoogtebeperking.set_waarde(value, owner=self)

    @property
    def typeBeweegbareconstructie(self) -> DtcTypeBWCWaarden:
        """Complex datatype om het type beweegbare waterkerende constructie aan te duiden"""
        return self._typeBeweegbareconstructie.get_waarde()

    @typeBeweegbareconstructie.setter
    def typeBeweegbareconstructie(self, value):
        self._typeBeweegbareconstructie.set_waarde(value, owner=self)
