import warnings
from asyncio import sleep
from pathlib import Path
from typing import Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_model.OtlmowModel.Helpers.GenericHelper import get_shortened_uri
from otlmow_converter.DotnotationDict import DotnotationDict
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.Exceptions.BadTypeWarning import BadTypeWarning
from otlmow_converter.Exceptions.MissingHeaderError import MissingHeaderError
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
    def _sort_headers(cls, headers: dict, separator: str = SEPARATOR) -> Iterable[str]:
        if headers is None or not headers:
            return []
        headers.pop('typeURI')
        has_agent_headers = False
        has_asset_headers = False
        asset_id_key = 'assetId.identificator'.replace('.', separator)
        asset_toegekend_key = 'assetId.toegekendDoor'.replace('.', separator)
        agent_id_key = 'agentId.identificator'.replace('.', separator)
        agent_toegekend_key = 'agentId.toegekendDoor'.replace('.', separator)

        if asset_id_key in headers:
            headers.pop(asset_id_key)
            has_asset_headers = True
        if asset_toegekend_key in headers:
            headers.pop(asset_toegekend_key)
            has_asset_headers = True
        if agent_id_key in headers:
            headers.pop(agent_id_key)
            has_agent_headers = True
        if agent_toegekend_key in headers:
            headers.pop(agent_toegekend_key)
            has_agent_headers = True
        sorted_list = ['typeURI']
        if has_asset_headers:
            sorted_list.extend((asset_id_key, asset_toegekend_key))
        if has_agent_headers:
            sorted_list.extend((agent_id_key, agent_toegekend_key))

        sorted_rest = sorted(headers)
        sorted_list.extend(sorted_rest)

        return sorted_list

    @classmethod
    def get_single_table_from_data(cls, list_of_objects: Iterable[OTLObject],
                                   separator: str = SEPARATOR, cardinality_separator: str = CARDINALITY_SEPARATOR,
                                   cardinality_indicator: str = CARDINALITY_INDICATOR,
                                   waarde_shortcut: bool = WAARDE_SHORTCUT,
                                   cast_list: bool = False, cast_datetime: bool = False,
                                   allow_non_otl_conform_attributes: bool = True,
                                   warn_for_non_otl_conform_attributes: bool = True,
                                   allow_empty_asset_id: bool = True) -> list[dict]:
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

            if not allow_empty_asset_id:
                if otl_object.typeURI == 'http://purl.org/dc/terms/Agent':
                    if otl_object.agentId.identificator is None or otl_object.agentId.identificator == '':
                        raise ValueError(f'{otl_object} does not have a valid agentId.')
                elif otl_object.assetId.identificator is None or otl_object.assetId.identificator == '':
                    raise ValueError(f'{otl_object} does not have a valid assetId.')

            data_dict = DotnotationDictConverter.to_dict(
                otl_object, separator=separator, cardinality_separator=cardinality_separator,
                cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cast_list=cast_list, cast_datetime=cast_datetime,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

            data_dict['typeURI'] = otl_object.typeURI

            for k, v in data_dict.items():
                if k not in header_dict:
                    header_dict[k] = header_count
                    header_count += 1

            list_of_dicts.append(data_dict)
        list_of_dicts.insert(0, header_dict)
        return list_of_dicts

    @classmethod
    async def get_single_table_from_data_async(cls, list_of_objects: Iterable[OTLObject],
                                         separator: str = SEPARATOR, cardinality_separator: str = CARDINALITY_SEPARATOR,
                                         cardinality_indicator: str = CARDINALITY_INDICATOR,
                                         waarde_shortcut: bool = WAARDE_SHORTCUT,
                                         cast_list: bool = False, cast_datetime: bool = False,
                                         allow_non_otl_conform_attributes: bool = True,
                                         warn_for_non_otl_conform_attributes: bool = True,
                                         allow_empty_asset_id: bool = True) -> list[dict]:
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

            if not allow_empty_asset_id:
                if otl_object.typeURI == 'http://purl.org/dc/terms/Agent':
                    if otl_object.agentId.identificator is None or otl_object.agentId.identificator == '':
                        raise ValueError(f'{otl_object} does not have a valid agentId.')
                elif otl_object.assetId.identificator is None or otl_object.assetId.identificator == '':
                    raise ValueError(f'{otl_object} does not have a valid assetId.')

            await sleep(0)
            data_dict = await DotnotationDictConverter.to_dict_async(
                otl_object, separator=separator, cardinality_separator=cardinality_separator,
                cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cast_list=cast_list, cast_datetime=cast_datetime,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

            data_dict['typeURI'] = otl_object.typeURI

            for k, v in data_dict.items():
                if k not in header_dict:
                    header_dict[k] = header_count
                    header_count += 1

            list_of_dicts.append(data_dict)
        list_of_dicts.insert(0, header_dict)
        return list_of_dicts

    @classmethod
    def get_tables_per_type_from_data(cls, sequence_of_objects: Iterable[OTLObject],
                                            values_as_string: bool = False, separator: str = SEPARATOR,
                                            cardinality_separator: str = CARDINALITY_SEPARATOR,
                                            cardinality_indicator: str = CARDINALITY_INDICATOR,
                                            waarde_shortcut: bool = WAARDE_SHORTCUT,
                                            cast_list: bool = False, cast_datetime: bool = False,
                                            allow_non_otl_conform_attributes: bool = True,
                                            warn_for_non_otl_conform_attributes: bool = True,
                                            allow_empty_asset_id: bool = True
                                            ) -> dict[str, list[dict]]:
        """Returns a dictionary with typeURIs as keys and a list of dicts as values, where each dict is a row, and the
        first row is the header"""

        identificator_key = 'assetId.identificator'.replace('.', separator)
        toegekend_door_key = 'assetId.toegekendDoor'.replace('.', separator)

        master_dict = {}

        for otl_object in sequence_of_objects:
            if not hasattr(otl_object, 'typeURI'):
                warnings.warn(BadTypeWarning(f'{otl_object} does not have a typeURI so this can not be instantiated. '
                                             f'Ignoring this object'))
                continue

            if not allow_empty_asset_id:
                if otl_object.typeURI == 'http://purl.org/dc/terms/Agent':
                    if otl_object.agentId.identificator is None or otl_object.agentId.identificator == '':
                        raise ValueError(f'{otl_object} does not have a valid agentId.')
                elif otl_object.assetId.identificator is None or otl_object.assetId.identificator == '':
                    raise ValueError(f'{otl_object} does not have a valid assetId.')

            if otl_object.typeURI == 'http://purl.org/dc/terms/Agent':
                short_uri = 'Agent'
            else:
                short_uri = get_shortened_uri(otl_object.typeURI)

            if short_uri not in master_dict:
                if short_uri == 'Agent':
                    master_dict[short_uri] = [{'typeURI': 0, 'agentId.identificator'.replace('.', separator): 1,
                                               'agentId.toegekendDoor'.replace('.', separator): 2}]
                else:
                    master_dict[short_uri] = [{'typeURI': 0, identificator_key: 1, toegekend_door_key: 2}]
            header_dict = master_dict[short_uri][0]
            header_count = len(header_dict)

            data_dict = DotnotationDictConverter.to_dict(
                otl_object, separator=separator, cardinality_separator=cardinality_separator,
                cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cast_list=cast_list, cast_datetime=cast_datetime,
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
    async def get_tables_per_type_from_data_async(cls, sequence_of_objects: Iterable[OTLObject],
                                            values_as_string: bool = False, separator: str = SEPARATOR,
                                            cardinality_separator: str = CARDINALITY_SEPARATOR,
                                            cardinality_indicator: str = CARDINALITY_INDICATOR,
                                            waarde_shortcut: bool = WAARDE_SHORTCUT,
                                            cast_list: bool = False, cast_datetime: bool = False,
                                            allow_non_otl_conform_attributes: bool = True,
                                            warn_for_non_otl_conform_attributes: bool = True,
                                            allow_empty_asset_id: bool = True
                                            ) -> dict[str, list[dict]]:
        """Returns a dictionary with typeURIs as keys and a list of dicts as values, where each dict is a row, and the
        first row is the header"""
        identificator_key = 'assetId.identificator'.replace('.', separator)
        toegekend_door_key = 'assetId.toegekendDoor'.replace('.', separator)

        master_dict = {}

        for otl_object in sequence_of_objects:
            if not hasattr(otl_object, 'typeURI'):
                warnings.warn(BadTypeWarning(f'{otl_object} does not have a typeURI so this can not be instantiated. '
                                             f'Ignoring this object'))
                continue

            if not allow_empty_asset_id:
                if otl_object.typeURI == 'http://purl.org/dc/terms/Agent':
                    if otl_object.agentId.identificator is None or otl_object.agentId.identificator == '':
                        raise ValueError(f'{otl_object} does not have a valid agentId.')
                elif otl_object.assetId.identificator is None or otl_object.assetId.identificator == '':
                    raise ValueError(f'{otl_object} does not have a valid assetId.')

            if otl_object.typeURI == 'http://purl.org/dc/terms/Agent':
                short_uri = 'Agent'
            else:
                short_uri = get_shortened_uri(otl_object.typeURI)

            if short_uri not in master_dict:
                if short_uri == 'Agent':
                    master_dict[short_uri] = [{'typeURI': 0, 'agentId.identificator'.replace('.', separator): 1,
                                               'agentId.toegekendDoor'.replace('.', separator): 2}]
                else:
                    master_dict[short_uri] = [{'typeURI': 0, identificator_key: 1, toegekend_door_key: 2}]
            header_dict = master_dict[short_uri][0]
            header_count = len(header_dict)

            await sleep(0)
            data_dict = await DotnotationDictConverter.to_dict_async(
                otl_object, separator=separator, cardinality_separator=cardinality_separator,
                cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cast_list=cast_list, cast_datetime=cast_datetime,
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
    def get_data_from_table(cls, table_data: list[dict], model_directory: Path = None,
                                  cast_list: bool = False, cast_datetime: bool = False,
                                  allow_non_otl_conform_attributes: bool = True,
                                  warn_for_non_otl_conform_attributes: bool = True,
                                  waarde_shortcut: bool = WAARDE_SHORTCUT,
                                  separator: str = SEPARATOR,
                                  cardinality_indicator: str = CARDINALITY_INDICATOR,
                                  cardinality_separator: str = CARDINALITY_SEPARATOR) -> list[OTLObject]:
        """Returns a list of OTL objects from a list of dicts, where each dict is a row, and the first row is the
        header"""
        instances = []
        headers, *rows = table_data
        if 'typeURI' not in headers:
            type_uri_in_first_rows = any('typeURI' in row.values() for row in rows)
            if not type_uri_in_first_rows:
                raise NoTypeUriInTableError
            else:
                raise TypeUriNotInFirstRowError
        headers.pop('typeURI')
        for row in rows:
            instance = cls.create_instance_from_row(
                row=row, model_directory=model_directory, cast_list=cast_list, cast_datetime=cast_datetime,
                separator=separator, cardinality_indicator=cardinality_indicator,
                waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
            instances.append(instance)

        return instances

    @classmethod
    async def get_data_from_table_async(cls, table_data: list[dict], model_directory: Path = None,
                                  cast_list: bool = False, cast_datetime: bool = False,
                                  allow_non_otl_conform_attributes: bool = True,
                                  warn_for_non_otl_conform_attributes: bool = True,
                                  waarde_shortcut: bool = WAARDE_SHORTCUT,
                                  separator: str = SEPARATOR,
                                  cardinality_indicator: str = CARDINALITY_INDICATOR,
                                  cardinality_separator: str = CARDINALITY_SEPARATOR) -> list[OTLObject]:
        """Returns a list of OTL objects from a list of dicts, where each dict is a row, and the first row is the
        header"""
        instances = []
        headers, *rows = table_data
        if 'typeURI' not in headers:
            type_uri_in_first_rows = any('typeURI' in row.values() for row in rows)
            if not type_uri_in_first_rows:
                raise NoTypeUriInTableError
            else:
                raise TypeUriNotInFirstRowError
        headers.pop('typeURI')
        for row in rows:
            instance = cls.create_instance_from_row(
                row=row, model_directory=model_directory, cast_list=cast_list, cast_datetime=cast_datetime,
                separator=separator, cardinality_indicator=cardinality_indicator,
                waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
            instances.append(instance)
            await sleep(0)

        return instances

    @classmethod
    def create_instance_from_row(cls, row: DotnotationDict, model_directory: Path = None,
                                       cast_list: bool = False, cast_datetime: bool = False,
                                       allow_non_otl_conform_attributes: bool = True,
                                       warn_for_non_otl_conform_attributes: bool = True,
                                       waarde_shortcut: bool = WAARDE_SHORTCUT,
                                       separator: str = SEPARATOR,
                                       cardinality_indicator: str = CARDINALITY_INDICATOR,
                                       cardinality_separator: str = CARDINALITY_SEPARATOR) -> OTLObject:
        return DotnotationDictConverter.from_dict(
            input_dict=row, model_directory=model_directory, cast_list=cast_list, cast_datetime=cast_datetime,
            separator=separator, cardinality_indicator=cardinality_indicator,
            waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)


    @classmethod
    async def create_instance_from_row_async(cls, row: DotnotationDict, model_directory: Path = None,
                                       cast_list: bool = False, cast_datetime: bool = False,
                                       allow_non_otl_conform_attributes: bool = True,
                                       warn_for_non_otl_conform_attributes: bool = True,
                                       waarde_shortcut: bool = WAARDE_SHORTCUT,
                                       separator: str = SEPARATOR,
                                       cardinality_indicator: str = CARDINALITY_INDICATOR,
                                       cardinality_separator: str = CARDINALITY_SEPARATOR) -> OTLObject:
        return await DotnotationDictConverter.from_dict_async(
            input_dict=row, model_directory=model_directory, cast_list=cast_list, cast_datetime=cast_datetime,
            separator=separator, cardinality_indicator=cardinality_indicator,
            waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

    @classmethod
    def transform_list_of_dicts_to_2d_sequence(cls, list_of_dicts: list[dict], separator: str = SEPARATOR,
                                                     empty_string_equals_none: bool = False) -> list[list]:
        """Returns a 2d array from a list of dicts, where each dict is a row, and the first row is the header"""
        # TODO also try this with numpy arrays to see what is faster

        header_dict, *data_dicts = list_of_dicts
        sorted_headers = cls._sort_headers(header_dict, separator=separator)
        matrix = []
        for d in data_dicts:
            row = [
                cls._get_item_from_dict(
                    input_dict=d,
                    item=header,
                    empty_string_equals_none=empty_string_equals_none,
                )
                for header in sorted_headers
            ]
            matrix.append(row)
        matrix.insert(0, list(sorted_headers))
        return matrix

    @classmethod
    async def transform_list_of_dicts_to_2d_sequence_async(cls, list_of_dicts: list[dict], separator: str = SEPARATOR,
                                                     empty_string_equals_none: bool = False) -> list[list]:
        """Returns a 2d array from a list of dicts, where each dict is a row, and the first row is the header"""
        # TODO also try this with numpy arrays to see what is faster

        header_dict, *data_dicts = list_of_dicts
        sorted_headers = cls._sort_headers(header_dict, separator=separator)
        await sleep(0)
        matrix = []
        for d in data_dicts:
            row = []
            for header in sorted_headers:
                row.append(cls._get_item_from_dict(input_dict=d, item=header, empty_string_equals_none=empty_string_equals_none))
                await sleep(0)
            matrix.append(row)
        matrix.insert(0, list(sorted_headers))
        return matrix

    @classmethod
    def transform_2d_sequence_to_list_of_dicts(cls, two_d_sequence: list[list],
                                                     empty_string_equals_none: bool = False) -> list[dict]:
        """Returns a list of dicts from a 2d array, where each dict is a row, and the first row is the header"""
        # TODO also try this with numpy arrays to see what is faster
        header_row, *data_rows = two_d_sequence
        header_dict = {header: index for index, header in enumerate(header_row)}

        list_of_dicts = [header_dict]
        for row in data_rows:
            data_dict = {}
            for header, index in header_dict.items():
                value = row[index]
                if value is None:
                    continue
                if header is None:
                    raise MissingHeaderError(f'Header is None at column {index+1}')
                if empty_string_equals_none and value == '':
                    continue
                if value == 'true':
                    value = True
                if value == 'false':
                    value = False
                data_dict[str(header)] = value
            if not data_dict:
                continue
            list_of_dicts.append(data_dict)

        return list_of_dicts

    @classmethod
    async def transform_2d_sequence_to_list_of_dicts_async(cls, two_d_sequence: list[list],
                                                     empty_string_equals_none: bool = False) -> list[dict]:
        """Returns a list of dicts from a 2d array, where each dict is a row, and the first row is the header"""
        # TODO also try this with numpy arrays to see what is faster
        header_row, *data_rows = two_d_sequence
        header_dict = {header: index for index, header in enumerate(header_row)}

        list_of_dicts = [header_dict]
        for row in data_rows:
            data_dict = {}
            for header, index in header_dict.items():
                value = row[index]
                if value is None:
                    continue
                if header is None:
                    raise MissingHeaderError(f'Header is None at column {index + 1}')
                if empty_string_equals_none and value == '':
                    continue
                if value == 'true':
                    value = True
                if value == 'false':
                    value = False
                data_dict[str(header)] = value
            if not data_dict:
                continue
            list_of_dicts.append(data_dict)
            await sleep(0)

        return list_of_dicts

    @classmethod
    def _get_item_from_dict(cls, input_dict: dict, item: str, empty_string_equals_none: bool) -> object:
        value = input_dict.get(item)
        return '' if empty_string_equals_none and value is None else value

