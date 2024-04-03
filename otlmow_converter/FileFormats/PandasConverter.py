from typing import List, Dict, Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from pandas import DataFrame

from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter


class PandasConverter:
    @classmethod
    def convert_objects_to_single_dataframe(cls, list_of_objects: Iterable[OTLObject]) -> DataFrame:
        single_table = DotnotationTableConverter.get_single_table_from_data(list_of_objects=list_of_objects)
        return DataFrame(data=single_table[1:])

    @classmethod
    def convert_objects_to_multiple_dataframes(cls, list_of_objects: Iterable[OTLObject]
                                               ) -> Dict[str, DataFrame]:
        dict_tables = DotnotationTableConverter.get_tables_per_type_from_data(list_of_objects=list_of_objects)
        return {key: DataFrame(data=value[1:]) for key, value in dict_tables.items()}

    @classmethod
    def convert_dataframe_to_objects(cls, dataframe: DataFrame, **kwargs) -> Iterable[OTLObject]:
        model_directory = None
        if kwargs is not None and 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']

        headers = list(dataframe)
        d = {header: index for index, header in enumerate(headers)}
        dict_list = [d]
        dict_list.extend(dataframe.to_dict('records'))

        return DotnotationTableConverter.get_data_from_table(table_data=dict_list, model_directory=model_directory,
                                                             cast_list=False)
    