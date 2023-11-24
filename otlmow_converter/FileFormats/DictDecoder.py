from otlmow_model.OtlmowModel.BaseClasses.KeuzelijstField import KeuzelijstField
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import get_attribute_by_name, get_attribute_by_uri

from otlmow_converter.FileFormats.JsonLdContext import JsonLdContext
from otlmow_converter.FileFormats.JsonLdExporter import JsonLdExporter


# dict encoder = asset object to dict
# dict decoder = dict to asset object

class DictDecoder:
    @staticmethod
    def set_value_by_dictitem(instance_or_attribute, key, value, waarde_shortcut: bool = False, ld: bool = False, ld_context: dict={}):
        if not ld:
            attribute_to_set = get_attribute_by_name(instance_or_attribute, key)
        else:
            key = JsonLdContext.replace_context(key, context_dict=ld_context)
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
                            DictDecoder.set_value_by_dictitem(attribute_to_set.waarde[index], k, v, waarde_shortcut,
                                                              ld=ld, ld_context=ld_context)

            elif isinstance(value, dict):  # only complex / union possible
                if attribute_to_set.waarde is None:
                    attribute_to_set.add_empty_value()

                for k, v in value.items():
                    DictDecoder.set_value_by_dictitem(attribute_to_set.waarde, k, v, waarde_shortcut,
                                                      ld=ld, ld_context=ld_context)
            else:  # must be a dte / kwantWrd
                if attribute_to_set.waarde is None:
                    attribute_to_set.add_empty_value()

                attribute_to_set.waarde._waarde.set_waarde(value)
        else:
            if issubclass(attribute_to_set.field, KeuzelijstField):
                if attribute_to_set.kardinaliteit_max != '1':
                    value = [JsonLdContext.replace_context(list_item, context_dict=ld_context) for list_item in value]
                else:
                    value = JsonLdContext.replace_context(value, context_dict=ld_context)
            attribute_to_set.set_waarde(value)
