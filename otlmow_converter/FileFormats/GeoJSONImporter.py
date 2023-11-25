import json
from pathlib import Path

from otlmow_model.OtlmowModel.Helpers.AssetCreator import dynamic_create_instance_from_uri

from otlmow_converter.DotnotationHelper import DotnotationHelper


class GeoJSONImporter:
    def __init__(self, settings):
        self.settings = next(s for s in settings['file_formats'] if s['name'] == 'geojson')
        self.dotnotation_helper = DotnotationHelper(**self.settings['dotnotation'])

    def import_file(self, filepath: Path = None, **kwargs) -> list:
        """Imports a json file created with Davie and decodes it to OTL objects

        :param filepath: location of the file, defaults to ''
        :type: Path
        :rtype: list
        :return: returns a list of OTL objects
        """

        ignore_failed_objects = False

        if kwargs is not None:
            if 'ignore_failed_objects' in kwargs:
                ignore_failed_objects = kwargs['ignore_failed_objects']

        with open(filepath, 'r') as file:
            data = json.load(file)

        return self.decode_objects(data, ignore_failed_objects=ignore_failed_objects)

    def decode_objects(self, data, ignore_failed_objects: bool = False, model_directory: Path = None):
        list_of_objects = []

        for data_object in data['features']:
            props = data_object['properties']
            if 'typeURI' not in props:
                if ignore_failed_objects:
                    continue
                raise ValueError('typeURI not found in properties')

            asset = dynamic_create_instance_from_uri(props['typeURI'], model_directory=model_directory)
            for dotnotation in props:
                if dotnotation == 'typeURI':
                    continue

                self.dotnotation_helper.set_attribute_by_dotnotation_instance(
                    instance_or_attribute=asset, dotnotation=dotnotation, value=props[dotnotation])

            if 'geometry' in data_object:
                geom = data_object['geometry']
                asset.geometry = self.construct_wkt_string_from_geojson(geom)

            list_of_objects.append(asset)
        return list_of_objects

    def construct_wkt_string_from_geojson(self, geom):
        geo_type = geom['type']
        coords = geom['coordinates']

        first_coord = coords
        while isinstance(first_coord[0], list):
            first_coord = first_coord[0]

        z_part = ''
        if len(first_coord) == 3:
            z_part = ' Z'
        
        wkt = geo_type.upper() + z_part + ' ' + self.construct_wkt_string_from_coords(coords)
        return wkt

    def construct_wkt_string_from_coords(self, coords):
        wkt = ''
        if not isinstance(coords[0], list):
            return '(' + self.construct_wkt_string_from_coord(coords) + ')'
        for coord in coords:
            if isinstance(coords[0][0], list):
                wkt += self.construct_wkt_string_from_coords(coord) + ', '
            else:
                wkt += self.construct_wkt_string_from_coord(coord) + ', '
        return '(' + wkt[:-2] + ')'

    def construct_wkt_string_from_coord(self, coord):
        wkt = ''
        for c in coord:
            wkt += str(c) + ' '
        return wkt[:-1]
