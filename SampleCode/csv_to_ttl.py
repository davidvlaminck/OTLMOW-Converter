from datetime import datetime
from pathlib import Path

from otlmow_model.OtlmowModel.Classes.Onderdeel.Stroomkring import Stroomkring
from otlmow_model.OtlmowModel.Classes.Onderdeel.Verkeersregelaar import Verkeersregelaar
from otlmow_model.OtlmowModel.Classes.Onderdeel.Voedt import Voedt
from otlmow_model.OtlmowModel.Helpers import RelationCreator

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    otlmow_converter = OtlmowConverter()

    instance = Verkeersregelaar()
    instance.assetId.identificator = '00003707-0eeb-4c42-ba0a-0b590a7d00fb-b25kZXJkZWVsI1dlZ2thbnRrYXN0'
    instance.toestand = 'in-gebruik'
    instance.isActief = True
    instance.vplanNummer = 'V0123456'
    instance.theoretischeLevensduur.waarde = 240
    assets = [instance]

    s = Stroomkring()
    s.assetId.identificator = '000d3091-deca-4714-8f82-d95aace9ea90-b25kZXJkZWVsI1N0cm9vbWtyaW5n'

    instance.isActief = True

    assets = [RelationCreator.create_relation(source=s, target=instance, relation_type=Voedt)]

# export
    input_file_path = Path(f'Output/20260918132734_verkeersregelaar.json')
    assets = otlmow_converter.from_file_to_objects(file_path=input_file_path)
    file_path = Path(f'Output/{datetime.now().strftime("%Y%m%d%H%M%S")}_verkeersregelaar.ttl')
    otlmow_converter.to_file(file_path=file_path, subject=assets)
