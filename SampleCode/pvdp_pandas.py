from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    otlmow_converter = OtlmowConverter()

    d_dicts = otlmow_converter.to_dotnotation_dicts(Path('DA-2024-22964_export.csv'))

    objects = []
    heeft_betrokkenes = []
    hoort_bijs = []
    allowed_types = {'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Beschermbuis',
                     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#TechnischePut',
                     'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Telecomkabel',
                     'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#TelecommunicationsCable'}
    for d_dict in d_dicts:
        if d_dict['typeURI'] in allowed_types:
            objects.append(d_dict)
        elif d_dict['typeURI'] == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBetrokkene':
            heeft_betrokkenes.append(d_dict)
        elif d_dict['typeURI'] == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HoortBij':
            hoort_bijs.append(d_dict)

    df_asset = otlmow_converter.to_dataframe(objects)
    df_heeft_betrokkene = otlmow_converter.to_dataframe(heeft_betrokkenes)
    df_hoort_bij = otlmow_converter.to_dataframe(heeft_betrokkenes)

    print(df_asset)
    print(df_heeft_betrokkene)
    print(df_hoort_bij)
