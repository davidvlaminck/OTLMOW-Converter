import copy
import warnings
from pathlib import Path
from typing import Union, List

from otlmow_model.Classes.ImplementatieElement.AIMObject import AIMObject
from otlmow_model.Classes.ImplementatieElement.RelatieObject import RelatieObject

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.Exceptions.BadTypeWarning import BadTypeWarning
from otlmow_converter.HelperFunctions import get_ns_and_name_from_uri, get_shortened_uri


class TableExporter:
    def __init__(self, dotnotation_settings=None, class_directory: str = 'otlmow_model.Classes',
                 ignore_empty_asset_id: bool = False):
        if class_directory is None:
            class_directory = 'otlmow_model.Classes'
        self.aim_object_ref = self._import_aim_object(class_directory)
        self.relatie_object_ref = self._import_relatie_object(class_directory)

        self.ignore_empty_asset_id = ignore_empty_asset_id

        if dotnotation_settings is None:
            dotnotation_settings = {}
        self.settings = dotnotation_settings

        for required_attribute in ['separator', 'cardinality separator', 'cardinality indicator', 'waarde_shortcut_applicable']:
            if required_attribute not in self.settings:
                raise ValueError("The settings are not loaded or don't contain the full dotnotation settings")

        self.master = {}  # holds different "tabs", 1 for each typeURI

    #
    # def _export_multiple_csv_files(self, list_of_objects: list, file_location: Path = None, delimiter: str = ''):
    #     if list_of_objects is None:
    #         list_of_objects = []
    #
    #     dir_location = file_location.parent
    #     filename = file_location.name
    #
    #     types = set(map(lambda x: x.typeURI, list_of_objects))
    #     for object_type in types:
    #         filtered_objects = list(filter(lambda x: x.typeURI == object_type, list_of_objects))
    #         ns, name = get_ns_and_name_from_uri(object_type)
    #         shortened_uri = ns + '_' + name
    #
    #         specific_filename = filename.split('.')[0] + '_' + shortened_uri + '.' + filename.split('.')[1]
    #
    #         csv_data = self._create_data_from_objects(filtered_objects)
    #         csv_data_lines = self.create_data_lines_from_data(csv_data, delimiter)
    #         self.write_file(file_location=Path(dir_location) / specific_filename, data=csv_data_lines)
    #
    # def _create_data_from_objects(self, list_of_objects: list) -> [[str]]:
    #     self.csv_data = []
    #     if list_of_objects is None or list_of_objects == []:
    #         raise ValueError('There is no data to export to a csv file')
    #
    #     self.csv_headers = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor']
    #
    #     for asset_object in list_of_objects:
    #         if isinstance(asset_object, self.aimobject_ref) or isinstance(asset_object, self.relatieobject_ref):
    #             if asset_object.assetId.identificator is None or asset_object.assetId.identificator == '':
    #                 raise ValueError(
    #                     f'Not possible to export AIM Objects without a valid assetId.identificator. '
    #                     f'This is missing for asset_object : {asset_object}')
    #
    #             self.csv_data.append(self._create_csv_row_for_AIMObject(asset_object))
    #
    #     self.csv_headers = self.adjust_dotnotation_by_settings(headers=self.csv_headers, settings=self.settings)
    #     self.csv_headers = self.sort_headers(self.csv_headers)
    #     self.csv_data.insert(0, self.csv_headers)
    #
    #     csv_data = self.append_with_nones(self.csv_data)
    #
    #     return csv_data
    #
    # def _create_csv_row_for_AIMObject(self, aim_object):
    #     values_list = [aim_object.typeURI, aim_object.assetId.identificator, aim_object.assetId.toegekendDoor]
    #     while len(values_list) < len(self.csv_headers):
    #         values_list.append(None)
    #
    #     for attribute, value in DotnotationHelper.list_attributes_and_values_by_dotnotation(
    #             asset=aim_object,
    #             waarde_shortcut=self.settings['dotnotation']['waarde_shortcut_applicable']):
    #         if attribute in self.csv_headers[1:3]:
    #             continue
    #
    #         if attribute not in self.csv_headers:
    #             index = self.find_sorted_header_index(attribute)
    #             self.csv_headers.insert(index, attribute)
    #             while len(values_list) < len(self.csv_headers):
    #                 values_list.insert(index, None)
    #                 for data_row in self.csv_data:
    #                     if len(data_row) > 0:
    #                         data_row.insert(index, None)
    #
    #         index = self.csv_headers.index(attribute)
    #
    #         if attribute.count('[]') > 1:
    #             values_list[index] = '<unable to write a nested list in a csv>'
    #         elif isinstance(value, list):
    #             value = self.fix_cardinality_value(aim_object, attribute)
    #             values_list[index] = value
    #         else:
    #             values_list[index] = value
    #
    #     return values_list
    #
    # @staticmethod
    # def append_with_nones(csv_data):
    #     header_len = len(csv_data[0])
    #
    #     for row in csv_data[1:]:
    #         while len(row) < header_len:
    #             row.append(None)
    #
    #     return csv_data
    #
    # @staticmethod
    # def adjust_dotnotation_by_settings(headers, settings):
    #     for index, header in enumerate(headers):
    #         headers[index] = header.replace('.', settings['dotnotation']['separator']) \
    #             .replace('[]', settings['dotnotation']['cardinality indicator'])
    #     return headers
    #
    # def create_data_lines_from_data(self, csv_data, delimiter):
    #     csv_data_lines = []
    #     for index, row in enumerate(csv_data):
    #         row = self.stringify_list(row, self.settings['dotnotation']['cardinality separator'])
    #         csv_data_lines.append(delimiter.join(row))
    #     return csv_data_lines
    #
    # @staticmethod
    # def stringify_list(row: list, cardinality_seperator: str = '|'):
    #     for index, item in enumerate(row):
    #         if item is None:
    #             row[index] = ''
    #         else:
    #             if isinstance(item, list):
    #                 if len(item) == 0:
    #                     row[index] = ''
    #                 else:
    #                     item_string = ''
    #                     for item_element in item:
    #                         if item_element is None:
    #                             item_string += cardinality_seperator
    #                         elif isinstance(item_element, str):
    #                             item_string += item_element + cardinality_seperator
    #                         else:
    #                             item_string += str(item_element) + cardinality_seperator
    #                     item_string = item_string[:-1]
    #                     row[index] = item_string
    #             else:
    #                 try:
    #                     row[index] = str(item)
    #                 except TypeError:
    #                     row[index] = ''
    #     return row
    #
    # @staticmethod
    # def write_file(file_location, data):
    #     try:
    #         with open(file_location, "w") as file:
    #             for line in data:
    #                 file.writelines(line + '\n')
    #     except Exception as ex:
    #         raise ex
    #
    #
    # def fix_cardinality_value(self, aim_object, attribute):
    #     actual_attributes = DotnotationHelper.get_attributes_by_dotnotation(instance_or_attribute=aim_object,
    #                                                                         dotnotation=attribute,
    #                                                                         separator='.',
    #                                                                         cardinality_indicator='[]',
    #                                                                         waarde_shortcut_applicable=True)
    #
    #     if actual_attributes is None:
    #         return []
    #     if not isinstance(actual_attributes, list):
    #         return actual_attributes.waarde
    #
    #     if self.settings['dotnotation']['waarde_shortcut_applicable']:
    #         first_attr = actual_attributes[0]
    #         if first_attr.field.waarde_shortcut_applicable:
    #             values_list = []
    #             for actual_attribute in actual_attributes:
    #                 if actual_attribute.waarde is not None:
    #                     if isinstance(actual_attribute.waarde, list):
    #                         new_list = []
    #                         for item in actual_attribute.waarde:
    #                             new_list.append(item.waarde)
    #                         values_list.append(new_list)
    #                     else:
    #                         values_list.append(actual_attribute.waarde.waarde)
    #                 else:
    #                     values_list.append(None)
    #         else:
    #             values_list = list(map(lambda x: x.waarde, actual_attributes))
    #     else:
    #         values_list = list(map(lambda x: x.waarde, actual_attributes))
    #     return values_list
    #
    @staticmethod
    def _import_aim_object(class_directory):
        try:
            # TODO: check https://stackoverflow.com/questions/2724260/why-does-pythons-import-require-fromlist
            py_mod = __import__(name=f'{class_directory}.ImplementatieElement.AIMObject', fromlist=f'AIMObject')
        except ModuleNotFoundError:
            return None
        class_ = getattr(py_mod, 'AIMObject')
        return class_

    @staticmethod
    def _import_relatie_object(class_directory):
        try:
            # TODO: check https://stackoverflow.com/questions/2724260/why-does-pythons-import-require-fromlist
            py_mod = __import__(name=f'{class_directory}.ImplementatieElement.RelatieObject', fromlist=f'RelatieObject')
        except ModuleNotFoundError:
            return None
        class_ = getattr(py_mod, 'RelatieObject')
        return class_

    @staticmethod
    def sort_headers(headers):
        if headers is None or headers == []:
            return headers
        first_three = headers[0:3]
        rest = headers[3:]
        sorted_rest = sorted(rest)
        first_three.extend(sorted_rest)

        return first_three

    def get_data_as_table(self, type_name='single', values_as_strings=True):
        if type_name not in self.master:
            raise ValueError(f'There is no available for type name: {type_name}')
        table_data = []
        headers = self.sort_headers(self.master[type_name]['headers'])
        table_data.append(headers)
        for object_dict in self.master[type_name]['data']:
            row = []
            for header in headers:
                if header in object_dict:
                    row.append(self._stringify_value(object_dict[header], header=header,
                                                     values_as_strings=values_as_strings))
                else:
                    row.append(None)
            table_data.append(row)
        return table_data

    def fill_master_dict(self, list_of_objects: List[Union[AIMObject, RelatieObject]], split_per_type: bool = True):
        for otl_object in list_of_objects:
            if not isinstance(otl_object, self.aim_object_ref) and not isinstance(otl_object, self.relatie_object_ref):
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
                self.master[short_uri] = {'headers': ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor'],
                                          'data': []}
            data_dict = {
                'typeURI': otl_object.typeURI,
                'assetId.identificator': otl_object.assetId.identificator,
                'assetId.toegekendDoor': otl_object.assetId.toegekendDoor
            }

            for k, v in DotnotationHelper.list_attributes_and_values_by_dotnotation(otl_object,
                                                                                    waarde_shortcut=self.settings[
                                                                                        'waarde_shortcut_applicable']):
                if k in ['assetId.identificator', 'assetId.toegekendDoor']:
                    continue
                if k not in self.master[short_uri]['headers']:
                    self.master[short_uri]['headers'].append(k)
                data_dict[k] = v

            self.master[short_uri]['data'].append(data_dict)

    def _stringify_value(self, value, header: str = '', values_as_strings: bool = True):
        if value is None:
            return None
        if isinstance(value, list):
            if value == []:
                return None
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
