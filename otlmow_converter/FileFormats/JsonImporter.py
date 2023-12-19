from pathlib import Path

from otlmow_converter.FileFormats.JsonDecoder import JsonDecoder


class JsonImporter:
    def __init__(self, settings):
        self.decoder = JsonDecoder(settings=settings)

    def import_file(self, filepath: Path, **kwargs) -> list:
        """Imports a json file created with Davie and decodes it to OTL objects

        :param filepath: location of the file to import
        :type: Path
        :rtype: list
        :return: returns a list of OTL objects
        """

        ignore_failed_objects = False

        if kwargs is not None and 'ignore_failed_objects' in kwargs:
            ignore_failed_objects = kwargs['ignore_failed_objects']

        model_directory = None
        if kwargs is not None and 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']

        data = Path(filepath).read_text()
        return self.decoder.decode_json_string(data, ignore_failed_objects=ignore_failed_objects, 
                                               model_directory=model_directory)
