import datetime
import math
import warnings
from pathlib import Path
from typing import Dict, Any, Iterable, List

from otlmow_model.OtlmowModel.BaseClasses.DateField import DateField
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.Helpers.GenericHelper import get_shortened_uri

from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
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


    @classmethod
    def get_single_table_from_data(cls, list_of_objects: Iterable[OTLObject], values_as_string: bool = False,
                                   separator: str = SEPARATOR, cardinality_separator: str = CARDINALITY_SEPARATOR,
                                   cardinality_indicator: str = CARDINALITY_INDICATOR,
                                   waarde_shortcut: bool = WAARDE_SHORTCUT,
                                   list_as_string: bool = False, datetime_as_string: bool = False,
                                   allow_non_otl_conform_attributes: bool = True,
                                   warn_for_non_otl_conform_attributes: bool = True,
                                   allow_empty_asset_id: bool = True
                                   ) -> List[Dict]:
        """Returns a list of dicts, where each dict is a row, and the first row is the header"""
        identificator_key = 'assetId.identificator'.replace('.', separator)
        toegekend_door_key = 'assetId.toegekendDoor'.replace('.', separator)

        list_of_dicts = []
        header_dict = {'typeURI': 0, identificator_key: 1, toegekend_door_key: 2}
        header_count = 3

        for otl_object in list_of_objects:
            if not hasattr(otl_object, 'typeURI'):
                warnings.warn(BadTypeWarning(f'{otl_object} does not have a typeURI so this can not be instantiated. '
                                             f'Ignoring this object'))
                continue

            if not allow_empty_asset_id and (otl_object.assetId.identificator is None
                                                   or otl_object.assetId.identificator == ''):
                raise ValueError(f'{otl_object} does not have a valid assetId.')

            data_dict = DotnotationDictConverter.to_dict(
                otl_object, separator=separator, cardinality_separator=cardinality_separator,
                cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cast_list=list_as_string, cast_datetime=datetime_as_string,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

            data_dict['typeURI'] = otl_object.typeURI

            for k, v in data_dict.items():
                if k not in header_dict:
                    header_dict[k] = header_count
                    header_count += 1
                if values_as_string and not isinstance(v, str):
                    data_dict[k] = str(v)

            list_of_dicts.append(data_dict)
        list_of_dicts.insert(0, header_dict)
        return list_of_dicts

    @classmethod
    def get_tables_per_type_from_data(cls, list_of_objects: Iterable[OTLObject], values_as_string: bool = False,
                                      separator: str = SEPARATOR, cardinality_separator: str = CARDINALITY_SEPARATOR,
                                      cardinality_indicator: str = CARDINALITY_INDICATOR,
                                      waarde_shortcut: bool = WAARDE_SHORTCUT,
                                      list_as_string: bool = False, datetime_as_string: bool = False,
                                      allow_non_otl_conform_attributes: bool = True,
                                      warn_for_non_otl_conform_attributes: bool = True,
                                      allow_empty_asset_id: bool = True
                                      ) -> Dict[str, List[Dict]]:
        """Returns a dictionary with typeURIs as keys and a list of dicts as values, where each dict is a row, and the
        first row is the header"""
        identificator_key = 'assetId.identificator'.replace('.', separator)
        toegekend_door_key = 'assetId.toegekendDoor'.replace('.', separator)

        master_dict = {}

        for otl_object in list_of_objects:
            if not hasattr(otl_object, 'typeURI'):
                warnings.warn(BadTypeWarning(f'{otl_object} does not have a typeURI so this can not be instantiated. '
                                             f'Ignoring this object'))
                continue

            if not allow_empty_asset_id and (otl_object.assetId.identificator is None or
                                                   otl_object.assetId.identificator == ''):
                raise ValueError(f'{otl_object} does not have a valid assetId.')

            short_uri = get_shortened_uri(otl_object.typeURI)
            if short_uri not in master_dict:
                master_dict[short_uri] = [{'typeURI': 0, identificator_key: 1, toegekend_door_key: 2}]
            header_dict = master_dict[short_uri][0]
            header_count = len(header_dict)

            data_dict = DotnotationDictConverter.to_dict(
                otl_object, separator=separator, cardinality_separator=cardinality_separator,
                cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cast_list=list_as_string, cast_datetime=datetime_as_string,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

            data_dict['typeURI'] = otl_object.typeURI

            for k, v in data_dict.items():
                if k not in header_dict:
                    header_dict[k] = header_count
                    header_count += 1
                if values_as_string and not isinstance(v, str):
                    data_dict[k] = str(v)

            master_dict[short_uri].append(data_dict)

        return master_dict

    @classmethod
    def get_data_from_table(cls, table_data: List[Dict], empty_string_equals_none: bool = False,
                            convert_strings_to_types: bool = False, convert_datetimes_to_dates: bool = False,
                            list_as_string: bool=True, model_directory: Path = None) -> List[OTLObject]:
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
            instance = cls.create_instance_from_row(
                row=row, convert_datetimes_to_dates=convert_datetimes_to_dates,
                convert_strings_to_types=convert_strings_to_types, empty_string_equals_none=empty_string_equals_none,
                model_directory=model_directory, list_as_string=list_as_string)
            instances.append(instance)

        return instances

    @classmethod
    def create_instance_from_row(cls,row: Dict, convert_datetimes_to_dates: bool = False, list_as_string: bool=True,
                                 convert_strings_to_types: bool = False, empty_string_equals_none: bool = False,
                                 model_directory: Path = None) -> OTLObject:
        return DotnotationDictConverter.from_dict(input_dict=row, model_directory=model_directory,
                                                  all_types_as_string=convert_strings_to_types,
                                                  cast_list=list_as_string)

    @classmethod
    def transform_list_of_dicts_to_2d_sequence(cls, list_of_dicts: List[Dict],
                                               empty_string_equals_none: bool = False) -> List[List]:
        """Returns a 2d array from a list of dicts, where each dict is a row, and the first row is the header"""
        # TODO also try this with numpy arrays to see what is faster

        sorted_headers = cls._sort_headers(list_of_dicts[0])
        matrix = [[cls._get_item_from_dict(input_dict=d, item=header, empty_string_equals_none=empty_string_equals_none)
                   for header in sorted_headers] for d in list_of_dicts[1:]]
        matrix.insert(0, list(sorted_headers))
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
