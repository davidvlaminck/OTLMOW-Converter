from otlmow_converter.FileFormats.JsonLdDecoder import JsonLdDecoder


class JsonLdImporter:
    def __init__(self, settings):
        self.decoder = JsonLdDecoder(settings=settings)

    def import_file(self, filepath: str = '', **kwargs) -> list:
        """Imports a json file created with Davie and decodes it to OTL objects

        :param filepath: location of the file, defaults to ''
        :type: str
        :rtype: list
        :return: returns a list of OTL objects
        """

        ignore_failed_objects = False
        class_directory = None

        if kwargs is not None:
            if 'ignore_failed_objects' in kwargs:
                ignore_failed_objects = kwargs['ignore_failed_objects']
            if 'class_directory' in kwargs:
                class_directory = kwargs['class_directory']

        with open(filepath, 'r') as file:
            data = file.read()
        return self.decoder.decode_json_string(data, ignore_failed_objects=ignore_failed_objects,
                                               classes_directory=class_directory)
