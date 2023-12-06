import importlib
import logging
from ctypes import Array
from pathlib import Path
from typing import Union, List, Type, Dict, Sequence

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_model.OtlmowModel.Helpers.AssetCreator import dynamic_create_instance_from_uri

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.Exceptions.NoTypeUriInExcelTabError import NoTypeUriInExcelTabError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError

SEPARATOR = '.'
CARDINALITY_SEPARATOR = '|'
CARDINALITY_INDICATOR = '[]'
WAARDE_SHORTCUT = True


class DotnotationTableConverter:
    """Converts a list of OTL objects from and to a table with dotnotation as columns headers"""

    def __init__(self, model_directory: Path = None, ignore_empty_asset_id: bool = False,
                 dates_as_strings: bool = False,
                 separator: str = SEPARATOR, cardinality_separator: str = CARDINALITY_SEPARATOR,
                 cardinality_indicator: str = CARDINALITY_INDICATOR, waarde_shortcut: bool = WAARDE_SHORTCUT):
        self.model_directory: Path
        if model_directory is None:
            import otlmow_model
            otlmow_path = otlmow_model.__path__
            self.model_directory = Path(otlmow_path._path[0])
        else:
            self.model_directory = model_directory

        self.ignore_empty_asset_id: bool = ignore_empty_asset_id
        self.dates_as_strings: bool = dates_as_strings

        self.separator: str = separator
        self.cardinality_separator: str = cardinality_separator
        self.cardinality_indicator: str = cardinality_indicator
        self.waarde_shortcut: bool = waarde_shortcut

        self.otl_object_ref = self._import_otl_object()

        self.dotnotation_helper: DotnotationHelper = self.get_dotnotation_helper()

    def load_from_settings(self, settings: Dict):
        if 'separator' in settings:
            self.separator = settings['separator']
        if 'cardinality_separator' in settings:
            self.cardinality_separator = settings['cardinality_separator']
        if 'cardinality_indicator' in settings:
            self.cardinality_indicator = settings['cardinality_indicator']
        if 'waarde_shortcut' in settings:
            self.waarde_shortcut = settings['waarde_shortcut']

        self.dotnotation_helper: DotnotationHelper = self.get_dotnotation_helper()

    def get_dotnotation_helper(self) -> DotnotationHelper:
        return DotnotationHelper(separator=self.separator, cardinality_separator=self.cardinality_separator,
                                 cardinality_indicator=self.cardinality_indicator, waarde_shortcut=self.waarde_shortcut)

    @classmethod
    def _import_otl_object(cls) -> Union[Type[OTLObject], None]:
        try:
            mod = importlib.import_module('otlmow_model.OtlmowModel.BaseClasses.OTLObject')
            class_ = getattr(mod, 'OTLObject')
            return class_

        except ModuleNotFoundError:
            raise ModuleNotFoundError(f'When dynamically importing class OTLObject, the import failed. '
                                      f'Make sure you are directing to the (parent) directory where OtlmowModel is '
                                      f'located in.')

    @classmethod
    def get_index_of_typeURI_column_in_sheet(cls, filepath: Path, sheet: str, headers: List[str],
                                             data: List[List[str]]) -> int:
        try:
            type_index = headers.index('typeURI')
        except ValueError:
            type_index = -1
        if type_index == -1:
            for row in data[1:5]:
                try:
                    type_index = row.index('typeURI')
                except ValueError:
                    type_index = -1
                if type_index != -1:
                    break
            if type_index == -1:
                raise NoTypeUriInExcelTabError(
                    message=f'Could not find typeURI within 5 rows in Excel tab {sheet} in file {filepath.name}',
                    file_path=filepath, tab=sheet)
            else:
                raise TypeUriNotInFirstRowError(
                    message=f'The typeURI is not in the first row in Excel tab {sheet} in file {filepath.name}.'
                            f' Please remove the excess rows', file_path=filepath, tab=sheet)
        return type_index

    def get_single_table_from_data(self, list_of_objects: [OTLObject]) -> Sequence[Dict]:
        """Returns a list of dicts, where each dict is a row, and the first row is the header"""
        pass

    def get_tables_per_type_from_data(self, list_of_objects: [OTLObject]) -> Dict[str, Sequence[Dict]]:
        """Returns a dictionary with typeURIs as keys and a list of dicts as values, where each dict is a row, and the
        first row is the header"""
        pass

    def get_data_from_table(self, table_data: Sequence[Dict]) -> [OTLObject]:
        """Returns a list of OTL objects from a list of dicts, where each dict is a row, and the first row is the
        header"""
        pass

    def transform_list_of_dicts_to_2d_sequence(self, list_of_dicts: Sequence[Dict]) -> Sequence[Sequence]:
        """Returns a 2d array from a list of dicts, where each dict is a row, and the first row is the header"""
        # also try this with numpy arrays to see what is faster
        pass

    def transform_2d_sequence_to_list_of_dicts(self, two_d_sequence: Sequence[Sequence]) -> Sequence[Dict]:
        """Returns a list of dicts from a 2d array, where each dict is a row, and the first row is the header"""
        # also try this with numpy arrays to see what is faster
        pass

