from collections import defaultdict
from itertools import chain
from pathlib import Path
from typing import Iterable, Union

from numpy import nan
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, create_dict_from_asset
from otlmow_model.OtlmowModel.Helpers.GenericHelper import get_shortened_uri
from pandas import DataFrame

from otlmow_converter.DotnotationDict import DotnotationDict
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.FileExporter import FileExporter
from otlmow_converter.FileFormats.PandasConverter import PandasConverter
from otlmow_converter.FileImporter import FileImporter
from otlmow_converter.SettingsManager import load_settings

load_settings()


class OtlmowConverter:
    """
    Main utility class for converting OTLMOW objects to and from formats, such as files, dictionaries and dataframes.
    To change the settings, use the load_settings() or update_settings_by_dict() functions from SettingsManager
    before using this class. The converter uses the point of view of the OTLMOW model objects by default and thus
    supports conversion from OTLMOW model objects to and from all other formats. These are:

    - files (Path objects) to convert to and from JSON, CSV, Excel, GeoJSON and JSON-LD files

    - dictionaries, in native OTL terms

    - DotnotationDict objects, which are dictionaries with AWV dotnotation support

    - pandas DataFrames, which are used for tabular data and use the AWV dotnotation

    There are generic functions to convert to any of these formats, which will determine the type of the input(subject)
    and convert it to the desired output format. The more specific functions are used to convert to and from objects.

    Output in the form of a sequence is always an iterable (generator), which can be used in a for loop or converted to
    a list or other sequence type.
    """

    @classmethod
    def to_objects(cls, subject: object, model_directory: Path = None, **kwargs) -> Iterable[OTLObject]:
        """Converts any subject to a sequence of OTLObject objects.
        This conversion uses the OTLMOW settings.
        """
        if isinstance(subject, Path):
            yield from cls.from_file_to_objects(file_path=subject, model_directory=model_directory, **kwargs)
        elif isinstance(subject, DataFrame):
            yield from cls.from_dataframe_to_objects(dataframe=subject, model_directory=model_directory, **kwargs)
        elif isinstance(subject, Iterable):
            try:
                generator = iter(subject)
                first_element = next(generator)
                if first_element is None:
                    yield from []
                else:
                    new_generator = iter(chain([first_element], generator))
                    if isinstance(first_element, DotnotationDict):
                        yield from cls.from_dotnotation_dicts_to_objects(sequence_of_dotnotation_dicts=new_generator,
                                                                         model_directory=model_directory, **kwargs)
                    elif isinstance(first_element, dict):
                        yield from cls.from_dicts_to_objects(sequence_of_dicts=new_generator,
                                                             model_directory=model_directory, **kwargs)
                    elif isinstance(first_element, OTLObject):
                        yield from new_generator
                    else:
                        raise ValueError(f"Unsupported subject type: {type(first_element)}")
            except StopIteration:
                yield from []
        else:
            raise ValueError(f"Unsupported subject type: {type(subject)}")

    @classmethod
    def to_file(cls, subject: object, file_path: Path, model_directory: Path = None, **kwargs) -> None:
        """Converts any subject (including another file) to a file.
        This conversion uses the OTLMOW settings.
        """
        if isinstance(subject, Path):
            objects = cls.from_file_to_objects(file_path=subject, model_directory=model_directory, **kwargs)
            cls.from_objects_to_file(file_path=file_path, sequence_of_objects=objects, **kwargs)
        elif isinstance(subject, DataFrame):
            objects = cls.from_dataframe_to_objects(dataframe=subject, model_directory=model_directory, **kwargs)
            cls.from_objects_to_file(file_path=file_path, sequence_of_objects=objects, **kwargs)
        elif isinstance(subject, Iterable):
            try:
                generator = iter(subject)
                first_element = next(generator)
                if first_element is None:
                    return
                else:
                    new_generator = iter(chain([first_element], generator))
                    if isinstance(first_element, DotnotationDict):
                        objects = cls.from_dotnotation_dicts_to_objects(sequence_of_dotnotation_dicts=new_generator,
                                                                        model_directory=model_directory, **kwargs)
                        cls.from_objects_to_file(file_path=file_path, sequence_of_objects=objects, **kwargs)
                    elif isinstance(first_element, dict):
                        objects = cls.from_dicts_to_objects(sequence_of_dicts=new_generator,
                                                            model_directory=model_directory, **kwargs)
                        cls.from_objects_to_file(file_path=file_path, sequence_of_objects=objects, **kwargs)
                    elif isinstance(first_element, OTLObject):
                        cls.from_objects_to_file(file_path=file_path, sequence_of_objects=new_generator, **kwargs)
                    else:
                        raise ValueError(f"Unsupported subject type: {type(first_element)}")
            except StopIteration:
                return
        else:
            raise ValueError(f"Unsupported subject type: {type(subject)}")

    @classmethod
    def to_dataframe(cls, subject: object, split_per_type: bool = False, model_directory: Path = None, **kwargs
                     ) -> Union[DataFrame, dict[str, DataFrame]]:
        """Converts any subject to a pandas Dataframe.
        This conversion uses the OTLMOW settings.
        """
        if isinstance(subject, Path):
            objects = cls.from_file_to_objects(file_path=subject, model_directory=model_directory, **kwargs)
            return cls.from_objects_to_dataframe(sequence_of_objects=objects, split_per_type=split_per_type, **kwargs)
        elif isinstance(subject, DataFrame):
            if split_per_type:
                objects = cls.from_dataframe_to_objects(dataframe=subject, model_directory=model_directory, **kwargs)
                return PandasConverter.convert_objects_to_multiple_dataframes(sequence_of_objects=objects, **kwargs)
            return subject
        elif isinstance(subject, Iterable):
            try:
                generator = iter(subject)
                first_element = next(generator)
                if first_element is None:
                    return DataFrame()
                else:
                    new_generator = iter(chain([first_element], generator))
                    if isinstance(first_element, DotnotationDict):
                        if split_per_type:
                            master_dict = defaultdict(list)
                            for d in new_generator:
                                master_dict[get_shortened_uri(d['typeURI'])].append(d)

                            return {key: DataFrame(data=value) for key, value in master_dict.items()}
                        else:
                            return DataFrame(new_generator)
                    elif isinstance(first_element, dict):
                        objects = cls.from_dicts_to_objects(sequence_of_dicts=new_generator,
                                                            model_directory=model_directory, **kwargs)
                        return cls.from_objects_to_dataframe(sequence_of_objects=objects, split_per_type=split_per_type,
                                                             **kwargs)
                    elif isinstance(first_element, OTLObject):
                        return cls.from_objects_to_dataframe(sequence_of_objects=new_generator,
                                                             split_per_type=split_per_type, **kwargs)
                    else:
                        raise ValueError(f"Unsupported subject type: {type(first_element)}")
            except StopIteration:
                return DataFrame()
        else:
            raise ValueError(f"Unsupported subject type: {type(subject)}")

    @classmethod
    def to_dicts(cls, subject: object, model_directory: Path = None, **kwargs) -> Iterable[dict]:
        """Converts any subject to a sequence of dictionaries.
        This conversion uses the OTLMOW settings.
        """
        if isinstance(subject, Path):
            objects = cls.from_file_to_objects(file_path=subject, model_directory=model_directory, **kwargs)
            yield from cls.from_objects_to_dicts(sequence_of_objects=objects, **kwargs)
        elif isinstance(subject, DataFrame):
            objects = cls.from_dataframe_to_objects(dataframe=subject, model_directory=model_directory, **kwargs)
            yield from cls.from_objects_to_dicts(sequence_of_objects=objects, **kwargs)
        elif isinstance(subject, Iterable):
            try:
                generator = iter(subject)
                first_element = next(generator)
                if first_element is None:
                    yield from []
                else:
                    new_generator = iter(chain([first_element], generator))
                    if isinstance(first_element, DotnotationDict):
                        objects = cls.from_dotnotation_dicts_to_objects(sequence_of_dotnotation_dicts=new_generator,
                                                                        model_directory=model_directory, **kwargs)
                        yield from cls.from_objects_to_dicts(sequence_of_objects=objects, **kwargs)
                    elif isinstance(first_element, dict):
                        yield from new_generator
                    elif isinstance(first_element, OTLObject):
                        yield from cls.from_objects_to_dicts(sequence_of_objects=new_generator, **kwargs)
                    else:
                        raise ValueError(f"Unsupported subject type: {type(first_element)}")
            except StopIteration:
                yield from []
        else:
            raise ValueError(f"Unsupported subject type: {type(subject)}")

    @classmethod
    def to_dotnotation_dicts(cls, subject: object, model_directory: Path = None, **kwargs) -> Iterable[DotnotationDict]:
        """Converts any subject to a sequence of DotnotationDict objects.
        This conversion uses the OTLMOW settings.
        """
        if isinstance(subject, Path):
            objects = cls.from_file_to_objects(file_path=subject, model_directory=model_directory, **kwargs)
            yield from cls.from_objects_to_dotnotation_dicts(sequence_of_objects=objects, **kwargs)
        elif isinstance(subject, DataFrame):
            subject = subject.replace({nan: None})
            yield from [DotnotationDict({k: v for k, v in d.items() if v is not None})
                        for d in subject.to_dict('records')]
        elif isinstance(subject, Iterable):
            try:
                generator = iter(subject)
                first_element = next(generator)
                if first_element is None:
                    yield from []
                else:
                    new_generator = iter(chain([first_element], generator))
                    if isinstance(first_element, DotnotationDict):
                        yield from new_generator
                    elif isinstance(first_element, dict):
                        objects = cls.from_dicts_to_objects(sequence_of_dicts=new_generator,
                                                            model_directory=model_directory, **kwargs)
                        yield from cls.from_objects_to_dotnotation_dicts(sequence_of_objects=objects, **kwargs)
                    elif isinstance(first_element, OTLObject):
                        yield from cls.from_objects_to_dotnotation_dicts(sequence_of_objects=new_generator, **kwargs)
                    else:
                        raise ValueError(f"Unsupported subject type: {type(first_element)}")
            except StopIteration:
                yield from []
        else:
            raise ValueError(f"Unsupported subject type: {type(subject)}")

    @classmethod
    def from_objects_to_dicts(cls, sequence_of_objects: Iterable[OTLObject], **kwargs) -> Iterable[dict]:
        """
        Converts a sequence of OTLObject objects to a sequence of dictionaries.
        This conversion uses the OTLMOW settings.
        See the create_dict_from_asset() method in the OTLObject class for more information on the keyword arguments.
        """
        for obj in sequence_of_objects:
            yield create_dict_from_asset(obj, **kwargs)

    @classmethod
    def from_dicts_to_objects(cls, sequence_of_dicts: Iterable[dict], **kwargs) -> Iterable[OTLObject]:
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
    def from_file_to_objects(cls, file_path: Path, model_directory: Path = None, **kwargs) -> Iterable[OTLObject]:
        """Converts a file to a sequence of OTLObject objects.
        This conversion uses the OTLMOW settings.
        See the specific Importer functions for more information on the keyword arguments.
        """
        importer = FileImporter.get_importer_from_extension(extension=file_path.suffix[1:])
        return importer.to_objects(filepath=file_path, model_directory=model_directory, **kwargs)

    @classmethod
    def from_objects_to_file(cls, file_path: Path, sequence_of_objects: Iterable[OTLObject], **kwargs) -> None:
        """Converts a sequence of OTLObject objects to a file.
        This conversion uses the OTLMOW settings.
        See the specific Exporter functions for more information on the keyword arguments.
        """
        exporter = FileExporter.get_exporter_from_extension(extension=file_path.suffix[1:])
        exporter.from_objects(sequence_of_objects=sequence_of_objects, filepath=file_path, **kwargs)

    @classmethod
    def from_objects_to_dataframe(cls, sequence_of_objects: Iterable[OTLObject], split_per_type: bool = False, **kwargs
                                  ) -> Union[DataFrame, dict[str, DataFrame]]:
        """Converts a sequence of OTLObject objects to a pandas DataFrame.
        This conversion uses the OTLMOW settings.
        """
        if split_per_type:
            return PandasConverter.convert_objects_to_multiple_dataframes(sequence_of_objects, **kwargs)
        else:
            return PandasConverter.convert_objects_to_single_dataframe(sequence_of_objects, **kwargs)

    @classmethod
    def from_dataframe_to_objects(cls, dataframe: DataFrame, **kwargs) -> Iterable[OTLObject]:
        """Converts a pandas DataFrame to a sequence of OTLObject objects.
        This method can be used when you have a single dataframe to convert.
        This conversion uses the OTLMOW settings.
        """
        return PandasConverter.convert_dataframe_to_objects(dataframe, **kwargs)

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


def to_objects(subject: object, model_directory: Path = None, **kwargs) -> Iterable[OTLObject]:
    return OtlmowConverter.to_objects(subject=subject, model_directory=model_directory, **kwargs)


def to_dicts(subject: object, model_directory: Path = None, **kwargs) -> Iterable[dict]:
    return OtlmowConverter.to_dicts(subject=subject, model_directory=model_directory, **kwargs)


def to_dotnotation_dicts(subject: object, model_directory: Path = None, **kwargs) -> Iterable[DotnotationDict]:
    return OtlmowConverter.to_dotnotation_dicts(subject=subject, model_directory=model_directory, **kwargs)


def to_file(subject: object, file_path: Path, model_directory: Path = None, **kwargs) -> None:
    OtlmowConverter.to_file(subject=subject, file_path=file_path, model_directory=model_directory, **kwargs)


def to_dataframe(subject: object, split_per_type: bool = False, model_directory: Path = None, **kwargs
                 ) -> Union[DataFrame, dict[str, DataFrame]]:
    return OtlmowConverter.to_dataframe(subject=subject, split_per_type=split_per_type,
                                        model_directory=model_directory, **kwargs)
