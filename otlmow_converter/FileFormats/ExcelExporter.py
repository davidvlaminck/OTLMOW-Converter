import copy
from pathlib import Path
from typing import Dict

import pandas
from numpy import nan
from otlmow_model.Classes.ImplementatieElement.AIMObject import AIMObject
from pandas import DataFrame

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.FileFormats.TableExporter import TableExporter


class ExcelExporter:
    def __init__(self, settings=None, class_directory: str = None, ignore_empty_asset_id: bool = False):
        self.aimobject_ref = self.import_aimobject(class_directory)

        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        xls_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'xls'), None)
        if xls_settings is None:
            raise ValueError("Unable to find xls in file formats settings")

        self.settings = xls_settings
        self.headers = []
        self.data: Dict[str, DataFrame] = {}
        self.objects = []
        self.csv_headers = []
        self.csv_data = []

        self.table_exporter = TableExporter(dotnotation_settings=xls_settings['dotnotation'],
                                            class_directory=class_directory,
                                            ignore_empty_asset_id=ignore_empty_asset_id)

    def export_to_file(self, filepath: Path = None, list_of_objects: list = None, **kwargs):
        self.create_dataframe_dict_from_objects(list_of_objects=list_of_objects)

        if filepath is None:
            raise ValueError(f'Can not write a file to: {filepath}')

        with pandas.ExcelWriter(filepath) as writer:
            for k, df in self.data.items():
                df.to_excel(writer, sheet_name=k, index=False)

    @staticmethod
    def adjust_dotnotation_by_settings(headers, settings):
        for index, header in enumerate(headers):
            headers[index] = header.replace('.', settings['dotnotation']['separator']) \
                .replace('[]', settings['dotnotation']['cardinality indicator'])
        return headers

    @staticmethod
    def write_file(file_location, data):
        try:
            with open(file_location, "w") as file:
                for line in data:
                    file.writelines(line + '\n')
        except Exception as ex:
            raise ex

    def fix_cardinality_value(self, aim_object, attribute):
        actual_attributes = DotnotationHelper.get_attributes_by_dotnotation(instance_or_attribute=aim_object,
                                                                            dotnotation=attribute,
                                                                            separator='.',
                                                                            cardinality_indicator='[]',
                                                                            waarde_shortcut_applicable=False)

        if actual_attributes is None:
            return []
        if not isinstance(actual_attributes, list):
            return actual_attributes.waarde

        if self.settings['dotnotation']['waarde_shortcut_applicable']:
            first_attr = actual_attributes[0]
            if first_attr.field.waarde_shortcut_applicable:
                values_list = []
                for actual_attribute in actual_attributes:
                    if actual_attribute.waarde is not None:
                        values_list.append(actual_attribute.waarde.waarde)
                    else:
                        values_list.append(None)
            else:
                values_list = list(map(lambda x: x.waarde, actual_attributes))
        else:
            values_list = list(map(lambda x: x.waarde, actual_attributes))
        return values_list

    @staticmethod
    def import_aimobject(class_directory):
        try:
            # TODO: check https://stackoverflow.com/questions/2724260/why-does-pythons-import-require-fromlist
            py_mod = __import__(name=f'{class_directory}.ImplementatieElement.AIMObject', fromlist=f'AIMObject')
        except ModuleNotFoundError:
            return None
        class_ = getattr(py_mod, 'AIMObject')
        return class_

    def create_dataframe_dict_from_objects(self, list_of_objects: [AIMObject]):
        for otl_object in list_of_objects:
            type_uri = otl_object.typeURI
            short_uri = type_uri.split('/ns/')[1].split('#')[1]
            if short_uri not in self.data:
                self.data[short_uri] = DataFrame()
            d = {}

            # TODO check if assetId.identificator is empty is a problem for Davie or not

            for k, v in DotnotationHelper.list_attributes_and_values_by_dotnotation(otl_object):
                if self.settings['dotnotation']['cardinality indicator'] in k:
                    string_list = []
                    for item in v:
                        if not isinstance(item, str):
                            item = str(item)
                        string_list.append(item)
                    d[k] = self.settings['dotnotation']['cardinality separator'].join(string_list)
                else:
                    d[k] = v

            if 'typeURI' not in d:
                d['typeURI'] = otl_object.typeURI
            if 'assetId.identificator' not in d:
                d['assetId.identificator'] = None
            # if 'assetId.toegekendDoor' not in d:
            #     d['assetId.toegekendDoor'] = None

            df = DataFrame(d, index=[self.data[short_uri].shape[0]])

            self.data[short_uri] = pandas.concat([self.data[short_uri], df])

        self.fix_headers_order_and_replace_nan_with_none(self.data)

    @staticmethod
    def fix_headers_order_and_replace_nan_with_none(data):
        fixed_first_headers = ['typeURI', 'assetId.identificator', 'assetId.toegekendDoor']
        for k, df in data.items():
            headers = []
            headers.extend(fixed_first_headers)
            for fixed_header in fixed_first_headers:
                if fixed_header not in df.columns:
                    headers.remove(fixed_header)

            for col in df.columns:
                if col in fixed_first_headers:
                    continue
                headers.append(col)

            if 'geometry' in headers:
                headers.remove('geometry')
                headers.append('geometry')

            data[k] = df[headers].replace({nan: None})


