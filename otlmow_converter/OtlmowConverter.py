import logging
from pathlib import Path

from otlmow_converter.FileExporter import FileExporter
from otlmow_converter.FileImporter import FileImporter
from otlmow_converter.SettingsManager import load_settings


class OtlmowConverter:
    def __init__(self,
                 settings_path: Path = None,
                 logging_level: int = logging.WARNING,
                 logfile: Path = None):
        """Main utility class for creating a model, importing and exporting assets from files and enabling validation features

        :param settings_path: specifies the location of the settings file this library loads. Defaults to the example that is supplied with the library ('./settings_otlmow_converter.json')
        :type settings_path: Path
        :param logging_level: specifies the level of logging that is used for actions with this class
        :type logging_level: int
        :param logfile: specifies the path to the logfile.
        :type logfile: Path
        """
        self.settings: dict = load_settings(settings_path)

        if logging_level != 0 and logfile is not None and str(logfile) != '':
            logging.basicConfig(filename=str(logfile),
                                filemode='a',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt='%H:%M:%S',
                                level=logging_level)

    def create_assets_from_file(self, filepath: Path = None, **kwargs) -> list:
        """Creates asset objects in memory from a file. Supports csv and json files.

        :param filepath: Path to the file that is to be imported
        :type: Path

        Supported arguments for csv:

        delimiter (str): Specifies the delimiter for the csv file. Defaults to ';'

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
        split_per_type (bool): If True, creates a file per type instead of one file for all objects

        :return: Returns a list with asset objects
        :rtype: list
        """
        file_exporter = FileExporter(settings=self.settings)
        return file_exporter.create_file_from_assets(filepath=filepath, list_of_objects=list_of_objects, **kwargs)

    @staticmethod
    def _validate_environment(environment: str):
        if environment is None:
            return 'prd'
        environment = environment.lower()
        if environment in ['', 'prd']:
            return 'prd'
        elif environment in ['tei', 'dev', 'aim']:
            return environment
        raise ValueError("Valid options for the environment parameter are: '', 'prd', 'tei', 'dev' and 'aim'")
