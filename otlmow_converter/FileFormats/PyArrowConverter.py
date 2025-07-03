import pyarrow as pa
from otlmow_model.OtlmowModel.Helpers.GenericHelper import get_shortened_uri

from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter


class PyArrowConverter:
    @classmethod
    def convert_objects_to_single_table(cls, list_of_objects) -> pa.Table:
        # Convert each object to a dotnotation dict
        dict_list = [DotnotationDictConverter.to_dict(obj, cast_list=True, cast_datetime=True, waarde_shortcut=True) for obj in list_of_objects]

        if not dict_list:
            return pa.table({})

        # Collect all keys in a single pass
        all_keys = sorted(set().union(*(d.keys() for d in dict_list)))

        # Normalize dicts so all have all keys
        if any(len(d) != len(all_keys) for d in dict_list):
            normalized_dict_list = []
            for d in dict_list:
                if len(d) == len(all_keys):
                    normalized_dict_list.append(d)
                else:
                    normalized_dict_list.append({k: d.get(k, None) for k in all_keys})
            dict_list = normalized_dict_list

        # Build schema: auto-detect for all columns except 'aanleg' and 'aansluitvermogen'
        str_columns = {'aanleg','aansluitvermogen','aantalAdersEnSectie','afmeting','afmetingGrondvlak','afmetingen','appurtenanceType','armlengte','autonomie','beheeroptie','bijlage','brandweerstand','breedte','buitendiameter','code','communicatiewijze','detectieprincipe','diameter','diameterPaalschacht','diepte','dikte','droogzetbaarheid','fabrikant','foto','frequentierange','functie','gebruik','gewicht','hellingshoek','hoogte','hoogteBovenMaaiveld','kaliber','kleur','laagtype','lengte','licentie','lichtpuntHoogte','masthoogte','masttype','materiaal','maximaalDebiet','merk','modelnaam','nominaalVermogen','nominaleSpanning','ontwerpbelasting','opschrift','opstelHoogte','opstelling','paallengte','plaatsingswijze','productfamilie','protocol','rijrichting','rijstrook','schermelementtype','sluitkracht','soort','soortLamp','soortOmschrijving','spanning','subthema','totaleLengte','type','typeBevestiging','typeSpecificatie','uitvoering','uitvoeringsmethode','uitvoeringswijze','vermogen','vorm','vormgeving'}
        str_columns = {col for base in str_columns for col in (base, f"{base}[]")}
        for key in all_keys:
            if key in str_columns:
                for d in dict_list:
                    if key in d and d[key] is not None and not isinstance(d[key], str):
                        d[key] = str(d[key])

        return pa.Table.from_pylist(dict_list)

    @classmethod
    def convert_objects_to_multiple_tables(cls, list_of_objects) -> dict[str, pa.Table]:
        from collections import defaultdict
        type_to_objs = defaultdict(list)
        for otl_object in list_of_objects:
            if otl_object.typeURI == 'http://purl.org/dc/terms/Agent':
                short_uri = 'Agent'
            else:
                short_uri = get_shortened_uri(otl_object.typeURI)
            type_to_objs[short_uri].append(otl_object)
        return {short_uri: cls.convert_objects_to_single_table(objs) for short_uri, objs in type_to_objs.items()}
