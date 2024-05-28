from pathlib import Path

from otlmow_model.OtlmowModel.Classes.Onderdeel.Armatuurcontroller import Armatuurcontroller
from otlmow_model.OtlmowModel.Classes.Onderdeel.Bevestiging import Bevestiging
from otlmow_model.OtlmowModel.Classes.Onderdeel.HoortBij import HoortBij
from otlmow_model.OtlmowModel.Classes.Onderdeel.LEDDriver import LEDDriver
from otlmow_model.OtlmowModel.Classes.Onderdeel.Segmentcontroller import Segmentcontroller
from otlmow_model.OtlmowModel.Classes.Onderdeel.Sturing import Sturing
from otlmow_model.OtlmowModel.Classes.Onderdeel.VerlichtingstoestelLED import VerlichtingstoestelLED
from otlmow_model.OtlmowModel.Classes.Onderdeel.VoedtAangestuurd import VoedtAangestuurd
from otlmow_model.OtlmowModel.Classes.Onderdeel.WVLichtmast import WVLichtmast
from otlmow_model.OtlmowModel.Helpers.RelationCreator import create_relation

from otlmow_converter.OtlmowConverter import OtlmowConverter

segc_id = '37b57977-5839-45fa-9574-05793652a551'
segc_uri = 'https://lgc.data.wegenenverkeer.be/ns/installatie#SegC'
segc_sn = 'APS-G3-2019-053'

mast_1_id = '5cbef4a5-cb91-4b20-a6a4-143d6f6fbdd9'
mast_2_id = '4bf34578-91f9-4727-9a10-98c969fa78d1'
mast_uri = 'https://lgc.data.wegenenverkeer.be/ns/installatie#VPLMast'

ac_1_1_merk = 'smartnodes'
ac_1_2_merk = 'smartnodes'
ac_1_1_sn = 'SLC-G3-2020-5174'
ac_1_2_sn = 'SLC-G3-2018-1671'
mast_1_type = 'hoofdweg'

ac_2_1_merk = 'smartnodes'
ac_2_1_sn = 'SLC-G3-2020-5177'
mast_2_type = 'punctuele-verlichting'

assets_to_create = []

segmentcontroller = Segmentcontroller()
segmentcontroller.assetId.identificator = 'segc'
segmentcontroller.serienummer = segc_sn
segmentcontroller.naam = 'testCGI.LS.SC1'
assets_to_create.append(segmentcontroller)
assets_to_create.append(create_relation(source=segmentcontroller, target_uuid=segc_id, target_typeURI=segc_uri,
                                        relation_type=HoortBij))

mast_1 = WVLichtmast()
mast_1.aantalArmen = '2'
mast_1.naam = 'testCGI.1'
mast_1.assetId.identificator = 'mast_1'

assets_to_create.append(mast_1)

assets_to_create.append(create_relation(source=mast_1, target_uuid=mast_1_id, target_typeURI=mast_uri,
                                        relation_type=HoortBij))

led_1_1 = VerlichtingstoestelLED()
led_1_1.assetId.identificator = 'led_1_1'
led_1_1.naam = 'testCGI.1.WV1'
led_1_1.verlichtGebied = mast_1_type
assets_to_create.append(led_1_1)

assets_to_create.append(create_relation(source=mast_1, target=led_1_1, relation_type=Bevestiging))

led_1_2 = VerlichtingstoestelLED()
led_1_2.assetId.identificator = 'led_1_2'
led_1_2.naam = 'testCGI.1.WV2'
led_1_2.verlichtGebied = mast_1_type
assets_to_create.append(led_1_2)

assets_to_create.append(create_relation(source=mast_1, target=led_1_2, relation_type=Bevestiging))

driver_1_1 = LEDDriver()
driver_1_1.assetId.identificator = 'driver_1_1'
driver_1_1.naam = 'testCGI.1.WV1.LD1'
assets_to_create.append(driver_1_1)

