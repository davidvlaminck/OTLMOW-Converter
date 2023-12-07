import importlib
import warnings
from pathlib import Path
from typing import Union, List, Type, Dict, Sequence, Any

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_model.OtlmowModel.Helpers.AssetCreator import dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.Helpers.GenericHelper import get_shortened_uri

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.Exceptions.BadTypeWarning import BadTypeWarning
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

    def load_settings(self, dotnotation_settings: Dict):
        if 'separator' in dotnotation_settings:
            self.separator = dotnotation_settings['separator']
        if 'cardinality_separator' in dotnotation_settings:
            self.cardinality_separator = dotnotation_settings['cardinality_separator']
        if 'cardinality_indicator' in dotnotation_settings:
            self.cardinality_indicator = dotnotation_settings['cardinality_indicator']
        if 'waarde_shortcut' in dotnotation_settings:
            self.waarde_shortcut = dotnotation_settings['waarde_shortcut']

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
    def _get_index_of_typeURI_column_in_sheet(cls, filepath: Path, sheet: str, headers: List[str],
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

    @classmethod
    def _sort_headers(cls, headers: dict) -> Sequence[str]:
        if headers is None or headers == {}:
            return []
        headers.pop('typeURI')
        headers.pop('assetId.identificator')
        headers.pop('assetId.toegekendDoor')
        sorted_list = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor']

        sorted_rest = sorted(headers)
        sorted_list.extend(sorted_rest)

        return sorted_list

    def get_single_table_from_data(self, list_of_objects: [OTLObject], values_as_string: bool = False) -> Sequence[Dict]:
        """Returns a list of dicts, where each dict is a row, and the first row is the header"""
        identificator_key = 'assetId.identificator'.replace('.', self.separator)
        toegekend_door_key = 'assetId.toegekendDoor'.replace('.', self.separator)

        list_of_dicts = []
        header_dict = {'typeURI': 0, identificator_key: 1, toegekend_door_key: 2}
        header_count = 3

        for otl_object in list_of_objects:
            if not hasattr(otl_object, 'is_instance_of'):
                warnings.warn(
                    BadTypeWarning(f'{otl_object} does not have an is_instance_of method. Ignoring this object'))
                continue
            if not otl_object.is_instance_of(self.otl_object_ref):
                warnings.warn(
                    BadTypeWarning(f'{otl_object} is not of type AIMObject. Ignoring this object'))
                continue

            if not self.ignore_empty_asset_id:
                if otl_object.assetId.identificator is None or otl_object.assetId.identificator == '':
                    raise ValueError(f'{otl_object} does not have an asset-id.')

            data_dict = {
                'typeURI': otl_object.typeURI,
                identificator_key: otl_object.assetId.identificator
            }

            for k, v in self.dotnotation_helper.list_attributes_and_values_by_dotnotation_instance(
                    instance_or_attribute=otl_object):
                if k == identificator_key:
                    continue
                if k not in header_dict:
                    header_dict[k] = header_count
                    header_count += 1
                if values_as_string:
                    data_dict[k] = self._turn_value_to_string(v)
                else:
                    data_dict[k] = v
            list_of_dicts.append(data_dict)
        list_of_dicts.insert(0, header_dict)
        return list_of_dicts

    def get_tables_per_type_from_data(self, list_of_objects: [OTLObject], values_as_string: bool = False
                                      ) -> Dict[str, Sequence[Dict]]:
        """Returns a dictionary with typeURIs as keys and a list of dicts as values, where each dict is a row, and the
        first row is the header"""
        identificator_key = 'assetId.identificator'.replace('.', self.separator)
        toegekend_door_key = 'assetId.toegekendDoor'.replace('.', self.separator)

        master_dict = {}

        for otl_object in list_of_objects:
            if not hasattr(otl_object, 'is_instance_of'):
                warnings.warn(
                    BadTypeWarning(f'{otl_object} does not have an is_instance_of method. Ignoring this object'))
                continue
            if not otl_object.is_instance_of(self.otl_object_ref):
                warnings.warn(
                    BadTypeWarning(f'{otl_object} is not of type AIMObject. Ignoring this object'))
                continue

            if not self.ignore_empty_asset_id:
                if otl_object.assetId.identificator is None or otl_object.assetId.identificator == '':
                    raise ValueError(f'{otl_object} does not have an asset-id.')

            short_uri = get_shortened_uri(otl_object.typeURI)
            if short_uri not in master_dict:
                master_dict[short_uri] = [{'typeURI': 0, identificator_key: 1, toegekend_door_key: 2}]
            header_dict = master_dict[short_uri][0]
            header_count = len(header_dict)
            data_dict = {
                'typeURI': otl_object.typeURI,
                identificator_key: otl_object.assetId.identificator
            }

            for k, v in self.dotnotation_helper.list_attributes_and_values_by_dotnotation_instance(
                    instance_or_attribute=otl_object):
                if k == identificator_key:
                    continue
                if k not in header_dict:
                    header_dict[k] = header_count
                    header_count += 1
                if values_as_string:
                    data_dict[k] = self._turn_value_to_string(v)
                else:
                    data_dict[k] = v
            master_dict[short_uri].append(data_dict)

        return master_dict

    def get_data_from_table(self, table_data: Sequence[Dict], empty_string_equals_none: bool = False,
                            convert_strings_to_types: bool = False) -> [OTLObject]:
        """Returns a list of OTL objects from a list of dicts, where each dict is a row, and the first row is the
        header"""
        instances = []
        headers = table_data[0]
        headers.pop('typeURI')
        for row in table_data[1:]:
            instance = dynamic_create_instance_from_uri(row['typeURI'], model_directory=self.model_directory)
            instances.append(instance)
            for header in headers:
                try:
                    value = row.get(header, None)
                    if value is None:
                        continue
                    if empty_string_equals_none and value == '':
                        continue
                    self.dotnotation_helper.set_attribute_by_dotnotation_instance(
                        instance_or_attribute=instance, dotnotation=header, value=value,
                        convert=convert_strings_to_types)
                except AttributeError:
                    asset_id = row['assetId.identificator']
                    raise AttributeError(f'{header} for asset {asset_id}')

        return instances

    @classmethod
    def transform_list_of_dicts_to_2d_sequence(cls, list_of_dicts: Sequence[Dict],
                                               empty_string_equals_none: bool = False) -> Sequence[Sequence]:
        """Returns a 2d array from a list of dicts, where each dict is a row, and the first row is the header"""
        # TODO also try this with numpy arrays to see what is faster

        sorted_headers = cls._sort_headers(list_of_dicts[0])
        matrix = [[cls._get_item_from_dict(input_dict=d, item=header, empty_string_equals_none=empty_string_equals_none)
                   for header in sorted_headers] for d in list_of_dicts[1:]]
        matrix.insert(0, sorted_headers)
        return matrix

    @classmethod
    def transform_2d_sequence_to_list_of_dicts(cls, two_d_sequence: Sequence[Sequence],
                                               empty_string_equals_none: bool = False) -> Sequence[Dict]:
        """Returns a list of dicts from a 2d array, where each dict is a row, and the first row is the header"""
        # TODO also try this with numpy arrays to see what is faster
        header_row = two_d_sequence[0]
        header_dict = {header: index for index, header in enumerate(header_row)}

        list_of_dicts = [header_dict]
        for row in two_d_sequence[1:]:
            data_dict = {}
            for header, index in header_dict.items():
                value = row[index]
                if value is None:
                    continue
                if empty_string_equals_none and value == '':
                    continue
                data_dict[header] = value
            list_of_dicts.append(data_dict)

        return list_of_dicts

    @classmethod
    def _get_item_from_dict(cls, input_dict: dict, item: str, empty_string_equals_none: bool):
        value = input_dict.get(item, None)
        if empty_string_equals_none and value is None:
            return ''
        return value

    def _turn_value_to_string(self, value: Any) -> str:
        if isinstance(value, list):
            if isinstance(value[0], list):
                raise ValueError(f'Not possible to turn a list of a list into a string')

            str_list = [(str(item) if item is not None else '') for item in value]
            return self.cardinality_separator.join(str_list)
        if not isinstance(value, str):
            return str(value)
        return value
