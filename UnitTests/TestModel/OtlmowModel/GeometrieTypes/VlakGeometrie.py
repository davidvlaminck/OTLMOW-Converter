from abc import abstractmethod

from otlmow_model.OtlmowModel.GeometrieTypes.AbstracteGeometrie import AbstracteGeometrie


class VlakGeometrie(AbstracteGeometrie):
    @abstractmethod
    def __init__(self):
        super().__init__()
        self._geometry_types.append('POLYGON Z')
