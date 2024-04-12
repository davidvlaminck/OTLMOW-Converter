from pathlib import Path
from typing import Iterable, Dict, Union

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, create_dict_from_asset
from pandas import DataFrame

from otlmow_converter.DotnotationDict import DotnotationDict
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.FileExporter import FileExporter
from otlmow_converter.FileFormats.PandasConverter import PandasConverter
from otlmow_converter.FileImporter import FileImporter
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

load_settings()


class OtlmowConverter:
    """
    Main utility class for converting OTLMOW objects to and from formats, such as files, dictionaries and dataframes.
    To change the settings, use the load_settings() or update_settings_by_dict() functions from SettingsManager
    before using this class.
    The converter uses the point of view of the OTLMOW model objects.
    For example, when using the from_objects_to_file() method, it converts the OTLMOW model objects (in memory) to a file.
    When using the from_file_to_objects() method, it converts the file to OTLMOW model objects (in memory).
    """

    @classmethod
    def from_objects_to_dicts(cls, sequence_of_objects: Iterable[OTLObject], **kwargs) -> Iterable[Dict]:
        """
        Converts a sequence of OTLObject objects to a sequence of dictionaries.
        This conversion uses the OTLMOW settings.
        See the create_dict_from_asset() method in the OTLObject class for more information on the keyword arguments.
        """
        for obj in sequence_of_objects:
            yield create_dict_from_asset(obj, **kwargs)

    @classmethod
    def from_dicts_to_objects(cls, sequence_of_dicts: Iterable[Dict], **kwargs) -> Iterable[OTLObject]:
        """
        Converts a sequence of dictionaries to a sequence of OTLObject objects.
        This conversion uses the OTLMOW settings.
        See the from_dict() method in the OTLObject class for more information on the keyword arguments.
        """

        for d in sequence_of_dicts:
            yield OTLObject.from_dict(input_dict=d, **kwargs)

    @classmethod
    def from_objects_to_dotnotation_dicts(cls, sequence_of_objects: Iterable[OTLObject], **kwargs
                                          ) -> Iterable[DotnotationDict]:
        """
        Converts a sequence of OTLObject objects to a sequence of dictionaries.
        This conversion uses the OTLMOW settings.
        See the to_dict() method in the DotnotationDictConverter class for more information on the keyword arguments.
        """
        for obj in sequence_of_objects:
            yield DotnotationDictConverter.to_dict(obj, **kwargs)

    @classmethod
    def from_dotnotation_dicts_to_objects(cls, sequence_of_dotnotation_dicts: Iterable[DotnotationDict], **kwargs
                                          ) -> Iterable[OTLObject]:
        """
        Converts a sequence of OTLObject objects to a sequence of dictionaries.
        This conversion uses the OTLMOW settings.
        See the from_dict() method in the DotnotationDictConverter class for more information on the keyword arguments.
        """
        for obj in sequence_of_dotnotation_dicts:
            yield DotnotationDictConverter.from_dict(obj, **kwargs)

    @classmethod
    def from_file_to_objects(cls, file_path: Path, **kwargs) -> Iterable[OTLObject]:
        """Converts a file to a sequence of OTLObject objects.
        This conversion uses the OTLMOW settings.
        See the specific Importer functions for more information on the keyword arguments.
        """
        importer = FileImporter.get_importer_from_extension(extension=file_path.suffix[1:])
        return importer.to_objects(filepath=file_path, **kwargs)

    @classmethod
    def from_objects_to_file(cls, file_path: Path, sequence_of_objects: Iterable[OTLObject], **kwargs) -> None:
        """Converts a sequence of OTLObject objects to a file.
        This conversion uses the OTLMOW settings.
        See the specific Exporter functions for more information on the keyword arguments.
        """
        exporter = FileExporter.get_exporter_from_extension(extension=file_path.suffix[1:])
        exporter.from_objects(sequence_of_objects=sequence_of_objects, filepath=file_path, **kwargs)

    @classmethod
    def from_objects_to_dataframe(cls, sequence_of_objects: Iterable[OTLObject], split_per_type: bool = False
                                  ) -> Union[DataFrame, Dict[str, DataFrame]]:
        """Converts a sequence of OTLObject objects to a pandas DataFrame.
        This conversion uses the OTLMOW settings.
        """
        if split_per_type:
            return PandasConverter.convert_objects_to_multiple_dataframes(sequence_of_objects)
        else:
            return PandasConverter.convert_objects_to_single_dataframe(sequence_of_objects)

    @classmethod
    def from_dataframe_to_objects(cls, dataframe: DataFrame, **kwargs) -> Iterable[OTLObject]:
        """Converts a pandas DataFrame to a sequence of OTLObject objects.
        This method can be used when you have a single dataframe to convert.
        This conversion uses the OTLMOW settings.
        """
        return PandasConverter.convert_dataframe_to_objects(dataframe, **kwargs)

    #
    #
    # def create_assets_from_file(self, filepath: Path = None, **kwargs) -> list:
    #     """Creates asset objects in memory from a file. Supports csv and json files.
    #
    #     :param filepath: Path to the file that is to be imported
    #     :type: Path
    #
    #     Supported arguments for csv:
    #
    #     delimiter (str): Specifies the delimiter for the csv file. Defaults to ';'
    #     quote_char (str): Specifies the quote_char for the csv file. Defaults to '"'
    #
    #     Supported arguments for json:
    #
    #     ignore_failed_objects (bool): If True, suppresses the errors resulting from the creation of one object,
    #     to allow the collection of all non-erroneous objects. Defaults to False
    #
    #     :return: Returns a list with asset objects
    #     :rtype: list
    #     """
    #     file_importer = FileImporter(settings=self.settings)
    #     return file_importer.create_assets_from_file(filepath=filepath, **kwargs)
    #
    # def create_file_from_assets(self, filepath: Path, list_of_objects: list, **kwargs) -> None:
    #     """Creates a file from asset objects in memory. Supports csv and json files.
    #
    #     :param filepath: Path to the file that is to be created
    #     :type: Path
    #     :param list_of_objects: The objects in memory that will be exported to a file
    #     :type: list
    #
    #     Supported arguments for csv:
    #
    #     delimiter (str): Specifies the delimiter for the csv file. Defaults to ';'
    #     quote_char (str): Specifies the quote_char for the csv file. Defaults to '"'
    #     split_per_type (bool): If True, creates a file per type instead of one file for all objects
    #
    #     :return: Returns a list with asset objects
    #     :rtype: list
    #     """
    #     file_exporter = FileExporter(settings=self.settings)
    #     return file_exporter.create_file_from_assets(filepath=filepath, list_of_objects=list_of_objects, **kwargs)

    suffix_mapping_table = {
        'json': 'JSON',
        'csv': 'csv',
        'xlsx': 'xlsx',
        'xls': 'xlsx',
        'geojson': 'GeoJSON',
        'ttl': 'ttl',
        'jsonld': 'JSON-LD',
    }

    @classmethod
    def get_mapped_setting_name_from_file_path(cls, file_path: Path):
        suffix = file_path.suffix[1:]
        return cls.suffix_mapping_table.get(suffix)

