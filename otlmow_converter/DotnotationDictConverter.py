from __future__ import annotations

import inspect
import warnings
from pathlib import Path

from otlmow_model.OtlmowModel.BaseClasses.DateField import DateField
from otlmow_model.OtlmowModel.BaseClasses.DateTimeField import DateTimeField
from otlmow_model.OtlmowModel.BaseClasses.KeuzelijstField import KeuzelijstField
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, OTLAttribuut, dynamic_create_instance_from_uri, \
    get_attribute_by_name
from otlmow_model.OtlmowModel.BaseClasses.TimeField import TimeField
from otlmow_model.OtlmowModel.Exceptions.NonStandardAttributeWarning import NonStandardAttributeWarning

from otlmow_converter.DotnotationDict import DotnotationDict
from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError
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
                         separator: str = SEPARATOR, cardinality_indicator: str = CARDINALITY_SEPARATOR,
                         cardinality_separator: str = CARDINALITY_INDICATOR,
                         cast_datetime: bool = False, allow_non_otl_conform_attributes: bool = True,
                         warn_for_non_otl_conform_attributes: bool = True, cast_list: bool = False
                         ) -> DotnotationDict:
        if self.separator is not None:
            separator = self.separator
        if self.waarde_shortcut is not None:
            waarde_shortcut = self.waarde_shortcut
        if self.cardinality_indicator is not None:
            cardinality_indicator = self.cardinality_indicator
        if self.cardinality_separator is not None:
            cardinality_separator = self.cardinality_separator

        return self.to_dict(otl_object=otl_object, waarde_shortcut=waarde_shortcut, separator=separator,
                            cardinality_indicator=cardinality_indicator, cardinality_separator=cardinality_separator,
                            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
                            cast_list=cast_list, cast_datetime=cast_datetime)

    @classmethod
    def to_dict(cls, otl_object: OTLObject, waarde_shortcut: bool = WAARDE_SHORTCUT, separator: str = SEPARATOR,
                cardinality_indicator: str = CARDINALITY_INDICATOR, cardinality_separator: str = CARDINALITY_SEPARATOR,
                cast_datetime: bool = False, allow_non_otl_conform_attributes: bool = True,
                warn_for_non_otl_conform_attributes: bool = True, cast_list: bool = False
                ) -> DotnotationDict:
        type_uri = getattr(otl_object, 'typeURI', None)
        if type_uri is None:
            raise ValueError('typeURI is None. The object must have an attribute typeURI.')

        d = DotnotationDict(cls._iterate_over_attributes_and_values_by_dotnotation(
            object_or_attribute=otl_object, waarde_shortcut=waarde_shortcut, separator=separator,
            cardinality_indicator=cardinality_indicator, cardinality_separator=cardinality_separator,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
            cast_list=cast_list, cast_datetime=cast_datetime))
        d['typeURI'] = type_uri
        return d

    @classmethod
    def _iterate_over_attributes_and_values_by_dotnotation(cls, object_or_attribute: OTLObject | OTLAttribuut,
                                                           waarde_shortcut: bool = WAARDE_SHORTCUT,
                                                           separator: str = SEPARATOR,
                                                           cardinality_indicator: str = CARDINALITY_INDICATOR,
                                                           cardinality_separator: str = CARDINALITY_SEPARATOR,
                                                           allow_non_otl_conform_attributes: bool = True,
                                                           warn_for_non_otl_conform_attributes: bool = True,
                                                           cast_list: bool = False,
                                                           cast_datetime: bool = False) -> (str, object):
        for attr_key, attribute in vars(object_or_attribute).items():
            if attr_key in {'_parent', '_valid_relations', '_geometry_types'}:
                continue
            if not isinstance(attribute, OTLAttribuut):
                yield from cls.handle_non_conform_attribute(allow_non_otl_conform_attributes, attr_key, attribute,
                                                            object_or_attribute, warn_for_non_otl_conform_attributes)
                continue
            if attribute.waarde is None:
                if not attribute.mark_to_be_cleared:
                    continue

                dotnotation = DotnotationHelper.get_dotnotation(
                    attribute, waarde_shortcut=waarde_shortcut, separator=separator,
                    cardinality_indicator=cardinality_indicator)
                if attribute.kardinaliteit_max != '1':
                    yield dotnotation, '88888888'
                else:
                    yield dotnotation, attribute.field.clearing_value
                continue

            if attribute.field.waardeObject is None:
                dotnotation = DotnotationHelper.get_dotnotation(
                    attribute, waarde_shortcut=waarde_shortcut, separator=separator,
                    cardinality_indicator=cardinality_indicator)
                if dotnotation.count(cardinality_indicator) > 1:
                    raise DotnotationListOfListError(f'Can not use dotnotation for lists of lists. '
                                                     f'Dotnotation: {dotnotation}')
                if attribute.mark_to_be_cleared:
                    yield dotnotation, attribute.field.clearing_value

                if cast_list and attribute.kardinaliteit_max != '1':
                    yield dotnotation, cardinality_separator.join(str(a) for a in attribute.waarde)
                elif cast_datetime:
                    yield dotnotation, attribute.field.value_default(attribute.waarde)
                else:
                    yield dotnotation, attribute.waarde
            elif attribute.kardinaliteit_max != '1':
                combined_dict: dict[str, list] = {}
                for index, lijst_item in enumerate(attribute.waarde):
                    for k1, v1 in cls._iterate_over_attributes_and_values_by_dotnotation(
                            object_or_attribute=lijst_item, waarde_shortcut=waarde_shortcut, separator=separator,
                            cardinality_indicator=cardinality_indicator, cardinality_separator=cardinality_separator,
                            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
                            cast_list=cast_list, cast_datetime=cast_datetime):
                        if k1 not in combined_dict:
                            combined_dict[k1] = [None for _ in range(index)]
                        combined_dict[k1].append(v1)

                    for lijst in combined_dict.values():
                        if len(lijst) < index + 1:
                            lijst.append(None)
                if cast_list:
                    for k, v in combined_dict.items():
                        yield k, cardinality_separator.join(str(a) for a in v)
                else:
                    yield from combined_dict.items()
            else:
                yield from cls._iterate_over_attributes_and_values_by_dotnotation(
                    object_or_attribute=attribute.waarde, waarde_shortcut=waarde_shortcut, separator=separator,
                    cardinality_indicator=cardinality_indicator, cardinality_separator=cardinality_separator,
                    allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                    warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
                    cast_list=cast_list, cast_datetime=cast_datetime)

    @classmethod
    def handle_non_conform_attribute(cls, allow_non_otl_conform_attributes, attr_key, attribute, object_or_attribute,
                                     warn_for_non_otl_conform_attributes):
        if attr_key.startswith('_'):
            raise ValueError(
                f'{attr_key} is a non standardized attribute of {object_or_attribute.__class__.__name__}. '
                f'While this is supported, the key can not start with "_".')
        if not allow_non_otl_conform_attributes:
            raise ValueError(
                f'{attr_key} is a non standardized attribute of {object_or_attribute.__class__.__name__}. '
                f'If you want to allow this, set allow_non_otl_conform_attributes to True.')
        if warn_for_non_otl_conform_attributes:
            warnings.warn(
                message=f'{attr_key} is a non standardized attribute of {object_or_attribute.__class__.__name__}. '
                        f'The attribute will be added on the instance.',
                stacklevel=2,
                category=NonStandardAttributeWarning)
        if attribute is not None:
            yield attr_key, attribute

    def from_dict_instance(self, input_dict: DotnotationDict, model_directory: Path = None,
                           waarde_shortcut: bool = WAARDE_SHORTCUT, separator: str = SEPARATOR,
                           cardinality_indicator: str = CARDINALITY_SEPARATOR,
                           cardinality_separator: str = CARDINALITY_INDICATOR,
                           cast_datetime: bool = False, allow_non_otl_conform_attributes: bool = True,
                           warn_for_non_otl_conform_attributes: bool = True, cast_list: bool = False
                           ) -> OTLObject:
        if self.separator is not None:
            separator = self.separator
        if self.waarde_shortcut is not None:
            waarde_shortcut = self.waarde_shortcut
        if self.cardinality_indicator is not None:
            cardinality_indicator = self.cardinality_indicator
        if self.cardinality_separator is not None:
            cardinality_separator = self.cardinality_separator

        return self.from_dict(input_dict=input_dict, model_directory=model_directory, waarde_shortcut=waarde_shortcut,
                              separator=separator, cardinality_indicator=cardinality_indicator, cast_list=cast_list,
                              cardinality_separator=cardinality_separator, cast_datetime=cast_datetime,
                              allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                              warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

    @classmethod
    def from_dict(cls, input_dict: DotnotationDict, model_directory: Path = None,
                  cast_list: bool = False, cast_datetime: bool = False,
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
        except TypeError as e:
            raise ValueError('typeURI is invalid. Add a valid typeURI to the input dictionary.') from e

        for k, v in input_dict.items():
            if v is None:
                continue
            if k == 'typeURI':
                continue
            if k.startswith('_'):
                raise ValueError(f'{k} is a non standardized attribute of {o.__class__.__name__}. '
                                 f'While this is supported, the key can not start with "_".')
            cls.set_attribute_by_dotnotation(
                o, dotnotation=k, value=v, separator=separator, cardinality_indicator=cardinality_indicator,
                waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator,
                cast_datetime=cast_datetime, cast_list=cast_list,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

        return o

    @classmethod
    def set_attribute_by_dotnotation(cls, object_or_attribute: OTLObject | OTLAttribuut,
                                     dotnotation: str, value: object,
                                     separator: str = SEPARATOR, cardinality_indicator: str = CARDINALITY_INDICATOR,
                                     waarde_shortcut: bool = WAARDE_SHORTCUT,
                                     cardinality_separator: str = CARDINALITY_SEPARATOR,
                                     cast_datetime: bool = False,
                                     cast_list: bool = False,
                                     allow_non_otl_conform_attributes: bool = True,
                                     warn_for_non_otl_conform_attributes: bool = True):
        if dotnotation.count(cardinality_indicator) > 1:
            raise DotnotationListOfListError("can't use dotnotation for lists of lists")

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
                        message=f'{dotnotation} is a non standardized attribute of '
                                f'{object_or_attribute.__class__.__name__}. '
                                f'The attribute will be added on the instance.',
                        stacklevel=2,
                        category=NonStandardAttributeWarning)
                setattr(object_or_attribute, dotnotation, value)
                return
            if cardinality and cast_list:
                if value == '88888888':
                    attribute.clear_value()
                    return
                value = [attribute.field.convert_to_correct_type(v, log_warnings=False)
                         for v in str(value).split(cardinality_separator)]

            if attribute.field.waarde_shortcut_applicable and waarde_shortcut:
                if cardinality:
                    for index, v in enumerate(value):
                        if attribute.waarde is None or len(attribute.waarde) <= index:
                            attribute.add_empty_value()
                        if cast_list:
                            v = attribute.waarde[index]._waarde.field.convert_to_correct_type(v, log_warnings=False)
                        cls.set_attribute_by_dotnotation(
                            attribute.waarde[index], dotnotation='waarde', value=v,
                            cast_datetime=cast_datetime, cast_list=cast_list,
                            separator=separator, cardinality_indicator=cardinality_indicator,
                            waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator)
                else:
                    if attribute.waarde is None:
                        attribute.add_empty_value()
                    cls.set_attribute_by_dotnotation(
                        attribute.waarde, dotnotation='waarde', value=value,
                        cast_datetime=cast_datetime, cast_list=cast_list,
                        separator=separator, cardinality_indicator=cardinality_indicator,
                        waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator)
            else:
                if cast_datetime and attribute.field in {TimeField, DateField, DateTimeField}:
                    value = attribute.field.convert_to_correct_type(value, log_warnings=False)
                elif issubclass(attribute.field, KeuzelijstField):
                    if cardinality and value != '88888888':
                        value = [str(v) for v in value]
                    else:
                        value = str(value)
                try:
                    attribute.set_waarde(value)
                except Exception as exc:
                    print(exc)
            return

        first, rest = dotnotation.split(separator, 1)
        cardinality = False
        if first.endswith(cardinality_indicator):
            first = first[:-2]
            cardinality = True
        attribute = get_attribute_by_name(object_or_attribute, first)
        if attribute is None:
            raise ValueError(f'{first} is not an attribute of {object_or_attribute.__class__.__name__}.')

        if cardinality:
            if cast_list:
                last_attribute = DotnotationHelper.get_attribute_by_dotnotation(
                    instance_or_attribute=object_or_attribute, dotnotation=dotnotation, separator=separator,
                    waarde_shortcut=waarde_shortcut, cardinality_indicator=cardinality_indicator)
                value = [last_attribute.field.convert_to_correct_type(v, log_warnings=False)
                         for v in str(value).split(cardinality_separator)]
            for index, v in enumerate(value):
                if attribute.waarde is None or len(attribute.waarde) <= index:
                    attribute.add_empty_value()
                cls.set_attribute_by_dotnotation(
                    attribute.waarde[index], dotnotation=rest, value=v,
                    cast_datetime=cast_datetime, cast_list=cast_list,
                    separator=separator, cardinality_indicator=cardinality_indicator,
                    waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator)
            return

        if attribute.waarde is None:
            attribute.add_empty_value()
        cls.set_attribute_by_dotnotation(attribute.waarde, dotnotation=rest, value=value, separator=separator,
                                         cast_datetime=cast_datetime, cast_list=cast_list,
                                         cardinality_indicator=cardinality_indicator,
                                         waarde_shortcut=waarde_shortcut, cardinality_separator=cardinality_separator)
        # if value == '':
        #     value = None
