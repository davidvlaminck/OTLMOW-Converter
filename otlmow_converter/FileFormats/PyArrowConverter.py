from typing import Iterable

import pyarrow as pa
from otlmow_model.OtlmowModel.Helpers.GenericHelper import get_shortened_uri

from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

load_settings()

SEPARATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['separator']
CARDINALITY_SEPARATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['cardinality_separator']
CARDINALITY_INDICATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['cardinality_indicator']
WAARDE_SHORTCUT = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['waarde_shortcut']

class PyArrowConverter:
    @classmethod
    def convert_objects_to_single_table(
            cls, list_of_objects: Iterable, waarde_shortcut: bool = WAARDE_SHORTCUT, separator: str = SEPARATOR,
            cardinality_separator: str = CARDINALITY_SEPARATOR, cardinality_indicator: str = CARDINALITY_INDICATOR,
            cast_list: bool = False, cast_datetime: bool = False, allow_non_otl_conform_attributes: bool = True,
            warn_for_non_otl_conform_attributes: bool = True, allow_empty_asset_id: bool = True,
            avoid_multiple_types_in_single_column: bool = False
    ) -> pa.Table:
        # Convert each object to a dotnotation dict
        dict_list = [DotnotationDictConverter.to_dict(
            otl_object=obj, cast_list=cast_list, cast_datetime=cast_datetime, waarde_shortcut=waarde_shortcut,
            separator=separator, cardinality_indicator=cardinality_indicator,
            cardinality_separator=cardinality_separator,
            collect_native_types=avoid_multiple_types_in_single_column,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
            for obj in list_of_objects]

        if not dict_list:
            return pa.table({})

        # Collect all keys in a single pass but remove the '_native_type_dict' key if present
        all_keys = sorted(set().union(*(d.keys() for d in dict_list)))
        if avoid_multiple_types_in_single_column:
            all_keys.remove('_native_type_dict')
            for d in dict_list:
                del d['_native_type_dict']  # Remove native types if present

        # Normalize dicts so all have all keys
        if any(len(d) != len(all_keys) for d in dict_list):
            normalized_dict_list = []
            for d in dict_list:
                if len(d) == len(all_keys):
                    normalized_dict_list.append(d)
                else:
                    normalized_dict_list.append({k: d.get(k, None) for k in all_keys})
            dict_list = normalized_dict_list

        # Build schema: auto-detect for all columns except the ones listed below
        if avoid_multiple_types_in_single_column:
            str_columns = {'aanleg','aansluitvermogen','aantalAdersEnSectie','afmeting','afmetingGrondvlak','afmetingen','appurtenanceType','armlengte','autonomie','beheeroptie','bijlage','brandweerstand','breedte','buitendiameter','code','communicatiewijze','detectieprincipe','diameter','diameterPaalschacht','diepte','dikte','droogzetbaarheid','fabrikant','foto','frequentierange','functie','gebruik','gewicht','hellingshoek','hoogte','hoogteBovenMaaiveld','kaliber','kleur','laagtype','lengte','licentie','lichtpuntHoogte','masthoogte','masttype','materiaal','maximaalDebiet','merk','modelnaam','nominaalVermogen','nominaleSpanning','ontwerpbelasting','opschrift','opstelHoogte','opstelling','paallengte','plaatsingswijze','productfamilie','protocol','rijrichting','rijstrook','schermelementtype','sluitkracht','soort','soortLamp','soortOmschrijving','spanning','subthema','totaleLengte','type','typeBevestiging','typeSpecificatie','uitvoering','uitvoeringsmethode','uitvoeringswijze','vermogen','vorm','vormgeving'}
            str_columns = {col for base in str_columns for col in (base, f"{base}[]")}
            for key in all_keys:
                if key in str_columns:
                    for d in dict_list:
                        if key in d and d[key] is not None and not isinstance(d[key], str):
                            d[key] = str(d[key])

        return pa.Table.from_pylist(dict_list)

    @classmethod
    def convert_objects_to_multiple_tables(cls, list_of_objects: Iterable, waarde_shortcut: bool = WAARDE_SHORTCUT, separator: str = SEPARATOR,
            cardinality_separator: str = CARDINALITY_SEPARATOR, cardinality_indicator: str = CARDINALITY_INDICATOR,
            cast_list: bool = False, cast_datetime: bool = False, allow_non_otl_conform_attributes: bool = True,
            warn_for_non_otl_conform_attributes: bool = True, allow_empty_asset_id: bool = True) -> dict[str, pa.Table]:
        from collections import defaultdict
        type_to_objs = defaultdict(list)
        for otl_object in list_of_objects:
            if otl_object.typeURI == 'http://purl.org/dc/terms/Agent':
                short_uri = 'Agent'
            else:
                short_uri = get_shortened_uri(otl_object.typeURI)
            type_to_objs[short_uri].append(otl_object)
        return {short_uri: cls.convert_objects_to_single_table(
            list_of_objects=objs, cast_list=cast_list, cast_datetime=cast_datetime, waarde_shortcut=waarde_shortcut,
            separator=separator, cardinality_indicator=cardinality_indicator,
            cardinality_separator=cardinality_separator,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
            for short_uri, objs in type_to_objs.items()}
