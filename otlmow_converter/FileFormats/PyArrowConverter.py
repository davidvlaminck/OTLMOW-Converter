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

        # Pre-allocate a list of dicts with all keys, only if needed
        if all(len(d) == len(all_keys) for d in dict_list):
            # All dicts already have all keys, no need to normalize
            return pa.Table.from_pylist(dict_list)
        else:
            # Only fill missing keys for dicts that need it
            normalized_dict_list = []
            for d in dict_list:
                if len(d) == len(all_keys):
                    normalized_dict_list.append(d)
                else:
                    normalized_dict_list.append({k: d.get(k, None) for k in all_keys})
            return pa.Table.from_pylist(normalized_dict_list)

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
