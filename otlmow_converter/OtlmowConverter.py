from pathlib import Path
from typing import Iterable

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, create_dict_from_asset

from otlmow_converter.FileExporter import FileExporter
from otlmow_converter.FileImporter import FileImporter
import otlmow_converter.SettingsManager
from otlmow_converter.SettingsManager import load_settings

load_settings()
global OTLMOW_CONVERTER_SETTINGS
settings = OTLMOW_CONVERTER_SETTINGS

class OtlmowConverter:
    """
    Main utility class for converting OTLMOW objects to and from formats, such as files, dictionaries and dataframes.
    To change the settings, use the SettingsManager.load_settings() method before using this class
    The converter uses the point of view of the OTLMOW model objects.
    For example, when using the to_file() method, it converts the OTLMOW model objects (in memory) to a file.
    When using the from_file() method, it converts the file to OTLMOW model objects (in memory).
    """

    @classmethod
    def to_dicts(cls, sequence_of_objects: Iterable[OTLObject], **kwargs) -> Iterable[dict]:
        """
        Converts a sequence of OTLObject objects to a sequence of dictionaries.
        This conversion uses the OTLMOW settings.
        See the create_dict_from_asset() method in the OTLObject class for more information on the keyword arguments.
        """
        datetime_as_string = settings['formats']['OTLMOW']['datetime_as_string']
        for obj in sequence_of_objects:
            yield create_dict_from_asset(obj, datetime_as_string=datetime_as_string, **kwargs)


    def create_assets_from_file(self, filepath: Path = None, **kwargs) -> list:
        """Creates asset objects in memory from a file. Supports csv and json files.

        :param filepath: Path to the file that is to be imported
        :type: Path

        Supported arguments for csv:

        delimiter (str): Specifies the delimiter for the csv file. Defaults to ';'
        quote_char (str): Specifies the quote_char for the csv file. Defaults to '"'

        Supported arguments for json:

        ignore_failed_objects (bool): If True, suppresses the errors resulting from the creation of one object,
        to allow the collection of all non-erroneous objects. Defaults to False

        :return: Returns a list with asset objects
        :rtype: list
        """
        file_importer = FileImporter(settings=self.settings)
        return file_importer.create_assets_from_file(filepath=filepath, **kwargs)

    def create_file_from_assets(self, filepath: Path, list_of_objects: list, **kwargs) -> None:
        """Creates a file from asset objects in memory. Supports csv and json files.

        :param filepath: Path to the file that is to be created
        :type: Path
        :param list_of_objects: The objects in memory that will be exported to a file
        :type: list

        Supported arguments for csv:

        delimiter (str): Specifies the delimiter for the csv file. Defaults to ';'
        quote_char (str): Specifies the quote_char for the csv file. Defaults to '"'
        split_per_type (bool): If True, creates a file per type instead of one file for all objects

        :return: Returns a list with asset objects
        :rtype: list
        """
        file_exporter = FileExporter(settings=self.settings)
        return file_exporter.create_file_from_assets(filepath=filepath, list_of_objects=list_of_objects, **kwargs)
