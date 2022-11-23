﻿from typing import Union, Iterable, Tuple, List

from otlmow_model.BaseClasses.OTLAttribuut import OTLAttribuut
from otlmow_model.BaseClasses.WaardenObject import WaardenObject


class DotnotationHelper:
    separator = '.'
    cardinality_separator = '|'
    cardinality_indicator = '[]'
    waarde_shortcut_applicable = False

    @staticmethod
    def set_class_vars_to_parameters(cardinality_indicator, separator, waarde_shortcut_applicable):
        DotnotationHelper.separator = separator
        DotnotationHelper.cardinality_indicator = cardinality_indicator
        DotnotationHelper.waarde_shortcut_applicable = waarde_shortcut_applicable

    @staticmethod
    def set_parameters_to_class_vars(cardinality_indicator, separator, waarde_shortcut_applicable):
        if separator == '':
            separator = DotnotationHelper.separator
        if cardinality_indicator == '':
            cardinality_indicator = DotnotationHelper.cardinality_indicator
        if waarde_shortcut_applicable is None:
            waarde_shortcut_applicable = DotnotationHelper.waarde_shortcut_applicable
        return cardinality_indicator, separator, waarde_shortcut_applicable

    @staticmethod
    def get_dotnotation(attribute: OTLAttribuut,
                        separator: str = '.',
                        cardinality_indicator: str = '[]',
                        waarde_shortcut_applicable: bool = False):

        # cardinality_indicator, separator, waarde_shortcut_applicable = DotnotationHelper.set_parameters_to_class_vars(
        #     cardinality_indicator, separator, waarde_shortcut_applicable)

        if waarde_shortcut_applicable:
            if attribute.naam == 'waarde' and attribute.owner._parent is not None and attribute.owner._parent.field.waarde_shortcut_applicable:
                return DotnotationHelper.get_dotnotation(
                    attribute=attribute.owner._parent, separator=separator, cardinality_indicator=cardinality_indicator,
                    waarde_shortcut_applicable=waarde_shortcut_applicable)

        dotnotation = attribute.naam
        if attribute.kardinaliteit_max != '1':
            dotnotation += cardinality_indicator

        if isinstance(attribute.owner, OTLAttribuut):
            return dotnotation

        if isinstance(attribute.owner, WaardenObject):
            return DotnotationHelper.get_dotnotation(
                attribute=attribute.owner._parent, separator=separator, cardinality_indicator=cardinality_indicator,
                waarde_shortcut_applicable=waarde_shortcut_applicable) + separator + dotnotation

        return dotnotation

    # TODO add allow_nested_lists parameter
    @staticmethod
    def get_attributes_by_dotnotation(
            instance_or_attribute, dotnotation: str, separator: str = '', cardinality_indicator: str = '',
            waarde_shortcut_applicable: Union[bool, None] = None) -> Union[OTLAttribuut, List[OTLAttribuut]]:
        """Returns the attribute matching the dotnotation starting from a given class instance name or attribute
        :param instance_or_attribute: class or attribute to start the dotnotation from
        :param dotnotation: a string representing a hierarchical structure of attributes
        :type: str
        :return: returns the attribute matching the dotnotation starting from a given class instance name or attribute
        :rtype: OTLAttribuut or a list of OTLAttribuut
        """
        cardinality_indicator, separator, waarde_shortcut_applicable = DotnotationHelper.set_parameters_to_class_vars(
            cardinality_indicator, separator, waarde_shortcut_applicable)

        if waarde_shortcut_applicable and separator not in dotnotation:
            attribute = getattr(instance_or_attribute, '_' + dotnotation.replace(cardinality_indicator, ''))
            if attribute.field.waarde_shortcut_applicable:
                waardenObject = getattr(instance_or_attribute, dotnotation.replace(cardinality_indicator, ''))
                if attribute.kardinaliteit_max != '1':
                    collected_attributes = []
                    for waardenObject_in_list in waardenObject:
                        collected_attributes.append(getattr(waardenObject_in_list, '_waarde'))
                    return collected_attributes
                else:
                    return getattr(waardenObject, '_waarde')

        if separator in dotnotation:
            first = dotnotation.split(separator)[0]
            rest = dotnotation.split(separator, 1)[1]
            if cardinality_indicator in first:
                first = first.replace(cardinality_indicator, '')
                attribute = getattr(instance_or_attribute, first)
                collected_attributes = []
                for attr_in_list in attribute:
                    collected_attributes.append(DotnotationHelper.get_attributes_by_dotnotation(attr_in_list, rest))
                return collected_attributes
            else:
                attribute = getattr(instance_or_attribute, first)
                return DotnotationHelper.get_attributes_by_dotnotation(instance_or_attribute=attribute,
                                                                       dotnotation=rest,
                                                                       cardinality_indicator=cardinality_indicator,
                                                                       separator=separator,
                                                                       waarde_shortcut_applicable=waarde_shortcut_applicable)
        else:
            if cardinality_indicator in dotnotation:
                return getattr(instance_or_attribute, '_' + dotnotation.replace(cardinality_indicator, ''))
            else:
                return getattr(instance_or_attribute, '_' + dotnotation)

    @staticmethod
    def set_attribute_by_dotnotation(instanceOrAttribute, dotnotation, value, convert=True,
                                     convert_warnings: bool = True,
                                     separator: str = '', cardinality_indicator: str = '',
                                     waarde_shortcut_applicable: Union[bool, None] = None) -> None:

        cardinality_indicator, separator, waarde_shortcut_applicable = DotnotationHelper.set_parameters_to_class_vars(
            cardinality_indicator, separator, waarde_shortcut_applicable)

        if dotnotation.count(cardinality_indicator) == 0:
            gets = DotnotationHelper.get_attributes_by_dotnotation(instance_or_attribute=instanceOrAttribute,
                                                                   dotnotation=dotnotation,
                                                                   separator=separator,
                                                                   cardinality_indicator=cardinality_indicator,
                                                                   waarde_shortcut_applicable=waarde_shortcut_applicable)
            if convert:
                gets.set_waarde(DotnotationHelper.convert_waarde_to_correct_type(value, gets, convert_warnings))
            else:
                gets.set_waarde(value)
            return

        # there is a cardinality_indicator in the dotnotation

        if separator not in dotnotation:
            # set list directly
            attribute = DotnotationHelper.get_attributes_by_dotnotation(instance_or_attribute=instanceOrAttribute,
                                                                        dotnotation=dotnotation,
                                                                        separator=separator,
                                                                        cardinality_indicator=cardinality_indicator,
                                                                        waarde_shortcut_applicable=waarde_shortcut_applicable)

            if not isinstance(attribute, list) and not attribute.field.waarde_shortcut_applicable:
                if convert:
                    converted_value = DotnotationHelper.convert_waarde_to_correct_type(value, attribute,
                                                                                       convert_warnings)
                    attribute.set_waarde(converted_value)
                else:
                    attribute.set_waarde(value)
                return

            # waarde shortcut
            if isinstance(attribute, list):
                attribute = attribute[0]

            if attribute.field.waarde_shortcut_applicable:
                parent_waarde_attr = attribute
            else:
                parent_waarde_attr = attribute.owner._parent
            if parent_waarde_attr.waarde is None:
                parent_waarde_attr.add_empty_value()
            while len(parent_waarde_attr.waarde) < len(value):
                parent_waarde_attr.add_empty_value()

            for index, list_item in enumerate(value):
                DotnotationHelper.set_attribute_by_dotnotation(instanceOrAttribute=parent_waarde_attr.waarde[index],
                                                               dotnotation='waarde',
                                                               value=list_item,
                                                               convert=convert,
                                                               convert_warnings=convert_warnings,
                                                               separator=separator,
                                                               cardinality_indicator=cardinality_indicator,
                                                               waarde_shortcut_applicable=waarde_shortcut_applicable)
            return

        # cardinality > 1 and separator => search cardinality indicator
        first = dotnotation.split(separator)[0]
        rest = dotnotation.split(separator, maxsplit=1)[1]

        if cardinality_indicator not in first:
            # cardinality indicator not in first part => go one deeper
            attribute = DotnotationHelper.get_attributes_by_dotnotation(instance_or_attribute=instanceOrAttribute,
                                                                        dotnotation=first,
                                                                        separator=separator,
                                                                        cardinality_indicator=cardinality_indicator,
                                                                        waarde_shortcut_applicable=waarde_shortcut_applicable)
            if attribute.waarde is None:
                attribute.add_empty_value()
            DotnotationHelper.set_attribute_by_dotnotation(instanceOrAttribute=attribute.waarde, dotnotation=rest,
                                                           value=value, convert=convert,
                                                           convert_warnings=convert_warnings, separator=separator,
                                                           cardinality_indicator=cardinality_indicator,
                                                           waarde_shortcut_applicable=waarde_shortcut_applicable)
            return

        if cardinality_indicator in first:
            # shortcut waarde can't be applicable to this attribute because there is still a 2nd part in dotnotation
            # this must be a union / complex type
            attribute = DotnotationHelper.get_attributes_by_dotnotation(instance_or_attribute=instanceOrAttribute,
                                                                        dotnotation=first.replace(cardinality_indicator,
                                                                                                  ''),
                                                                        separator=separator,
                                                                        cardinality_indicator=cardinality_indicator,
                                                                        waarde_shortcut_applicable=waarde_shortcut_applicable)

            for index, value_item in enumerate(value):
                if attribute.waarde is None or len(attribute.waarde) <= index:
                    attribute.add_empty_value()
                DotnotationHelper.set_attribute_by_dotnotation(instanceOrAttribute=attribute.waarde[index],
                                                               dotnotation=rest, value=value_item, convert=convert,
                                                               convert_warnings=convert_warnings, separator=separator,
                                                               cardinality_indicator=cardinality_indicator,
                                                               waarde_shortcut_applicable=waarde_shortcut_applicable)

    @classmethod
    def list_attributes_and_values_by_dotnotation(cls, asset=None, waarde_shortcut: bool = False, separator: str = '.',
                                                  cardinality_indicator: str = '[]') -> Iterable[Tuple[str, object]]:
        sorted_attributes = sorted(list(vars(asset).items()), key=lambda i: i[0])

        for k, v in sorted_attributes:
            if k in ['_parent', '_geometry_types', '_valid_relations']:
                continue

            if v.waarde is None:
                continue

            if v.field.waardeObject is None:
                dotnotation = DotnotationHelper.get_dotnotation(
                    v, waarde_shortcut_applicable=waarde_shortcut, separator=separator,
                    cardinality_indicator=cardinality_indicator)
                yield dotnotation, v.waarde
                continue
            else:
                if v.kardinaliteit_max != '1':
                    combined_dict = {}
                    for index, lijst_item in enumerate(v.waarde):
                        for k1, v1 in cls.list_attributes_and_values_by_dotnotation(
                                asset=lijst_item, waarde_shortcut=waarde_shortcut, separator=separator,
                                cardinality_indicator=cardinality_indicator):
                            if k1 not in combined_dict:
                                combined_dict[k1] = []
                                for i in range(index):
                                    combined_dict[k1].append(None)
                            combined_dict[k1].append(v1)

                        for lijst in combined_dict.values():
                            if len(lijst) < index + 1:
                                lijst.append(None)

                    for k2, v2 in combined_dict.items():
                        yield k2, v2
                else:
                    for k1, v1 in cls.list_attributes_and_values_by_dotnotation(
                            asset=v.waarde, waarde_shortcut=waarde_shortcut, separator=separator,
                            cardinality_indicator=cardinality_indicator):
                        yield k1, v1

    @staticmethod
    def convert_waarde_to_correct_type(waarde, attribuut, log_warnings):
        field = attribuut.field
        if attribuut.kardinaliteit_max != '1' and isinstance(waarde, list):
            new_list = []
            for value_item in waarde:
                new_list.append(field.convert_to_correct_type(value_item, log_warnings=log_warnings))
            return new_list

        if attribuut.field.waardeObject is not None and attribuut.field.waarde_shortcut_applicable:
            if attribuut.waarde is None:
                attribuut.add_empty_value()
            field = attribuut.waarde._waarde.field

        return field.convert_to_correct_type(waarde, log_warnings=log_warnings)

    def flatten_dict(self, input_dict: dict, seperator: str = '.', prefix='', affix='', new_dict=None):
        if new_dict is None:
            new_dict = {}
        for k, v in input_dict.items():
            if isinstance(v, dict):
                self.flatten_dict(input_dict=v, prefix=k, new_dict=new_dict)
            elif isinstance(v, list):
                for i in range(0, len(v)):
                    if isinstance(v[i], dict):
                        self.flatten_dict(input_dict=v[i], prefix=k, affix='[' + str(i) + ']', new_dict=new_dict)
                    else:
                        if prefix != '':
                            new_dict[prefix + seperator + k + '[' + str(i) + ']'] = v[i]
                        else:
                            new_dict[k + '[' + str(i) + ']'] = v[i]
            else:
                if prefix != '':
                    new_dict[prefix + affix + seperator + k] = v
                else:
                    new_dict[k] = v

        return new_dict

# from collections.abc import MutableMapping
#
# def _flatten_dict_gen(d, parent_key, sep):
#     for k, v in d.items():
#         new_key = parent_key + sep + k if parent_key else k
#         if isinstance(v, MutableMapping):
#             yield from flatten_dict(v, new_key, sep=sep).items()
#         else:
#             yield new_key, v
#
#
# def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '.'):
#     return dict(_flatten_dict_gen(d, parent_key, sep))
