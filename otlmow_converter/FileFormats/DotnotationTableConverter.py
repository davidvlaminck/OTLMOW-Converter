import datetime
import math
import warnings
from pathlib import Path
from typing import Dict, Any, Iterable, List

from otlmow_model.OtlmowModel.BaseClasses.DateField import DateField
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.Helpers.GenericHelper import get_shortened_uri

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.Exceptions.BadTypeWarning import BadTypeWarning
from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError
from otlmow_converter.Exceptions.NoTypeUriInTableError import NoTypeUriInTableError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError

from otlmow_converter.SettingsManager import load_settings, GlobalVariables

load_settings()

SEPARATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['separator']
CARDINALITY_SEPARATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['cardinality_separator']
CARDINALITY_INDICATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['cardinality_indicator']
WAARDE_SHORTCUT = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['waarde_shortcut']


class DotnotationTableConverter:
    """Converts a list of OTL objects from and to a table with dotnotation as columns headers"""

    def __init__(self, model_directory: Path = None, ignore_empty_asset_id: bool = False,
                 dates_as_strings: bool = False,
                 separator: str = SEPARATOR, cardinality_separator: str = CARDINALITY_SEPARATOR,
                 cardinality_indicator: str = CARDINALITY_INDICATOR, waarde_shortcut: bool = WAARDE_SHORTCUT):
        self.model_directory: Path = model_directory

        self.ignore_empty_asset_id: bool = ignore_empty_asset_id
        self.dates_as_strings: bool = dates_as_strings

        self.separator: str = separator
        self.cardinality_separator: str = cardinality_separator
        self.cardinality_indicator: str = cardinality_indicator
        self.waarde_shortcut: bool = waarde_shortcut

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
    def _sort_headers(cls, headers: dict) -> Iterable[str]:
        if headers is None or not headers:
            return []
        headers.pop('typeURI')
        headers.pop('assetId.identificator')
        headers.pop('assetId.toegekendDoor')
        sorted_list = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor']

        sorted_rest = sorted(headers)
        sorted_list.extend(sorted_rest)

        return sorted_list

    def get_single_table_from_data(self, list_of_objects: Iterable[OTLObject], values_as_string: bool = False
                                   ) -> List[Dict]:
        """Returns a list of dicts, where each dict is a row, and the first row is the header"""
        identificator_key = 'assetId.identificator'.replace('.', self.separator)
        toegekend_door_key = 'assetId.toegekendDoor'.replace('.', self.separator)

        list_of_dicts = []
        header_dict = {'typeURI': 0, identificator_key: 1, toegekend_door_key: 2}
        header_count = 3

        for otl_object in list_of_objects:
            if not hasattr(otl_object, 'typeURI'):
                warnings.warn(BadTypeWarning(f'{otl_object} does not have a typeURI so this can not be instantiated. '
                                             f'Ignoring this object'))
                continue

            if not self.ignore_empty_asset_id and (otl_object.assetId.identificator is None 
                                                   or otl_object.assetId.identificator == ''):
                raise ValueError(f'{otl_object} does not have an assetId.')

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
                data_dict[k] = self._turn_value_to_string(v) if values_as_string else v
            list_of_dicts.append(data_dict)
        list_of_dicts.insert(0, header_dict)
        return list_of_dicts

    def get_tables_per_type_from_data(self, list_of_objects: Iterable[OTLObject], values_as_string: bool = False
                                      ) -> Dict[str, List[Dict]]:
        """Returns a dictionary with typeURIs as keys and a list of dicts as values, where each dict is a row, and the
        first row is the header"""
        identificator_key = 'assetId.identificator'.replace('.', self.separator)
        toegekend_door_key = 'assetId.toegekendDoor'.replace('.', self.separator)

        master_dict = {}

        for otl_object in list_of_objects:
            if not hasattr(otl_object, 'typeURI'):
                warnings.warn(BadTypeWarning(f'{otl_object} does not have a typeURI so this can not be instantiated. '
                                             f'Ignoring this object'))
                continue

            if not self.ignore_empty_asset_id and (otl_object.assetId.identificator is None or 
                                                   otl_object.assetId.identificator == ''):
                raise ValueError(f'{otl_object} does not have an assetId.')

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
                data_dict[k] = self._turn_value_to_string(v) if values_as_string else v
            master_dict[short_uri].append(data_dict)

        return master_dict

    def get_data_from_table(self, table_data: List[Dict], empty_string_equals_none: bool = False,
                            convert_strings_to_types: bool = False, convert_datetimes_to_dates: bool = False
                            ) -> List[OTLObject]:
        """Returns a list of OTL objects from a list of dicts, where each dict is a row, and the first row is the
        header"""
        instances = []
        headers = table_data[0]
        if 'typeURI' not in headers:
            type_uri_in_first_rows = any('typeURI' in row.values() for row in table_data[1:5])
            if not type_uri_in_first_rows:
                raise NoTypeUriInTableError
            else:
                raise TypeUriNotInFirstRowError
        headers.pop('typeURI')
        for row in table_data[1:]:
            instance = self.create_instance_from_row(
                headers=headers, row=row,  convert_datetimes_to_dates=convert_datetimes_to_dates,
                convert_strings_to_types=convert_strings_to_types, empty_string_equals_none=empty_string_equals_none)
            instances.append(instance)

        return instances

    def create_instance_from_row(self, headers: Dict, row: Dict, convert_datetimes_to_dates: bool = False,
                                 convert_strings_to_types: bool = False, empty_string_equals_none: bool = False
                                 ) -> OTLObject:
        instance = dynamic_create_instance_from_uri(row['typeURI'], model_directory=self.model_directory)
        for header in headers:
            try:
                value = row.get(header)
                if value is None:
                    continue
                if isinstance(value, float) and math.isnan(value):
                    continue
                if empty_string_equals_none and value == '':
                    continue
                if convert_datetimes_to_dates:
                    attr = self.dotnotation_helper.get_attribute_by_dotnotation_instance(
                        instance_or_attribute=instance, dotnotation=header)
                    if attr.field is DateField:
                        if isinstance(value, datetime.datetime):
                            value = value.date()
                        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], datetime.datetime):
                            value = [v.date() for v in value]

                self.dotnotation_helper.set_attribute_by_dotnotation_instance(
                    instance_or_attribute=instance, dotnotation=header, value=value,
                    convert=convert_strings_to_types)
            except AttributeError as e:
                asset_id = row['assetId.identificator']
                raise AttributeError(f'{header} for asset {asset_id}') from e
        return instance

    @classmethod
    def transform_list_of_dicts_to_2d_sequence(cls, list_of_dicts: List[Dict],
                                               empty_string_equals_none: bool = False) -> List[List]:
        """Returns a 2d array from a list of dicts, where each dict is a row, and the first row is the header"""
        # TODO also try this with numpy arrays to see what is faster

        sorted_headers = cls._sort_headers(list_of_dicts[0])
        matrix = [[cls._get_item_from_dict(input_dict=d, item=header, empty_string_equals_none=empty_string_equals_none)
                   for header in sorted_headers] for d in list_of_dicts[1:]]
        matrix.insert(0, sorted_headers)
        return matrix

    @classmethod
    def transform_2d_sequence_to_list_of_dicts(cls, two_d_sequence: List[List],
                                               empty_string_equals_none: bool = False) -> List[Dict]:
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
    def _get_item_from_dict(cls, input_dict: dict, item: str, empty_string_equals_none: bool) -> Any:
        value = input_dict.get(item)
        return '' if empty_string_equals_none and value is None else value

    def _turn_value_to_string(self, value: Any) -> str:
        if isinstance(value, list):
            if isinstance(value[0], list):
                raise DotnotationListOfListError('Not possible to turn a list of a list into a string')

            str_list = [(str(item) if item is not None else '') for item in value]
            return self.cardinality_separator.join(str_list)
        return value if isinstance(value, str) else str(value)
