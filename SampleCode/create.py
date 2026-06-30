from pathlib import Path

from otlmow_model.OtlmowModel.Classes.Onderdeel.DynBordRSS import DynBordRSS
from otlmow_model.OtlmowModel.Classes.Onderdeel.Omvormer import Omvormer
from otlmow_model.OtlmowModel.Classes.Onderdeel.Sturing import Sturing
from otlmow_model.OtlmowModel.Helpers.RelationCreator import create_relation

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    assets = []

    bord = DynBordRSS()
    bord.assetId.identificator = 'BORD_1'
    bord.naam = 'A01.1'
    bord.afmeting.vierhoekig.breedte.waarde = 1000
    bord.afmeting.vierhoekig.hoogte.waarde = 1500
    bord.toestand = 'in-gebruik'
    bord.ipAdres.waarde = '11.111.111.11'
    assets.append(bord)

    omv = Omvormer()
    omv.assetId.identificator = 'OMV_1'
    omv.toestand = 'in-gebruik'
    assets.append(omv)

    relation = create_relation(relation_type=Sturing, source=bord, target=omv)
    assets.append(relation)

    OtlmowConverter.from_objects_to_file(sequence_of_objects=assets, file_path=Path('assets_dyn_borden.json'))
