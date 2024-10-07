from json import JSONEncoder
from pathlib import Path
from typing import Iterable

import geojson
import numpy as np
from geojson import LineString, Point, MultiPoint, MultiLineString, Polygon, MultiPolygon, GeometryCollection
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from otlmow_converter.AbstractExporter import AbstractExporter
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


class GeoJSONExporter(AbstractExporter):
    @classmethod
    def from_dotnotation_dicts(cls, sequence_of_dotnotation_dicts: Iterable[dict], filepath: Path) -> None:
        list_of_objects = []
        for d in sequence_of_dotnotation_dicts:
            feature_dict = {
                'id': d['assetId.identificator'],
                'properties': d,
                'type': 'Feature'}

            geometry = d.get('geometry', None)
            if geometry is not None:
                geom = cls.convert_wkt_string_to_geojson(d.pop("geometry"))
                feature_dict['geometry'] = geom

            list_of_objects.append(feature_dict)

        fc = {
            'type': 'FeatureCollection',
            'features': list_of_objects
        }
        encoded_json = JSONEncoder(indent=4).encode(fc)

        with open(filepath, "w") as file:
            file.write(encoded_json)

    @classmethod
    def from_objects(cls, sequence_of_objects: Iterable[OTLObject], filepath: Path, **kwargs) -> None:
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

        cls.from_dotnotation_dicts(
            [DotnotationDictConverter.to_dict(
                asset, separator=separator, cardinality_indicator=cardinality_indicator,
                waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
                cast_datetime=cast_datetime, cast_list=cast_list,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
                for asset in sequence_of_objects], filepath=filepath)

    @classmethod
    def convert_wkt_string_to_geojson(cls, wkt_string: str):
        geom_type, coords_str = wkt_string.split('(', 1)
        coords_str = coords_str[:-1].replace(', ', ',').replace(' ,', ',')

        coords_list = []

        cls.split_and_add_to_list(coords_list, coords_str)

        geom_type = geom_type.lower()
        if geom_type.startswith('point'):
            geom = Point(tuple(coords_list))
        elif geom_type.startswith('linestring'):
            geom = LineString(tuple(coords_list))
        elif geom_type.startswith('multipoint'):
            geom = MultiPoint(tuple(coords_list))
        elif geom_type.startswith('multilinestring'):
            geom = MultiLineString(tuple(coords_list))
        elif geom_type.startswith('polygon'):
            geom = Polygon(tuple(coords_list))
        elif geom_type.startswith('multipolygon'):
            geom = MultiPolygon(tuple(coords_list))
        elif geom_type.startswith('geometrycollection'):
            geom = GeometryCollection(tuple(coords_list))
        else:
            raise NotImplementedError(f'Geometry type {geom_type} not implemented')

        if geom_type.startswith('point'):
            return {
                'bbox': cls.get_bounding_box(geom),
                'type': geom['type'],
                'coordinates': geom["coordinates"][0],
                'crs': {'properties': {'name': 'EPSG:31370'}, 'type': 'name'}}

        return {
            'bbox': cls.get_bounding_box(geom),
            'type': geom['type'],
            'coordinates': geom["coordinates"],
            'crs': {'properties': {'name': 'EPSG:31370'}, 'type': 'name'}}

    @classmethod
    def get_bounding_box(cls, geometry):
        coords = np.array(list(geojson.utils.coords(geometry)))
        if coords.shape[1] == 3:
            return [coords[:, 0].min(), coords[:, 1].min(), coords[:, 2].min(),
                    coords[:, 0].max(), coords[:, 1].max(), coords[:, 2].max()]
        else:
            return [[coords[:, 0].min(), coords[:, 1].min()], [coords[:, 0].max(), coords[:, 1].max()]]

    @classmethod
    def split_and_add_to_list(cls, coords_list: list, coords_str: str):
        if coords_str.startswith('('):
            coords_str = coords_str[1:-1]
            for new_coords_str in coords_str.split('),('):
                new_list = []
                cls.split_and_add_to_list(coords_list=new_list, coords_str=new_coords_str)
                coords_list.append(new_list)
        else:
            for c in coords_str.split(','):
                x_y_z = tuple(float(co) for co in c.strip().split(' '))
                coords_list.append(x_y_z)
