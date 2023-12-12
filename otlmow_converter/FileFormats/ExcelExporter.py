from pathlib import Path
from typing import List

from openpyxl import Workbook

from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter


class ExcelExporter:
    def __init__(self, settings=None, model_directory: Path = None, ignore_empty_asset_id: bool = False):

        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        xls_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'xls'), None)
        if xls_settings is None:
            raise ValueError("Unable to find xls in file formats settings")

        self.settings = xls_settings

        self.dotnotation_table_converter = DotnotationTableConverter()
        self.dotnotation_table_converter.load_settings(xls_settings['dotnotation'])

    def export_to_file(self, filepath: Path = None, list_of_objects: list = None, **kwargs):
        table_dict = self.dotnotation_table_converter.get_tables_per_type_from_data(
            list_of_objects=list_of_objects, values_as_string=True)

        wb = Workbook(write_only=True)
        if not list_of_objects:
            raise ValueError('There are no asset data to export to Excel')
        for class_name in table_dict:
            self._create_sheet_by_name(wb, class_name=class_name, table_data=table_dict[class_name])
        wb.save(filepath)

    def _create_sheet_by_name(self, wb: Workbook, class_name: str, table_data: List[dict]):
        if not table_data:
            return

        data = self.dotnotation_table_converter.transform_list_of_dicts_to_2d_sequence(
            list_of_dicts=table_data, empty_string_equals_none=True)

        sheet = wb.create_sheet(class_name)
        for row in data:
            sheet.append(row)
