# coding=utf-8
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut
from otlmow_model.OtlmowModel.BaseClasses.NonNegIntegerField import NonNegIntegerField
from otlmow_model.OtlmowModel.Classes.Abstracten.EMAfbakening import EMAfbakening
from otlmow_model.OtlmowModel.Datatypes.KlAlgMateriaal import KlAlgMateriaal
from otlmow_model.OtlmowModel.GeometrieTypes.LijnGeometrie import LijnGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class Bochtafbakeningsinstallatie(EMAfbakening, LijnGeometrie):
    """De verzameling van alle bochtafbakeningsborden in dezelfde bocht en rijrichting."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Bochtafbakeningsinstallatie'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        super().__init__()

        self._aantalBorden = OTLAttribuut(field=NonNegIntegerField,
                                          naam='aantalBorden',
                                          label='aantal borden',
                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Bochtafbakeningsinstallatie.aantalBorden',
                                          definition='Het aantal borden in de bochtafbakening voor het aanduiden van een bocht in een rijrichting.',
                                          owner=self)

        self._materiaalBehuizing = OTLAttribuut(field=KlAlgMateriaal,
                                                naam='materiaalBehuizing',
                                                label='materiaal behuizing',
                                                objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Bochtafbakeningsinstallatie.materiaalBehuizing',
                                                definition='Het materiaal waaruit de behuizing gemaakt is.',
                                                owner=self)

    @property
    def aantalBorden(self) -> int:
        """Het aantal borden in de bochtafbakening voor het aanduiden van een bocht in een rijrichting."""
        return self._aantalBorden.get_waarde()

    @aantalBorden.setter
    def aantalBorden(self, value):
        self._aantalBorden.set_waarde(value, owner=self)

    @property
    def materiaalBehuizing(self) -> str:
        """Het materiaal waaruit de behuizing gemaakt is."""
        return self._materiaalBehuizing.get_waarde()

    @materiaalBehuizing.setter
    def materiaalBehuizing(self, value):
        self._materiaalBehuizing.set_waarde(value, owner=self)
