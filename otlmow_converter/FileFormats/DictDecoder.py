def get_attribute_by_uri(instance_or_attribute, key: str,):
    for k, v in vars(instance_or_attribute).items():
        if k in ['_parent', '_geometry_types', '_valid_relations']:
            continue

        if v.objectUri == key:
            return v


def get_attribute_by_name(instance_or_attribute, key: str):
    attribute_to_set = getattr(instance_or_attribute, '_' + key)
    return attribute_to_set


class DictDecoder:
    @staticmethod
    def set_value_by_dictitem(instance_or_attribute, key, value, waarde_shortcut: bool = False, ld: bool = False):
        if not ld:
            attribute_to_set = get_attribute_by_name(instance_or_attribute, key)
        else:
            attribute_to_set = get_attribute_by_uri(instance_or_attribute, key)
        if attribute_to_set.field.waardeObject is not None:  # complex / union / KwantWrd / dte

            if isinstance(value, list):
                for index, list_item in enumerate(value):
                    if attribute_to_set.waarde is None or len(attribute_to_set.waarde) <= index:
                        attribute_to_set.add_empty_value()

                    if attribute_to_set.field.waarde_shortcut_applicable and waarde_shortcut:  # dte / kwantWrd
                        attribute_to_set.waarde[index]._waarde.set_waarde(list_item)
                    else:  # complex / union
                        for k, v in list_item.items():
                            DictDecoder.set_value_by_dictitem(attribute_to_set.waarde[index], k, v, waarde_shortcut, ld=ld)

            elif isinstance(value, dict):  # only complex / union possible
                if attribute_to_set.waarde is None:
                    attribute_to_set.add_empty_value()

                for k, v in value.items():
                    DictDecoder.set_value_by_dictitem(attribute_to_set.waarde, k, v, waarde_shortcut, ld=ld)
            else:  # must be a dte / kwantWrd
                if attribute_to_set.waarde is None:
                    attribute_to_set.add_empty_value()

                attribute_to_set.waarde._waarde.set_waarde(value)
        else:
            attribute_to_set.set_waarde(value)