assets_to_create.append(create_relation(source=led_1_1, target=driver_1_1, relation_type=Bevestiging))
assets_to_create.append(create_relation(source=led_1_1, target=driver_1_1, relation_type=Sturing))

driver_1_2 = LEDDriver()
driver_1_2.assetId.identificator = 'driver_1_2'
driver_1_2.naam = 'testCGI.1.WV2.LD1'
assets_to_create.append(driver_1_2)

assets_to_create.append(create_relation(source=led_1_2, target=driver_1_2, relation_type=Bevestiging))
assets_to_create.append(create_relation(source=led_1_2, target=driver_1_2, relation_type=Sturing))

ac_1_1 = Armatuurcontroller()
ac_1_1.assetId.identificator = 'ac_1_1'
ac_1_1.merk = ac_1_1_merk
ac_1_1.naam = 'testCGI.1.WV1.AC1'
ac_1_1.serienummer = ac_1_1_sn
assets_to_create.append(ac_1_1)

assets_to_create.append(create_relation(source=led_1_1, target=ac_1_1, relation_type=Bevestiging))
assets_to_create.append(create_relation(source=ac_1_1, target=driver_1_1, relation_type=VoedtAangestuurd))

ac_1_2 = Armatuurcontroller()
ac_1_2.assetId.identificator = 'ac_1_2'
ac_1_2.merk = ac_1_2_merk
ac_1_2.naam = 'testCGI.1.WV2.AC1'
ac_1_2.serienummer = ac_1_2_sn
assets_to_create.append(ac_1_2)

assets_to_create.append(create_relation(source=led_1_2, target=ac_1_2, relation_type=Bevestiging))
assets_to_create.append(create_relation(source=ac_1_2, target=driver_1_2, relation_type=VoedtAangestuurd))

assets_to_create.append(create_relation(source=ac_1_1, target=segmentcontroller, relation_type=Sturing))
assets_to_create.append(create_relation(source=ac_1_2, target=segmentcontroller, relation_type=Sturing))


mast_2 = WVLichtmast()
mast_2.aantalArmen = '1'
mast_2.naam = 'testCGI.2'
mast_2.assetId.identificator = 'mast_2'
assets_to_create.append(mast_2)

assets_to_create.append(create_relation(source=mast_2, target_uuid=mast_2_id, target_typeURI=mast_uri,
                                        relation_type=HoortBij))

led_2_1 = VerlichtingstoestelLED()
led_2_1.assetId.identificator = 'led_2_1'
led_2_1.naam = 'testCGI.2.WV1'
led_2_1.verlichtGebied = mast_2_type
assets_to_create.append(led_2_1)

assets_to_create.append(create_relation(source=mast_2, target=led_2_1, relation_type=Bevestiging))

driver_2_1 = LEDDriver()
driver_2_1.assetId.identificator = 'driver_2_1'
driver_2_1.naam = 'testCGI.1.WV2.LD1'
assets_to_create.append(driver_2_1)

assets_to_create.append(create_relation(source=led_2_1, target=driver_2_1, relation_type=Bevestiging))
assets_to_create.append(create_relation(source=led_2_1, target=driver_2_1, relation_type=Sturing))

ac_2_1 = Armatuurcontroller()
ac_2_1.assetId.identificator = 'ac_2_1'
ac_2_1.merk = ac_2_1_merk
ac_2_1.naam = 'testCGI.1.WV1.AC1'
ac_2_1.serienummer = ac_2_1_sn
assets_to_create.append(ac_2_1)

assets_to_create.append(create_relation(source=led_2_1, target=ac_2_1, relation_type=Bevestiging))
assets_to_create.append(create_relation(source=ac_2_1, target=driver_2_1, relation_type=VoedtAangestuurd))

assets_to_create.append(create_relation(source=ac_2_1, target=segmentcontroller, relation_type=Sturing))

if __name__ == '__main__':
    OtlmowConverter.to_file(assets_to_create, Path('segc_tei.json'), split_per_type=False)
