from abc import abstractmethod
from pathlib import Path

from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_class_dict, get_concrete_subclasses_from_class_dict


class RelationInteractor:
    typeURI = ''
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def add_valid_relation(self, relation: str, target: str, direction: str = 'o', deprecated: str = ''):
        if relation not in self._valid_relations:
            self._valid_relations[relation] = {}
        if target not in self._valid_relations[relation]:
            self._valid_relations[relation][target] = {}
        self._valid_relations[relation][target][direction] = deprecated

    @abstractmethod
    def __init__(self):
        super().__init__()

        self._valid_relations = {}
