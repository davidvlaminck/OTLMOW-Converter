from pathlib import Path

from openpyxl import Workbook

from otlmow_converter.FileFormats.TableExporter import TableExporter


class ExcelExporter:
    def __init__(self, settings=None, class_directory: str = None, ignore_empty_asset_id: bool = False):

        if settings is None:
            settings = {}
        self.settings = settings

        if 'file_formats' not in self.settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        xls_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'xls'), None)
        if xls_settings is None:
            raise ValueError("Unable to find xls in file formats settings")

        self.settings = xls_settings

        self.table_exporter = TableExporter(dotnotation_settings=xls_settings['dotnotation'],
                                            class_directory=class_directory,
                                            ignore_empty_asset_id=ignore_empty_asset_id)

    def export_to_file(self, filepath: Path = None, list_of_objects: list = None, **kwargs):
        self.table_exporter.fill_master_dict(list_of_objects=list_of_objects, split_per_type=True)
        self._write_file(file_location=filepath)

        return

    def _write_file(self, file_location: Path):
        wb = Workbook()
        if len(self.table_exporter.master.keys()) == 0:
            raise ValueError('There are no asset data to export to Excel')
        for class_name in self.table_exporter.master:
            self._create_sheet_by_name(wb, class_name)
        wb.remove(wb['Sheet'])
        wb.save(file_location)

    def _create_sheet_by_name(self, wb: Workbook, class_name: str):
        if len(self.table_exporter.master[class_name]['data']) == 0:
            return

        asset_data_table = self.table_exporter.get_data_as_table(class_name, values_as_strings=False)
        sheet = wb.create_sheet(class_name)
        for row_nr, row in enumerate(asset_data_table):
            for col_nr, col in enumerate(row):
                sheet.cell(row=row_nr + 1, column=col_nr + 1).value = col
