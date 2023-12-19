from typing import List, Dict

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from pandas import DataFrame

from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter


class PandasConverter:
    def __init__(self, settings=None):
        if settings is None:
            settings = {}

        if 'file_formats' not in settings:
            raise ValueError("The settings are not loaded or don't contain settings for file formats")
        pandas_settings = next((s for s in settings['file_formats'] if 'name' in s and s['name'] == 'pandas'), None)
        if pandas_settings is None:
            raise ValueError("Unable to find pandas in file formats settings")

        self.dotnotation_table_converter = DotnotationTableConverter()
        self.dotnotation_table_converter.load_settings(pandas_settings['dotnotation'])

    def convert_objects_to_single_dataframe(self, list_of_objects: List[OTLObject], **kwargs) -> DataFrame:
        model_directory = None
        if kwargs is not None and 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']
        self.dotnotation_table_converter.model_directory = model_directory

        single_table = self.dotnotation_table_converter.get_single_table_from_data(list_of_objects=list_of_objects)
        return DataFrame(data=single_table[1:])

    def convert_objects_to_multiple_dataframes(self, list_of_objects: List[OTLObject], **kwargs
                                               ) -> Dict[str, DataFrame]:
        pass

    def convert_dataframe_to_objects(self, dataframe: DataFrame, **kwargs) -> List[OTLObject]:
        model_directory = None
        if kwargs is not None and 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']
        self.dotnotation_table_converter.model_directory = model_directory

        headers = list(dataframe)
        d = {header: index for index, header in enumerate(headers)}
        dict_list = [d]
        dict_list.extend(dataframe.to_dict('records'))

        return self.dotnotation_table_converter.get_data_from_table(table_data=dict_list)
    