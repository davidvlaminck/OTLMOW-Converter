from pathlib import Path
from typing import Iterable
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from pandas import DataFrame

from otlmow_converter.FileFormats.DotnotationTableConverter import DotnotationTableConverter


class PandasConverter:
    @classmethod
    def convert_objects_to_single_dataframe(cls, list_of_objects: Iterable[OTLObject], **kwargs) -> DataFrame:
        single_table = DotnotationTableConverter.get_single_table_from_data(
            list_of_objects=list_of_objects, **kwargs)
        return DataFrame(data=single_table[1:])

    @classmethod
    async def convert_objects_to_single_dataframe_async(cls, list_of_objects: Iterable[OTLObject], **kwargs
                                                        ) -> (DataFrame):
        single_table = await DotnotationTableConverter.get_single_table_from_data_async(
            list_of_objects=list_of_objects, **kwargs)
        return DataFrame(data=single_table[1:])

    @classmethod
    def convert_objects_to_multiple_dataframes(cls, sequence_of_objects: Iterable[OTLObject], **kwargs
                                               ) -> dict[str, DataFrame]:
        dict_tables = DotnotationTableConverter.get_tables_per_type_from_data(
            sequence_of_objects=sequence_of_objects, **kwargs)
        return {key: DataFrame(data=value[1:]) for key, value in dict_tables.items()}

    @classmethod
    async def convert_objects_to_multiple_dataframes_async(cls, sequence_of_objects: Iterable[OTLObject], **kwargs
                                               ) -> dict[str, DataFrame]:
        dict_tables = await DotnotationTableConverter.get_tables_per_type_from_data_async(
            sequence_of_objects=sequence_of_objects, **kwargs)
        return {key: DataFrame(data=value[1:]) for key, value in dict_tables.items()}

    @classmethod
    def tolist_if_possible(cls, x):
        tolist = getattr(x, "tolist", None)
        return tolist() if callable(tolist) else x

    @classmethod
    def convert_dataframe_to_objects(cls, dataframe: DataFrame, model_directory: Path = None, **kwargs
                                     ) -> Iterable[OTLObject]:
        df = dataframe.where(~dataframe.isna(), None)

        for col in df.columns:
            if any(callable(getattr(x, "tolist", None)) for x in df[col]):
                df[col] = df[col].apply(cls.tolist_if_possible)

        headers = list(df)
        d = {header: index for index, header in enumerate(headers)}
        dict_list = [d]
        dict_list.extend(df.to_dict('records'))

        return DotnotationTableConverter.get_data_from_table(
            table_data=dict_list,   model_directory=model_directory, **kwargs)

    @classmethod
    async def convert_dataframe_to_objects_async(cls, dataframe: DataFrame, model_directory: Path = None, **kwargs
                                     ) -> Iterable[OTLObject]:
        dataframe = dataframe.where(~dataframe.isna(), None)
        headers = list(dataframe)
        d = {header: index for index, header in enumerate(headers)}
        dict_list = [d]
        dict_list.extend(dataframe.to_dict('records'))

        return await DotnotationTableConverter.get_data_from_table_async(
            table_data=dict_list,   model_directory=model_directory, **kwargs)

