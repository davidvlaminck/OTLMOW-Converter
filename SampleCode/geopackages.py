from geopandas import GeoDataFrame
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import dynamic_create_instance_from_uri
from shapely import wkt

from otlmow_converter.FileFormats.PandasConverter import PandasConverter
from otlmow_converter.OtlmowConverter import OtlmowConverter

uris = {
    'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Geleideconstructie',
    'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#GetesteBeginconstructie',
    'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#NietGetestBeginstuk',
    'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#NietConformBegin',
    'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Motorvangplank',
    'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Obstakelbeveiliger',
    'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#SchampkantAfw',
    'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#SchampkantStd',
}

if __name__ == '__main__':
    otlmow_converter = OtlmowConverter()
    assets = [dynamic_create_instance_from_uri(uri) for uri in uris]
    for asset in assets:
        asset.fill_with_dummy_data()
    pandas_converter = PandasConverter(settings = otlmow_converter.settings)
    multi_df = pandas_converter.convert_objects_to_multiple_dataframes(list_of_objects=assets)

    for uri, df in multi_df.items():  # iterate over the dataframes
        df['geometry'] = df.geometry.apply(wkt.loads)  # load the wkt string as a geometry in the same column
        gdf = GeoDataFrame(df, geometry='geometry')  # load the DataFrame as a GeoDataFrame
        gdf = gdf[:0]  # remove the dummy row
        gdf.to_file('Output/lijnvormige_elementen.gpkg', driver='GPKG', layer=uri.split('#')[-1])
