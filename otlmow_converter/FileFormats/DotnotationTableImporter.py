import importlib
import logging
import sys
from pathlib import Path
from typing import Union, List, Type, Dict

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.Exceptions.NoTypeUriInExcelTabError import NoTypeUriInExcelTabError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError


class DotnotationTableImporter:
    def __init__(self, dotnotation_settings: Dict = None, model_directory: Path = None,
                 ignore_empty_asset_id: bool = False):

        if model_directory is None:
            import otlmow_model
            otlmow_path = otlmow_model.__path__
            self.model_directory = Path(otlmow_path._path[0])
        else:
            self.model_directory = model_directory

        self.otl_object_ref = self._import_otl_object()

        self.ignore_empty_asset_id = ignore_empty_asset_id

        if dotnotation_settings is None:
            dotnotation_settings = {}
        self.settings = dotnotation_settings

        for required_attribute in ['separator', 'cardinality_separator', 'cardinality_indicator',
                                   'waarde_shortcut']:
            if required_attribute not in self.settings:
                raise ValueError("The settings are not loaded or don't contain the full dotnotation settings")

        self.dotnotation_helper = DotnotationHelper(**self.settings)

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
    def _import_relatie_object(cls, model_directory: Path) -> Union[Type[RelatieObject], None]:
        sys.path.insert(1, str(model_directory))
        try:
            mod = importlib.import_module('OtlmowModel.Classes.ImplementatieElement.RelatieObject')
            class_ = getattr(mod, 'RelatieObject')
            return class_

        except ModuleNotFoundError:
            raise ModuleNotFoundError(f'When dynamically importing class RelatieObject, the import failed. '
                                      f'Make sure you are directing to the (parent) directory where OtlmowModel is '
                                      f'located in.')

    @classmethod
    def get_index_of_typeURI_column_in_sheet(cls, filepath: Path, sheet: str,  headers: List[str],
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

    def from_table_to_data(self, data: List[List], values_as_strings: bool = True,  model_directory: Path = None
                           ) -> List[OTLObject]:
        if model_directory is None:
            model_directory = self.model_directory

        list_of_objects = []
        headers = data[0]

        type_index = self.get_index_of_typeURI_column_in_sheet(filepath=Path(''), sheet='sheet', headers=headers,
                                                               data=data[1:])

        for record in data[1:]:
            instance = dynamic_create_instance_from_uri(record[type_index], model_directory=model_directory)
            list_of_objects.append(instance)
            for index, row in enumerate(record):
                if index == type_index:
                    continue
                if row == '':
                    continue

                if headers[index] in ['bron.typeURI', 'doel.typeURI']:
                    continue  # TODO get bron and doel

                cardinality_indicator = self.settings['cardinality_indicator']

                if cardinality_indicator in headers[index]:
                    if headers[index].count(cardinality_indicator) > 1:
                        logging.warning(
                            f'{headers[index]} is a list of lists. This is not allowed in the CSV format')
                        continue
                    value = row
                else:
                    value = row

                if headers[index] == 'geometry':
                    value = value
                    if value == '':
                        value = None
                    headers[index] = 'geometry'

                try:
                    self.dotnotation_helper.set_attribute_by_dotnotation_instance(
                        instance_or_attribute=instance, dotnotation=headers[index], value=value,
                        convert_warnings=False)
                except AttributeError as exc:
                    raise AttributeError(headers[index]) from exc

        return list_of_objects
