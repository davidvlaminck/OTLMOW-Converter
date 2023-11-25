# coding=utf-8
from abc import abstractmethod
from ...Classes.ImplementatieElement.RelatieObject import RelatieObject


# Generated with OTLClassCreator. To modify: extend, do not edit
class DirectioneleRelatie(RelatieObject):
    """Een abstracte die relaties groepeert waarbij de richting semantisch gedefinieerd is."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DirectioneleRelatie'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    @abstractmethod
    def __init__(self):
        super().__init__()
