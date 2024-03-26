import inspect
import warnings
from pathlib import Path

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, OTLAttribuut, dynamic_create_instance_from_uri, \
    set_value_by_dictitem, get_attribute_by_name
from otlmow_model.OtlmowModel.Exceptions.NonStandardAttributeWarning import NonStandardAttributeWarning

from otlmow_converter.DotnotationDict import DotnotationDict
from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

load_settings()

SEPARATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['separator']
CARDINALITY_SEPARATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['cardinality_separator']
CARDINALITY_INDICATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['cardinality_indicator']
WAARDE_SHORTCUT = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['waarde_shortcut']


class DotnotationDictConverter:
    def __init__(self, separator: str = SEPARATOR, cardinality_separator: str = CARDINALITY_SEPARATOR,
                 cardinality_indicator: str = CARDINALITY_INDICATOR, waarde_shortcut: bool = WAARDE_SHORTCUT):
        self.separator: str = separator
        self.cardinality_separator: str = cardinality_separator
        self.cardinality_indicator: str = cardinality_indicator
        self.waarde_shortcut: bool = waarde_shortcut

    def to_dict_instance(self, otl_object: OTLObject, waarde_shortcut: bool = WAARDE_SHORTCUT,
                         separator: str = SEPARATOR,
                         cardinality_indicator: str = CARDINALITY_INDICATOR,
                         cardinality_separator: str = CARDINALITY_SEPARATOR,
                         datetime_as_string: bool = False, allow_non_otl_conform_attributes: bool = True,
                         warn_for_non_otl_conform_attributes: bool = True, list_as_string: bool = False
                         ) -> DotnotationDict[str, object]:
        return self.to_dict(otl_object=otl_object, waarde_shortcut=waarde_shortcut, separator=separator,
                            cardinality_indicator=cardinality_indicator, cardinality_separator=cardinality_separator,
                            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
                            list_as_string=list_as_string, datetime_as_string=datetime_as_string)

    @classmethod
    def to_dict(cls, otl_object: OTLObject, waarde_shortcut: bool = WAARDE_SHORTCUT, separator: str = SEPARATOR,
                cardinality_indicator: str = CARDINALITY_INDICATOR, cardinality_separator: str = CARDINALITY_SEPARATOR,
                datetime_as_string: bool = False, allow_non_otl_conform_attributes: bool = True,
                warn_for_non_otl_conform_attributes: bool = True, list_as_string: bool = False
                ) -> DotnotationDict[str, object]:
        return DotnotationDict(cls._iterate_over_attributes_and_values_by_dotnotation(
            object_or_attribute=otl_object, waarde_shortcut=waarde_shortcut, separator=separator,
            cardinality_indicator=cardinality_indicator, cardinality_separator=cardinality_separator,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
            list_as_string=list_as_string, datetime_as_string=datetime_as_string))

    @classmethod
    def _iterate_over_attributes_and_values_by_dotnotation(cls, object_or_attribute: OTLObject | OTLAttribuut,
                                                           waarde_shortcut: bool = WAARDE_SHORTCUT,
                                                           separator: str = SEPARATOR,
                                                           cardinality_indicator: str = CARDINALITY_INDICATOR,
                                                           cardinality_separator: str = CARDINALITY_SEPARATOR,
                                                           allow_non_otl_conform_attributes: bool = True,
                                                           warn_for_non_otl_conform_attributes: bool = True,
                                                           list_as_string: bool = False,
                                                           datetime_as_string: bool = False) -> (str, object):
        for attr_key, attribute in vars(object_or_attribute).items():
            if attr_key in {'_parent', '_valid_relations', '_geometry_types'}:
                continue
            if not isinstance(attribute, OTLAttribuut):
                yield from cls.handle_non_conform_attribute(allow_non_otl_conform_attributes, attr_key, attribute,
                                                            object_or_attribute, warn_for_non_otl_conform_attributes)
                continue
            if attribute.waarde is None:
                continue

            if attribute.field.waardeObject is None:
                dotnotation = DotnotationHelper.get_dotnotation(
                    attribute, waarde_shortcut=waarde_shortcut, separator=separator,
                    cardinality_indicator=cardinality_indicator)
                if list_as_string:
                    yield dotnotation, cardinality_separator.join(str(a) for a in attribute.waarde)
                elif datetime_as_string:
                    yield dotnotation, attribute.field.value_default(attribute.waarde)
                else:
                    yield dotnotation, attribute.waarde
            elif attribute.kardinaliteit_max != '1':
                combined_dict: dict[str, list] = {}
                for index, lijst_item in enumerate(attribute.waarde):
                    for k1, v1 in cls._iterate_over_attributes_and_values_by_dotnotation(
                            object_or_attribute=lijst_item, waarde_shortcut=waarde_shortcut, separator=separator,
                            cardinality_indicator=cardinality_indicator):
                        if k1 not in combined_dict:
                            combined_dict[k1] = [None for _ in range(index)]
                        combined_dict[k1].append(v1)

                    for lijst in combined_dict.values():
                        if len(lijst) < index + 1:
                            lijst.append(None)
                if list_as_string:
                    for k, v in combined_dict.items():
                        yield k, cardinality_separator.join(str(a) for a in v)
                else:
                    yield from combined_dict.items()
            else:
                yield from cls._iterate_over_attributes_and_values_by_dotnotation(
                    object_or_attribute=attribute.waarde,
                    waarde_shortcut=waarde_shortcut,
                    separator=separator,
                    cardinality_indicator=cardinality_indicator,
                )

    @classmethod
    def handle_non_conform_attribute(cls, allow_non_otl_conform_attributes, attr_key, attribute, object_or_attribute,
                                     warn_for_non_otl_conform_attributes):
        if attr_key.startswith('_'):
            raise ValueError(
                f'{attr_key} is a non standardized attribute of {object_or_attribute.__class__.__name__}. While this is supported, the key can not start with "_".')
        if not allow_non_otl_conform_attributes:
            raise ValueError(
                f'{attr_key} is a non standardized attribute of {object_or_attribute.__class__.__name__}. If you want to allow this, set allow_non_otl_conform_attributes to True.')
        if warn_for_non_otl_conform_attributes:
            warnings.warn(
                message=f'{attr_key} is a non standardized attribute of {object_or_attribute.__class__.__name__}. The attribute will be added on the instance.',
                stacklevel=2,
                category=NonStandardAttributeWarning)
        if attribute is not None:
            yield attr_key, attribute

    @classmethod
    def from_dict(cls, input_dict: DotnotationDict, model_directory: Path = None,
                  list_as_string: bool = False, datetime_as_string: bool = False,
                  allow_non_otl_conform_attributes: bool = True, warn_for_non_otl_conform_attributes: bool = True,
                  waarde_shortcut: bool = WAARDE_SHORTCUT,
                  separator: str = SEPARATOR,
                  cardinality_indicator: str = CARDINALITY_INDICATOR,
                  cardinality_separator: str = CARDINALITY_SEPARATOR,
                  ) -> OTLObject:
        type_uri = input_dict.get('typeURI')
        if type_uri is None:
            raise ValueError('typeURI is None. Add a valid typeURI to the input dictionary.')

        if model_directory is None:
            otl_object_file = inspect.getfile(OTLObject)
            model_directory = Path(otl_object_file).parent.parent.parent

        try:
            o = dynamic_create_instance_from_uri(str(type_uri), model_directory=model_directory)
        except TypeError:
            raise ValueError('typeURI is invalid. Add a valid typeURI to the input dictionary.')

        for k, v in input_dict.items():
            if k == 'typeURI':
                continue
            if k.startswith('_'):
                raise ValueError(f'{k} is a non standardized attribute of {o.__class__.__name__}. '
                                 f'While this is supported, the key can not start with "_".')
            cls.set_attribute_by_dotnotation(o, dotnotation=k, value=v, waarde_shortcut=waarde_shortcut,
                                             datetime_as_string=datetime_as_string, list_as_string=list_as_string,
                                             allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                             warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

        return o

    @classmethod
    def set_attribute_by_dotnotation(cls, object_or_attribute: OTLObject | OTLAttribuut,
                                     dotnotation: str, value: object,
                                     separator: str = SEPARATOR, cardinality_indicator: str = CARDINALITY_INDICATOR,
                                     waarde_shortcut: bool = WAARDE_SHORTCUT,
                                     cardinality_separator: str = CARDINALITY_SEPARATOR,
                                     convert: bool = True, convert_warnings: bool = True,
                                     datetime_as_string: bool = False,
                                     list_as_string: bool = False,
                                     allow_non_otl_conform_attributes: bool = True,
                                     warn_for_non_otl_conform_attributes: bool = True):
        if cardinality_separator in dotnotation:
            raise ValueError("can't use cardinality separator in dotnotation")

        if dotnotation.count(cardinality_indicator) > 1:
            raise ValueError("can't use dotnotation for lists of lists")

        if dotnotation.startswith('_'):
            raise ValueError(
                f'{dotnotation} is a non standardized attribute of {object_or_attribute.__class__.__name__}. '
                f'While this is supported, the key can not start with "_".')

        if separator not in dotnotation:
            cardinality = False
            if dotnotation.endswith(cardinality_indicator):
                dotnotation = dotnotation[:-2]
                cardinality = True

            attribute = get_attribute_by_name(object_or_attribute, dotnotation)
            if attribute is None:
                if not allow_non_otl_conform_attributes:
                    raise ValueError(
                        f'{dotnotation} is a non standardized attribute of {object_or_attribute.__class__.__name__}. '
                        f'If you want to allow this, set allow_non_otl_conform_attributes to True.')
                if warn_for_non_otl_conform_attributes:
                    warnings.warn(
                        message=f'{dotnotation} is a non standardized attribute of {object_or_attribute.__class__.__name__}. The attribute will be added on the instance.',
                        stacklevel=2,
                        category=NonStandardAttributeWarning)
                setattr(object_or_attribute, dotnotation, value)
                return
            if cardinality and list_as_string:
                value = value.split(cardinality_separator)

            if attribute.field.waarde_shortcut_applicable and waarde_shortcut:
                attribute.add_empty_value()
                attribute.waarde._waarde.set_waarde(value)
            else:
                attribute.set_waarde(value)
            return

        first, rest = dotnotation.split(separator, 1)
        cardinality = False
        if first.endswith(cardinality_indicator):
            first = first[:-2]
            cardinality = True
        attribute = get_attribute_by_name(object_or_attribute, first)
        if attribute is None:
            raise ValueError(f'{first} is not an attribute of {object_or_attribute.__class__.__name__}.')

        if attribute.waarde is None:
            attribute.add_empty_value()
        cls.set_attribute_by_dotnotation(attribute.waarde, dotnotation=rest, value=value, separator=separator,
                                         cardinality_indicator=cardinality_indicator,
                                         waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
                                         convert=convert, convert_warnings=convert_warnings)
        return

        if value == '':
            value = None

        if separator in dotnotation:
            first_part = dotnotation.split(separator)[0]
            rest = dotnotation.split(separator, 1)[1]

            if cardinality_indicator in first_part:
                first_part = first_part.replace(cardinality_indicator, '')
                attribute = get_attribute_by_name(instance_or_attribute, first_part)
                if value is None:
                    attribute.set_waarde(None)
                    return

                if not isinstance(value, list) and isinstance(value, str):
                    value = value.split(cardinality_separator)
                for index, v in enumerate(value):
                    if attribute.waarde is None or len(attribute.waarde) <= index:
                        attribute.add_empty_value()
                    DotnotationHelper.set_attribute_by_dotnotation(
                        attribute.waarde[index], dotnotation=rest, value=v,
                        separator=separator, cardinality_indicator=cardinality_indicator,
                        waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
                        convert=convert, convert_warnings=convert_warnings)
                return
            else:
                attribute = get_attribute_by_name(instance_or_attribute, first_part)
                if attribute.waarde is None:
                    attribute.add_empty_value()
                DotnotationHelper.set_attribute_by_dotnotation(
                    attribute.waarde, dotnotation=rest, value=value, convert=convert,
                    separator=separator, cardinality_indicator=cardinality_indicator,
                    waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
                    convert_warnings=convert_warnings)
                return

        else:
            cardinality = False
            if cardinality_indicator in dotnotation:
                dotnotation = dotnotation.replace(cardinality_indicator, '')
                cardinality = True

            attribute = get_attribute_by_name(instance_or_attribute, dotnotation)
            if value is None:
                if cardinality:
                    attribute.set_waarde([])
                else:
                    attribute.set_waarde(None)
                return

            if attribute.field.waarde_shortcut_applicable and waarde_shortcut:
                if attribute.waarde is None:
                    attribute.add_empty_value()
                if cardinality:
                    if not isinstance(value, list) and isinstance(value, str):
                        value = value.split(cardinality_separator)
                    if convert:
                        value = [attribute.waarde[0]._waarde.field.convert_to_correct_type(v, log_warnings=False)
                                 for v in value]
                    for index, v in enumerate(value):
                        if len(attribute.waarde) <= index:
                            attribute.add_empty_value()
                        attribute.waarde[index]._waarde.set_waarde(v)
                    return
                else:
                    if convert:
                        value = attribute.waarde._waarde.field.convert_to_correct_type(value, log_warnings=False)
                    attribute = attribute.waarde._waarde

            if cardinality:
                if not isinstance(value, list) and isinstance(value, str):
                    value = value.split(cardinality_separator)
                if convert:
                    value = [attribute.field.convert_to_correct_type(v, log_warnings=False) for v in value]
            elif convert:
                value = attribute.field.convert_to_correct_type(value, log_warnings=False)
            attribute.set_waarde(value)
            return
