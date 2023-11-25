from pathlib import Path

import geojson
import numpy as np

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.FileFormats.OtlAssetGeoJSONEncoder import OtlAssetGeoJSONEncoder
from otlmow_converter.FileFormats.TableExporter import TableExporter
from geojson import LineString, Point, MultiPoint, MultiLineString, Polygon, MultiPolygon, GeometryCollection


class GeoJSONExporter:
    def __init__(self, settings, model_directory: Path = None):
        self.settings = next(s for s in settings['file_formats'] if s['name'] == 'geojson')
        self.dotnotation_helper = DotnotationHelper(**self.settings['dotnotation'])
        self.encoder = OtlAssetGeoJSONEncoder(indent=4, settings=settings)
        if model_directory is None:
            model_directory = 'otlmow_model'
        self.table_exporter = TableExporter(dotnotation_settings=self.settings['dotnotation'],
                                            model_directory=model_directory)

    def export_to_file(self, filepath: Path, list_of_objects: list = None):
        list_of_dicts = self.convert_list_of_objects_to_list_of_geodicts(list_of_objects)

        fc = {
            'type': 'FeatureCollection',
            'features': list_of_dicts
        }

        encoded_json = self.encoder.encode(fc)
        self.encoder.write_json_to_file(encoded_json, filepath)

    def convert_list_of_objects_to_list_of_geodicts(self, list_of_objects):
        self.table_exporter.fill_master_dict(list_of_objects)

        l = []
        for k, assettype_data in self.table_exporter.master.items():
            for asset_dict in assettype_data['data']:
                geom = {}
                new_asset_dict = {}
                for k, v in asset_dict.items():
                    if v is None:
                        continue
                    if k == 'geometry':
                        geom = self.convert_wkt_string_to_geojson(v)
                        continue
                    if not isinstance(v, str):
                        new_asset_dict[k] = self.table_exporter._stringify_value(v)
                        if new_asset_dict[k] == 'True':
                            new_asset_dict[k] = 'true'
                        elif new_asset_dict[k] == 'False':
                            new_asset_dict[k] = 'false'
                    else:
                        new_asset_dict[k] = v
                asset_converted_dict = {
                    'id': new_asset_dict['assetId.identificator'],
                    'properties': new_asset_dict,
                    'type': 'Feature'}
                if geom != {}:
                    asset_converted_dict['geometry'] = geom
                l.append(asset_converted_dict)

        return l

    def convert_wkt_string_to_geojson(self, wkt_string):
        geom_type, coords_str = wkt_string.split('(', 1)
        coords_str = coords_str[:-1].replace(', ', ',').replace(' ,', ',')

        coords_list = []

        self.split_and_add_to_list(coords_list, coords_str)

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

        g = geojson.dumps(geom, sort_keys=True)
        return {
            'bbox': self.get_bounding_box(geom),
            'type': geom['type'],
            'coordinates': geom["coordinates"],
            'crs': {'properties': {'name': 'EPSG:31370'}, 'type': 'name'}}

    @staticmethod
    def get_bounding_box(geometry):
        coords = np.array(list(geojson.utils.coords(geometry)))
        if coords.shape[1] == 3:
            return [coords[:, 0].min(), coords[:, 1].min(), coords[:, 2].min(),
                    coords[:, 0].max(), coords[:, 1].max(), coords[:, 2].max()]
        else:
            return [[coords[:, 0].min(), coords[:, 1].min()], [coords[:, 0].max(), coords[:, 1].max()]]

    def split_and_add_to_list(self, coords_list: list, coords_str: str):
        if coords_str.startswith('('):
            coords_str = coords_str[1:-1]
            for new_coords_str in coords_str.split('),('):
                new_list = []
                self.split_and_add_to_list(coords_list=new_list, coords_str=new_coords_str)
                coords_list.append(new_list)
        else:
            for c in coords_str.split(','):
                x_y_z = tuple(float(co) for co in c.strip().split(' '))
                coords_list.append(x_y_z)
