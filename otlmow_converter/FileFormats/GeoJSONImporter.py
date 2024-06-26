import json
from pathlib import Path
from typing import Iterable, List

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from otlmow_converter.AbstractImporter import AbstractImporter
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

load_settings()

geojson_settings = GlobalVariables.settings['formats']['GeoJSON']
geojson_dotnotation_settings = geojson_settings['dotnotation']
SEPARATOR = geojson_dotnotation_settings['separator']
CARDINALITY_SEPARATOR = geojson_dotnotation_settings['cardinality_separator']
CARDINALITY_INDICATOR = geojson_dotnotation_settings['cardinality_indicator']
WAARDE_SHORTCUT = geojson_dotnotation_settings['waarde_shortcut']
CAST_LIST = geojson_settings['cast_list']
CAST_DATETIME = geojson_settings['cast_datetime']
ALLOW_NON_OTL_CONFORM_ATTRIBUTES = geojson_settings['allow_non_otl_conform_attributes']
WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES = geojson_settings['warn_for_non_otl_conform_attributes']


class GeoJSONImporter(AbstractImporter):
    @classmethod
    def to_objects(cls, filepath: Path, **kwargs) -> Iterable[OTLObject]:
        """Imports a geojson file created with DAVIE and decodes it to OTL objects

        :param filepath: location of the file, defaults to ''
        :type: Path
        :rtype: list
        :return: returns a list of OTL objects
        """

        ignore_failed_objects = False

        if kwargs is not None and 'ignore_failed_objects' in kwargs:
            ignore_failed_objects = kwargs['ignore_failed_objects']

        separator = kwargs.get('separator', SEPARATOR)
        cardinality_separator = kwargs.get('cardinality_separator', CARDINALITY_SEPARATOR)
        cardinality_indicator = kwargs.get('cardinality_indicator', CARDINALITY_INDICATOR)
        waarde_shortcut = kwargs.get('waarde_shortcut', WAARDE_SHORTCUT)
        cast_list = kwargs.get('cast_list', CAST_LIST)
        cast_datetime = kwargs.get('cast_datetime', CAST_DATETIME)
        allow_non_otl_conform_attributes = kwargs.get('allow_non_otl_conform_attributes',
                                                      ALLOW_NON_OTL_CONFORM_ATTRIBUTES)
        warn_for_non_otl_conform_attributes = kwargs.get('warn_for_non_otl_conform_attributes',
                                                         WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES)

        with open(filepath) as file:
            data = json.load(file)

        model_directory = None
        if kwargs is not None and 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']

        return cls.decode_objects(data, ignore_failed_objects=ignore_failed_objects, model_directory=model_directory,
                                  separator=separator, cardinality_indicator=cardinality_indicator,
                                  waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
                                  cast_datetime=cast_datetime, cast_list=cast_list,
                                  allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                  warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

    @classmethod
    def decode_objects(cls, data, ignore_failed_objects: bool = False, model_directory: Path = None,
                       cast_list: bool = False, cast_datetime: bool = False,
                       allow_non_otl_conform_attributes: bool = True,
                       warn_for_non_otl_conform_attributes: bool = True,
                       waarde_shortcut: bool = WAARDE_SHORTCUT,
                       separator: str = SEPARATOR,
                       cardinality_indicator: str = CARDINALITY_INDICATOR,
                       cardinality_separator: str = CARDINALITY_SEPARATOR) -> List[OTLObject]:
        list_of_objects = []

        for data_object in data['features']:
            props = data_object['properties']
            if 'typeURI' not in props:
                if ignore_failed_objects:
                    continue
                raise ValueError('typeURI not found in properties')

            asset = DotnotationDictConverter.from_dict(
                input_dict=props, model_directory=model_directory, cast_list=cast_list, cast_datetime=cast_datetime,
                separator=separator, cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cardinality_separator=cardinality_separator,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

            if 'geometry' in data_object:
                geom = data_object['geometry']
                asset.geometry = cls.construct_wkt_string_from_geojson(geom)

            list_of_objects.append(asset)
        return list_of_objects

    @classmethod
    def construct_wkt_string_from_geojson(cls, geom):
        geo_type = geom['type']
        coords = geom['coordinates']

        first_coord = coords
        while isinstance(first_coord[0], list):
            first_coord = first_coord[0]

        z_part = ' Z' if len(first_coord) == 3 else ''
        return geo_type.upper() + z_part + ' ' + cls.construct_wkt_string_from_coords(coords)

    @classmethod
    def construct_wkt_string_from_coords(cls, coords):
        wkt = ''
        if not isinstance(coords[0], list):
            return f'({cls.construct_wkt_string_from_coord(coords)})'
        for coord in coords:
            if isinstance(coords[0][0], list):
                wkt += f'{cls.construct_wkt_string_from_coords(coord)}, '
            else:
                wkt += f'{cls.construct_wkt_string_from_coord(coord)}, '
        return f'({wkt[:-2]})'

    @classmethod
    def construct_wkt_string_from_coord(cls, coord):
        wkt = ''.join(f'{str(c)} ' for c in coord)
        return wkt[:-1]
