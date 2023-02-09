import warnings
from typing import Union, List, Type, Any, Dict

from otlmow_model.BaseClasses.OTLObject import OTLObject
from otlmow_model.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.Helpers.GenericHelper import get_shortened_uri

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.Exceptions.BadTypeWarning import BadTypeWarning


class TableExporter:
    def __init__(self, dotnotation_settings: Dict = None, class_directory: str = 'otlmow_model.Classes',
                 ignore_empty_asset_id: bool = False):
        if class_directory is None:
            class_directory = 'otlmow_model.Classes'
        self.otl_object_ref = self._import_otl_object(class_directory)
        self.relatie_object_ref = self._import_relatie_object(class_directory)

        self.ignore_empty_asset_id = ignore_empty_asset_id

        if dotnotation_settings is None:
            dotnotation_settings = {}
        self.settings = dotnotation_settings

        for required_attribute in ['separator', 'cardinality separator', 'cardinality indicator',
                                   'waarde_shortcut_applicable']:
            if required_attribute not in self.settings:
                raise ValueError("The settings are not loaded or don't contain the full dotnotation settings")

        self.master = {}  # holds different "tabs", 1 for each typeURI, or one tab 'single'

    @staticmethod
    def _import_otl_object(class_directory: str) -> Union[Type[OTLObject], None]:
        try:
            py_mod = __import__(name=f'otlmow_model.BaseClasses.OTLObject', fromlist=f'OTLObject')
        except ModuleNotFoundError:
            return None
        class_ = getattr(py_mod, 'OTLObject')
        return class_

    @staticmethod
    def _import_relatie_object(class_directory: str) -> Union[Type[RelatieObject], None]:
        try:
            py_mod = __import__(name=f'{class_directory}.ImplementatieElement.RelatieObject', fromlist=f'RelatieObject')
        except ModuleNotFoundError:
            return None
        class_ = getattr(py_mod, 'RelatieObject')
        return class_

    @staticmethod
    def _sort_headers(headers: List[str]) -> List[str]:
        if headers is None or headers == []:
            return []
        first_three = headers[0:3]
        rest = headers[3:]
        sorted_rest = sorted(rest)
        first_three.extend(sorted_rest)

        return first_three

    def get_data_as_table(self, type_name: str = 'single', values_as_strings: bool = True) -> List[List]:
        if type_name not in self.master:
            raise ValueError(f'There is no available for type name: {type_name}')
        table_data = []
        headers = self._sort_headers(self.master[type_name]['headers'])
        table_data.append(headers)
        for object_dict in self.master[type_name]['data']:
            row = []
            for header in headers:
                if header in object_dict:
                    row.append(self._stringify_value(value=object_dict[header], header=header,
                                                     values_as_strings=values_as_strings))
                else:
                    if values_as_strings:
                        row.append('')
                    else:
                        row.append(None)
            table_data.append(row)
        return table_data

    def fill_master_dict(self, list_of_objects: List[Union[OTLObject, RelatieObject]],
                         split_per_type: bool = True) -> None:
        identificator_key = 'assetId.identificator'.replace('.', self.settings['separator'])
        toegekend_door_key = 'assetId.toegekendDoor'.replace('.', self.settings['separator'])
        for otl_object in list_of_objects:
            if not isinstance(otl_object, self.otl_object_ref) and not isinstance(otl_object, self.relatie_object_ref):
                warnings.warn(
                    BadTypeWarning(f'{otl_object} is not of type AIMObject or RelatieObject. Ignoring this object'))
                continue

            if not self.ignore_empty_asset_id:
                if otl_object.assetId.identificator is None or otl_object.assetId.identificator == '':
                    raise ValueError(f'{otl_object} does not have an asset-id.')

            short_uri = get_shortened_uri(otl_object.typeURI)
            if not split_per_type:
                short_uri = 'single'
            if short_uri not in self.master:
                self.master[short_uri] = {'headers': ['typeURI', identificator_key, toegekend_door_key],
                                          'data': []}
            data_dict = {
                'typeURI': otl_object.typeURI,
                identificator_key: otl_object.assetId.identificator,
                toegekend_door_key: otl_object.assetId.toegekendDoor
            }

            for k, v in DotnotationHelper.list_attributes_and_values_by_dotnotation(
                    asset=otl_object, waarde_shortcut=self.settings['waarde_shortcut_applicable'],
                    cardinality_indicator=self.settings['cardinality indicator'], separator=self.settings['separator']):
                if k in [identificator_key, toegekend_door_key]:
                    continue
                if k not in self.master[short_uri]['headers']:
                    self.master[short_uri]['headers'].append(k)
                data_dict[k] = v

            self.master[short_uri]['data'].append(data_dict)

    def _stringify_value(self, value, header: str = '', values_as_strings: bool = True) -> Any:
        if value is None:
            if values_as_strings:
                return ''
            else:
                return None
        if isinstance(value, list):
            if not value:
                if values_as_strings:
                    return ''
                else:
                    return 'None'
            if isinstance(value[0], list):
                raise ValueError(f'Not possible to make table exports with a list in a list value {header}')
            list_string = ''
            for list_item in value:
                if not isinstance(list_item, str):
                    if list_item is not None:
                        list_string += str(list_item)
                else:
                    list_string += list_item
                list_string += self.settings['cardinality separator']
            return list_string[:-1]
        if values_as_strings and not isinstance(value, str):
            return str(value)
        return value
