import json
from pathlib import Path

from otlmow_model.Helpers.AssetCreator import dynamic_create_instance_from_uri

from otlmow_converter.DotnotationHelper import DotnotationHelper


class GeoJSONImporter:
    def __init__(self, settings):
        self.settings = next(s for s in settings['file_formats'] if s['name'] == 'geojson')

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

    def decode_objects(self, data, ignore_failed_objects: bool = False, class_directory: str = None):
        list_of_objects = []
        settings_wsc = self.settings['dotnotation']['waarde_shortcut']
        settings_sep = self.settings['dotnotation']['separator']
        settings_card = self.settings['dotnotation']['cardinality_indicator']

        for data_object in data['features']:
            props = data_object['properties']
            if 'typeURI' not in props:
                if ignore_failed_objects:
                    continue
                raise ValueError('typeURI not found in properties')

            asset = dynamic_create_instance_from_uri(props['typeURI'], directory=class_directory)
            for dotnotation in props:
                if dotnotation == 'typeURI':
                    continue

                DotnotationHelper.set_attribute_by_dotnotation(
                    instance_or_attribute=asset, dotnotation=dotnotation, value=props[dotnotation],
                    waarde_shortcut=settings_wsc, separator=settings_sep,
                    cardinality_indicator=settings_card)

            if 'geometry' in data_object:
                geom = data_object['geometry']
                asset.geometry = self.construct_wkt_string_from_geojson(geom)

            list_of_objects.append(asset)
        return list_of_objects

    def construct_wkt_string_from_geojson(self, geom):
        geo_type = geom['type']
        coords = geom['coordinates']
        z_part = ''
        if len(coords[0]) == 3:
            z_part = ' Z'
        
        wkt = geo_type.upper() + z_part + ' (' + self.construct_wkt_string_from_coords(coords) + ')'
        return wkt

    def construct_wkt_string_from_coords(self, coords):
        wkt = ''
        for coord in coords:
            wkt += self.construct_wkt_string_from_coord(coord) + ', '
        return wkt[:-2]

    def construct_wkt_string_from_coord(self, coord):
        wkt = ''
        for c in coord:
            wkt += str(c) + ' '
        return wkt[:-1]
