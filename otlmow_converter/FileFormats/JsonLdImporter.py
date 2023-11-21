from pathlib import Path

from otlmow_converter.FileFormats.JsonLdDecoder import JsonLdDecoder


class JsonLdImporter:
    def __init__(self, settings, model_directory: str = None):
        self.decoder = JsonLdDecoder(settings=settings, model_directory=model_directory)

    def import_file(self, filepath: Path, **kwargs) -> list:
        """Imports a json file created with Davie and decodes it to OTL objects

        :param filepath: location of the file, defaults to ''
        :type: str
        :rtype: list
        :return: returns a list of OTL objects
        """

        ignore_failed_objects = False

        if kwargs is not None:
            if 'ignore_failed_objects' in kwargs:
                ignore_failed_objects = kwargs['ignore_failed_objects']
            if 'model_directory' in kwargs:
                self.decoder.model_directory = kwargs['model_directory']

        with open(filepath, 'r') as file:
            data = file.read()
        return self.decoder.decode_json_string(data, ignore_failed_objects=ignore_failed_objects)
