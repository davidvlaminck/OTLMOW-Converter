from pathlib import Path
from typing import Iterable, Dict, Union

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, create_dict_from_asset
from pandas import DataFrame

from otlmow_converter.FileExporter import FileExporter
from otlmow_converter.FileImporter import FileImporter
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

load_settings()

class OtlmowConverter:
    """
    Main utility class for converting OTLMOW objects to and from formats, such as files, dictionaries and dataframes.
    To change the settings, use the load_settings() or update_settings_by_dict() functions from SettingsManager
    before using this class.
    The converter uses the point of view of the OTLMOW model objects.
    For example, when using the to_file() method, it converts the OTLMOW model objects (in memory) to a file.
    When using the from_file() method, it converts the file to OTLMOW model objects (in memory).
    """

    @classmethod
    def to_dicts(cls, sequence_of_objects: Iterable[OTLObject], **kwargs) -> Iterable[Dict]:
        """
        Converts a sequence of OTLObject objects to a sequence of dictionaries.
        This conversion uses the OTLMOW settings.
        See the create_dict_from_asset() method in the OTLObject class for more information on the keyword arguments.
        """
        rdf = kwargs.get('rdf',  GlobalVariables.settings['formats']['OTLMOW']['rdf'])
        waarde_shortcut = kwargs.get('waarde_shortcut', GlobalVariables.settings['formats']['OTLMOW']['waarde_shortcut'])
        datetime_as_string = kwargs.get('datetime_as_string',
                                        GlobalVariables.settings['formats']['OTLMOW']['datetime_as_string'])
        allow_non_otl_conform_attributes = kwargs.get('allow_non_otl_conform_attributes',
                                        GlobalVariables.settings['formats']['OTLMOW']['allow_non_otl_conform_attributes'])
        warn_for_non_otl_conform_attributes = (
            kwargs.get('warn_for_non_otl_conform_attributes',
                       GlobalVariables.settings['formats']['OTLMOW']['warn_for_non_otl_conform_attributes']))

        for obj in sequence_of_objects:
            yield create_dict_from_asset(obj, rdf=rdf, waarde_shortcut=waarde_shortcut,
                                         allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                         warn_for_non_otl_conform_attributes= warn_for_non_otl_conform_attributes,
                                         datetime_as_string=datetime_as_string)

    @classmethod
    def from_dicts(cls, sequence_of_dicts: Iterable[Dict], **kwargs) -> Iterable[OTLObject]:
        """
        Converts a sequence of dictionaries to a sequence of OTLObject objects.
        This conversion uses the OTLMOW settings.
        See the from_dict() method in the OTLObject class for more information on the keyword arguments.
        """
        rdf = kwargs.get('rdf',  GlobalVariables.settings['formats']['OTLMOW']['rdf'])
        waarde_shortcut = kwargs.get('waarde_shortcut', GlobalVariables.settings['formats']['OTLMOW']['waarde_shortcut'])
        datetime_as_string = kwargs.get('datetime_as_string',
                                        GlobalVariables.settings['formats']['OTLMOW']['datetime_as_string'])
        allow_non_otl_conform_attributes = kwargs.get('allow_non_otl_conform_attributes',
                                        GlobalVariables.settings['formats']['OTLMOW']['allow_non_otl_conform_attributes'])
        warn_for_non_otl_conform_attributes = (
            kwargs.get('warn_for_non_otl_conform_attributes',
                       GlobalVariables.settings['formats']['OTLMOW']['warn_for_non_otl_conform_attributes']))

        for d in sequence_of_dicts:
            yield OTLObject.from_dict(input_dict=d, rdf=rdf, waarde_shortcut=waarde_shortcut,
                                      allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                      warn_for_non_otl_conform_attributes= warn_for_non_otl_conform_attributes,
                                      datetime_as_string=datetime_as_string, **kwargs)

    @classmethod
    def to_file(cls, file_path: Path, sequence_of_objects: Iterable[OTLObject], **kwargs) -> None:
        """Converts a sequence of OTLObject objects to a file.
        This conversion uses the OTLMOW settings.
        See the specific Exporter functions for more information on the keyword arguments.
        """
        suffix = file_path.suffix[1:]
        dotnotation_settings = kwargs.get('dotnotation_settings',
                                          GlobalVariables.settings['formats'][suffix]['dotnotation'])
        datetime_as_string = kwargs.get('datetime_as_string',
                                        GlobalVariables.settings['formats'][suffix]['datetime_as_string'])
        allow_non_otl_conform_attributes = kwargs.get('allow_non_otl_conform_attributes',
                                        GlobalVariables.settings['formats'][suffix]['allow_non_otl_conform_attributes'])
        warn_for_non_otl_conform_attributes = (
            kwargs.get('warn_for_non_otl_conform_attributes',
                       GlobalVariables.settings['formats'][suffix]['warn_for_non_otl_conform_attributes']))

        exporter = FileExporter.get_exporter_from_extension(extension=suffix)
        exporter.export_to_file(filepath=file_path, sequence_of_objects=sequence_of_objects, **kwargs)






    def to_dataframe(self, sequence_of_objects: Iterable[OTLObject], split_per_type: bool, **kwargs
                     ) -> Union[DataFrame, Dict[str, DataFrame]]:
        """Converts a sequence of OTLObject objects to a pandas DataFrame.
        This conversion uses the OTLMOW settings.
        See the create_dict_from_asset() method in the OTLObject class for more information on the keyword arguments.
        """
        #return DataFrame(self.to_dicts(sequence_of_objects, **kwargs)) # TODO: Implement this method
        pass



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
