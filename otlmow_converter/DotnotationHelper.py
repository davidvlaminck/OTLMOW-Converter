from typing import Union, Iterable, Tuple, List

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut, OTLObject, get_attribute_by_name
from otlmow_model.OtlmowModel.BaseClasses.WaardenObject import WaardenObject

from otlmow_converter.Exceptions.DotnotationListOfListError import DotnotationListOfListError
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

load_settings()

SEPARATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['separator']
CARDINALITY_SEPARATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['cardinality_separator']
CARDINALITY_INDICATOR = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['cardinality_indicator']
WAARDE_SHORTCUT = GlobalVariables.settings['formats']['OTLMOW']['dotnotation']['waarde_shortcut']


class DotnotationHelper:
    def __init__(self, separator: str = SEPARATOR, cardinality_separator: str = CARDINALITY_SEPARATOR,
                 cardinality_indicator: str = CARDINALITY_INDICATOR, waarde_shortcut: bool = WAARDE_SHORTCUT):
        self.separator: str = separator
        self.cardinality_separator: str = cardinality_separator
        self.cardinality_indicator: str = cardinality_indicator
        self.waarde_shortcut: bool = waarde_shortcut

    def get_dotnotation_instance(self, attribute: Union[OTLAttribuut, WaardenObject],
                        separator: str = SEPARATOR,
                        cardinality_indicator: str = CARDINALITY_INDICATOR,
                        waarde_shortcut: bool = WAARDE_SHORTCUT) -> str:
        return self.get_dotnotation(attribute=attribute, separator=separator, 
                                    cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut)

    @classmethod
    def get_dotnotation(cls, attribute: Union[OTLAttribuut, WaardenObject],
                        separator: str = SEPARATOR,
                        cardinality_indicator: str = CARDINALITY_INDICATOR,
                        waarde_shortcut: bool = WAARDE_SHORTCUT) -> str:
        if waarde_shortcut and (attribute.naam == 'waarde' and attribute.owner._parent is not None and
                            attribute.owner._parent.field.waarde_shortcut_applicable):
            return DotnotationHelper.get_dotnotation(
                attribute=attribute.owner._parent, separator=separator, cardinality_indicator=cardinality_indicator,
                waarde_shortcut=waarde_shortcut)

        dotnotation = attribute.naam
        if attribute.kardinaliteit_max != '1':
            dotnotation += cardinality_indicator

        if isinstance(attribute.owner, OTLAttribuut):
            return dotnotation

        if isinstance(attribute.owner, WaardenObject):
            return cls.get_dotnotation(
                attribute=attribute.owner._parent, separator=separator, cardinality_indicator=cardinality_indicator,
                waarde_shortcut=waarde_shortcut) + separator + dotnotation

        return dotnotation

    def get_attributes_per_level_by_dotnotation_instance(self, instance_or_attribute: Union[OTLAttribuut, OTLObject],
                                                         dotnotation: str) -> Union[OTLAttribuut, List[OTLAttribuut]]:
        return DotnotationHelper.get_attributes_per_level_by_dotnotation(
            instance_or_attribute=instance_or_attribute, dotnotation=dotnotation, separator=self.separator,
            cardinality_indicator=self.cardinality_indicator)

    @classmethod
    def get_attributes_per_level_by_dotnotation(cls, instance_or_attribute: Union[OTLAttribuut, OTLObject],
                                                dotnotation: str, separator: str = SEPARATOR,
                                                cardinality_indicator: str = CARDINALITY_INDICATOR
                                                ) -> [OTLAttribuut]:
        """Returns the attributes matching the dotnotation starting from a given class instance name or attribute and
        then iterating over the attributes in the dotnotation.
        If there is an attribute with cardinality > 1, the first instantiated attribute of that list is used.
        :param instance_or_attribute: class or attribute to start the dotnotation from
        :param dotnotation: a string representing a hierarchical structure of attributes
        :type: str
        :return: returns the attribute matching the dotnotation starting from a given class instance name or attribute
        :rtype: OTLAttribuut
        """

        if len(dotnotation.split(cardinality_indicator)) > 2:
            raise ValueError("can't use dotnotation for lists of lists")

        if separator in dotnotation:
            partial_dotnotation = ''
            parts = dotnotation.split(separator)
            for part in parts:
                if partial_dotnotation == '':
                    partial_dotnotation = part
                else:
                    partial_dotnotation += separator + part
                attribute = DotnotationHelper.get_attribute_by_dotnotation(
                    instance_or_attribute=instance_or_attribute, dotnotation=partial_dotnotation,
                    separator=separator, cardinality_indicator=cardinality_indicator, waarde_shortcut=False)
                yield attribute
                if attribute.field.waarde_shortcut_applicable:
                    yield DotnotationHelper.get_attribute_by_dotnotation(
                        instance_or_attribute=instance_or_attribute, dotnotation=partial_dotnotation,
                        separator=separator, cardinality_indicator=cardinality_indicator, waarde_shortcut=True)

        else:
            attribute = DotnotationHelper.get_attribute_by_dotnotation(
                instance_or_attribute=instance_or_attribute, dotnotation=dotnotation,
                separator=separator, cardinality_indicator=cardinality_indicator, waarde_shortcut=False)
            yield attribute
            if attribute.field.waarde_shortcut_applicable:
                yield DotnotationHelper.get_attribute_by_dotnotation(
                    instance_or_attribute=instance_or_attribute, dotnotation=dotnotation,
                    separator=separator, cardinality_indicator=cardinality_indicator, waarde_shortcut=True)

    def get_attribute_by_dotnotation_instance(self, instance_or_attribute: Union[OTLAttribuut, OTLObject],
                                              dotnotation: str
                                              ) -> Union[OTLAttribuut, List[OTLAttribuut]]:
        return DotnotationHelper.get_attribute_by_dotnotation(
            instance_or_attribute=instance_or_attribute, dotnotation=dotnotation, separator=self.separator,
            cardinality_indicator=self.cardinality_indicator, waarde_shortcut=self.waarde_shortcut)

    @classmethod
    def get_attribute_by_dotnotation(cls, instance_or_attribute: Union[OTLAttribuut, OTLObject], dotnotation: str,
                                     separator: str = SEPARATOR, cardinality_indicator: str = CARDINALITY_INDICATOR,
                                     waarde_shortcut: bool = WAARDE_SHORTCUT
                                     ) -> Union[OTLAttribuut, List[OTLAttribuut]]:
        """Returns the attribute matching the dotnotation starting from a given class instance name or attribute.
        If there is an attribute with cardinality > 1, the first instantiated attribute of that list is used.
        :param instance_or_attribute: class or attribute to start the dotnotation from
        :param dotnotation: a string representing a hierarchical structure of attributes
        :type: str
        :return: returns the attribute matching the dotnotation starting from a given class instance name or attribute
        :rtype: OTLAttribuut
        """

        if len(dotnotation.split(cardinality_indicator)) > 2:
            raise DotnotationListOfListError("can't use dotnotation for lists of lists")

        if separator in dotnotation:
            first_part = dotnotation.split(separator)[0]
            rest = dotnotation.split(separator, 1)[1]
            if cardinality_indicator in first_part:
                first_part = first_part.replace(cardinality_indicator, '')
                attribute = get_attribute_by_name(instance_or_attribute, first_part)
                if attribute.waarde is None:
                    attribute.add_empty_value()
                return DotnotationHelper.get_attribute_by_dotnotation(
                    instance_or_attribute=attribute.waarde[0], dotnotation=rest, separator=separator,
                    cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut)
            else:
                attribute = get_attribute_by_name(instance_or_attribute, first_part)
                if attribute.waarde is None:
                    attribute.add_empty_value()
                return DotnotationHelper.get_attribute_by_dotnotation(
                    instance_or_attribute=attribute.waarde, dotnotation=rest, separator=separator,
                    cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut)
        else:
            cardinality = False
            if cardinality_indicator in dotnotation:
                dotnotation = dotnotation.replace(cardinality_indicator, '')
                cardinality = True
            attribute = get_attribute_by_name(instance_or_attribute, dotnotation)
            if attribute.field.waarde_shortcut_applicable and waarde_shortcut:
                if attribute.waarde is None:
                    attribute.add_empty_value()
                return attribute.waarde[0]._waarde if cardinality else attribute.waarde._waarde
            return attribute

    def set_attribute_by_dotnotation_instance(
            self, instance_or_attribute: Union[OTLAttribuut, OTLObject], dotnotation: str, value: object,
            convert: bool = True, convert_warnings: bool = True) -> None:
        return DotnotationHelper.set_attribute_by_dotnotation(
            instance_or_attribute=instance_or_attribute, dotnotation=dotnotation, value=value, convert=convert,
            convert_warnings=convert_warnings, separator=self.separator,
            cardinality_indicator=self.cardinality_indicator,
            cardinality_separator=self.cardinality_separator, waarde_shortcut=self.waarde_shortcut)

    @classmethod
    def set_attribute_by_dotnotation(cls, instance_or_attribute: Union[OTLAttribuut, OTLObject], dotnotation: str,
                                     value: object, convert: bool = True, convert_warnings: bool = True,
                                     separator: str = SEPARATOR, cardinality_indicator: str = CARDINALITY_INDICATOR,
                                     cardinality_separator: str = CARDINALITY_SEPARATOR,
                                     waarde_shortcut: bool = True) -> None:
        if len(dotnotation.split(cardinality_indicator)) > 2:
            raise ValueError("can't use dotnotation for lists of lists")

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

    def list_attributes_and_values_by_dotnotation_instance(
            self, instance_or_attribute: Union[OTLAttribuut, OTLObject]) -> Iterable[Tuple[str, object]]:
        return DotnotationHelper.list_attributes_and_values_by_dotnotation(
            asset=instance_or_attribute, separator=self.separator,
            cardinality_indicator=self.cardinality_indicator, waarde_shortcut=self.waarde_shortcut)

    @classmethod
    def list_attributes_and_values_by_dotnotation(cls, asset=None, waarde_shortcut: bool = False, separator: str = '.',
                                                  cardinality_indicator: str = '[]') -> Iterable[Tuple[str, object]]:
        for attribute in asset:
            if attribute.waarde is None:
                continue

            if attribute.field.waardeObject is None:
                dotnotation = DotnotationHelper.get_dotnotation(
                    attribute, waarde_shortcut=waarde_shortcut, separator=separator,
                    cardinality_indicator=cardinality_indicator)
                yield dotnotation, attribute.waarde
                continue
            else:
                if attribute.kardinaliteit_max != '1':
                    combined_dict = {}
                    for index, lijst_item in enumerate(attribute.waarde):
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
                            asset=attribute.waarde, waarde_shortcut=waarde_shortcut, separator=separator,
                            cardinality_indicator=cardinality_indicator):
                        yield k1, v1

    @classmethod
    def flatten_dict(cls, input_dict: dict, separator: str = '.', prefix='', affix='', new_dict=None) -> dict:
        if new_dict is None:
            new_dict = {}
        for k, v in input_dict.items():
            if isinstance(v, dict):
                cls.flatten_dict(input_dict=v, prefix=k, new_dict=new_dict)
            elif isinstance(v, list):
                for i in range(len(v)):
                    if isinstance(v[i], dict):
                        cls.flatten_dict(input_dict=v[i], prefix=k, affix=f'[{i}]', new_dict=new_dict)
                    elif prefix == '':
                        new_dict[f'{k}[{str(i)}]'] = v[i]
                    else:
                        new_dict[prefix + separator + k + '[' + str(i) + ']'] = v[i]
            elif prefix != '':
                    new_dict[prefix + affix + separator + k] = v
            else:
                new_dict[k] = v

        return new_dict

    @classmethod
    def clear_list_of_list_attributes(cls, instance_or_attribute: Union[OTLObject, OTLAttribuut], cardinality_level: int = 0):
        for attribute in instance_or_attribute:
            if attribute.waarde is None or attribute.waarde == []:
                continue

            if cardinality_level > 1 and attribute.field.waardeObject is None:
                attribute.set_waarde(None)
                continue

            if attribute.field.waardeObject is None:
                if attribute.kardinaliteit_max == '1':
                    continue
                if cardinality_level >= 1:
                    attribute.set_waarde(None)
            else: # complex attribute
                if attribute.kardinaliteit_max != '1':
                    cls.clear_list_of_list_attributes(attribute.waarde[0], cardinality_level + 1)
                else:
                    cls.clear_list_of_list_attributes(attribute.waarde, cardinality_level)
