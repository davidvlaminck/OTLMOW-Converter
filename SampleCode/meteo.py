import json
from pathlib import Path

from otlmow_model.Classes.Onderdeel.Bevestiging import Bevestiging
from otlmow_model.Classes.Onderdeel.HoortBij import HoortBij
from otlmow_model.Helpers.GenericHelper import print_overview_assets

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.RelationCreator import create_relation


def simplify_asset_data_set():
    with open(Path('/home/davidlinux/Documents/AWV/DA-2022-00914_export (3).json'), 'r') as file:
        data = file.read()
    other_json = json.loads(data)
    other_hoortbij = []
    for d in other_json['@graph']:
        if d['@type'] == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HoortBij':
            instance = HoortBij()
            other_hoortbij.append(instance)
            instance.assetId.identificator = d['RelatieObject.assetId']['DtcIdentificator.identificator']
            instance.bronAssetId.identificator = d['RelatieObject.bronAssetId']['DtcIdentificator.identificator']
            instance.doelAssetId.identificator = d['RelatieObject.doelAssetId']['DtcIdentificator.identificator']

    converter = OtlmowConverter()

    assets = converter.create_assets_from_file(Path('/home/davidlinux/Documents/AWV/meteo.json'))
    sensoren = list(
        filter(
            lambda a: a.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Wegdeksensor' and a.isActief,
            assets))
    meetstation = list(
        filter(lambda
                   a: a.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Meetstation' and a.isActief,
               assets))
    rechtesteunen = list(
        filter(
            lambda a: a.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#RechteSteun' and a.isActief,
            assets))
    alle_hoortbij = list(
        filter(lambda a: a.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HoortBij' and a.isActief,
               assets))

    alle_hoortbij.extend(other_hoortbij)

    meteo_lgc_uuids = set()
    for sensor in sensoren:
        hoortbij = list(filter(
            lambda h: h.bronAssetId.identificator == sensor.assetId.identificator and
                      not h.doelAssetId.identificator.endswith('aW5zdGFsbGF0aWUjTWVldHN0YXRpb24'), alle_hoortbij)) # meetstation
        if len(hoortbij) == 1:
            meteo_lgc_uuids.add(hoortbij[0].doelAssetId.identificator)

    print(len(meteo_lgc_uuids))
    filtered_rechte_steunen = []
    for meteo_lgc_uuid in meteo_lgc_uuids:
        print(meteo_lgc_uuid)
        hoortbij = list(filter(
            lambda h: h.doelAssetId.identificator == meteo_lgc_uuid and
                      h.bronAssetId.identificator.endswith('b25kZXJkZWVsI1JlY2h0ZVN0ZXVu'), alle_hoortbij))
        if len(hoortbij) == 1:
            steun = list(filter(lambda a: a.assetId.identificator == hoortbij[0].bronAssetId.identificator,
                                rechtesteunen))
            filtered_rechte_steunen.append(steun[0])
            print('found one')
        else:
            print("didn't find one")

    sensoren.extend(alle_hoortbij)
    sensoren.extend(meetstation)
    sensoren.extend(filtered_rechte_steunen)

    converter.create_file_from_assets(filepath=Path('/home/davidlinux/Documents/AWV/meteo_simplified.xlsx'),
                                      list_of_objects=sensoren)


if __name__ == '__main__':
    # simplify_asset_data_set()
    converter = OtlmowConverter()
    assets = converter.create_assets_from_file(Path('/home/davidlinux/Documents/AWV/meteo_simplified.xlsx'))
    print_overview_assets(assets)

    nieuwe_relaties = []
    meetstations = list(filter(lambda a: a.isActief and
                    a.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Meetstation', assets))
    rechte_steunen = list(filter(lambda a: a.isActief and
                    a.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#RechteSteun', assets))
    hoortbijs = list(filter(lambda a: a.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HoortBij', assets))

    for meetstation in meetstations:
        print(meetstation.naam)
        hoortbijs_meetstation = list(filter(lambda h: h.doelAssetId.identificator == meetstation.assetId.identificator,
                                            hoortbijs))
        print(len(hoortbijs_meetstation))

        meteo_legacy_ids = set()
        for hoortbij_meetstation in hoortbijs_meetstation:
            hoortbijs_meteo = list(filter(lambda h:
                h.bronAssetId.identificator == hoortbij_meetstation.bronAssetId.identificator and
                h.doelAssetId.identificator != meetstation.assetId.identificator, hoortbijs))
            for hoortbij_meteo in hoortbijs_meteo:
                meteo_legacy_ids.add(hoortbij_meteo.doelAssetId.identificator)

        if len(meteo_legacy_ids) == 0:
            continue

        meteo_legacy_id = meteo_legacy_ids.pop()
        print(meteo_legacy_id)

        hoortbijs_meteo_lgc = list(filter(
                lambda h: h.doelAssetId.identificator == meteo_legacy_id, hoortbijs))

        for hoortbij_meteo_lgc in hoortbijs_meteo_lgc:
            if not hoortbij_meteo_lgc.bronAssetId.identificator.endswith('b25kZXJkZWVsI1JlY2h0ZVN0ZXVu'):
                continue
            rechtesteun = list(filter(
                lambda r: r.assetId.identificator == hoortbij_meteo_lgc.bronAssetId.identificator, rechte_steunen))

            if len(rechtesteun) == 0:
                continue

            print(rechtesteun[0])
            paal = rechtesteun[0]

            if meetstation.naam[0:3] != 'MET':
                continue

            if meetstation.naam[4] == '2':
                relatie_te_leggen = create_relation(source=rechtesteun[0], target=meetstation, relation_type=Bevestiging)
                nieuwe_relaties.append(relatie_te_leggen)
                print(relatie_te_leggen)
            elif meetstation.naam[4] == '1':
                relatie_te_leggen = create_relation(source=rechtesteun[0], target=meetstation, relation_type=HoortBij)
                nieuwe_relaties.append(relatie_te_leggen)
                print(relatie_te_leggen)

    print_overview_assets(nieuwe_relaties)
    converter.create_file_from_assets(filepath=Path('/home/davidlinux/Documents/AWV/nieuwe_relaties.xlsx'),
                                      list_of_objects=nieuwe_relaties)








