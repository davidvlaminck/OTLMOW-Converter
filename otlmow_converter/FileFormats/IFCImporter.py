import json
import re
import warnings
from pathlib import Path
from typing import Iterable, List

import ifcopenshell
import ifcopenshell.util.element
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from rdflib.plugins.sparql.parserutils import value

from otlmow_converter.AbstractImporter import AbstractImporter
from otlmow_converter.DotnotationDict import DotnotationDict
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.Exceptions.UnexpectedIfcTypeWarning import UnexpectedIfcTypeWarning
from otlmow_converter.SettingsManager import load_settings, GlobalVariables

load_settings()

ifc_settings = GlobalVariables.settings['formats']['IFC']
ifc_dotnotation_settings = ifc_settings['dotnotation']
SEPARATOR = ifc_dotnotation_settings['separator']
CARDINALITY_SEPARATOR = ifc_dotnotation_settings['cardinality_separator']
CARDINALITY_INDICATOR = ifc_dotnotation_settings['cardinality_indicator']
WAARDE_SHORTCUT = ifc_dotnotation_settings['waarde_shortcut']
CAST_LIST = ifc_settings['cast_list']
CAST_DATETIME = ifc_settings['cast_datetime']
ALLOW_NON_OTL_CONFORM_ATTRIBUTES = ifc_settings['allow_non_otl_conform_attributes']
WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES = ifc_settings['warn_for_non_otl_conform_attributes']




class IFCImporter(AbstractImporter):
    allowed_ifc_types = {'IfcBeam', 'IfcColumn', 'IfcFooting', 'IfcSlab', 'IfcWall', 'IfcWallStandardCase', 'IfcPlate',
                         'IfcDiscreteAccessory', 'IfcMechanicalFastener', 'IfcOpeningElement', 'IfcMember',
                         'IfcElementAssembly', 'IfcReinforcingBar', 'IfcBuildingElementProxy', 'IfcCovering',
                         'IfcFastener'}

    @classmethod
    def to_objects(cls, filepath: Path, **kwargs) -> Iterable[OTLObject]:
        """Imports an IFC 4.3 file and decodes it to OTL objects

        :param filepath: location of the file, defaults to ''
        :type: Path
        :rtype: list
        :return: returns a list of OTL objects
        """

        ignore_failed_objects = False
        if kwargs is not None and 'ignore_failed_objects' in kwargs:
            ignore_failed_objects = kwargs['ignore_failed_objects']

        model_directory = None
        if kwargs is not None and 'model_directory' in kwargs:
            model_directory = kwargs['model_directory']

        separator = kwargs.get('separator', SEPARATOR)
        cardinality_separator = kwargs.get('cardinality_separator', CARDINALITY_SEPARATOR)
        cardinality_indicator = kwargs.get('cardinality_indicator', CARDINALITY_INDICATOR)
        waarde_shortcut = kwargs.get('waarde_shortcut', WAARDE_SHORTCUT)
        cast_list = kwargs.get('cast_list', CAST_LIST)
        cast_datetime = kwargs.get('cast_datetime', CAST_DATETIME)
        allow_non_otl_conform_attributes = kwargs.get('allow_non_otl_conform_attributes',
                                                      ALLOW_NON_OTL_CONFORM_ATTRIBUTES)
        warn_for_non_otl_conform_attributes = kwargs.get('warn_for_non_otl_conform_attributes',
                                                         WARN_FOR_NON_OTL_CONFORM_ATTRIBUTES)

        model = ifcopenshell.open(filepath)

        for el in model.by_type('IfcBuildingElement'):
            property_set = ifcopenshell.util.element.get_psets(el)
            first_key = next(iter(property_set))
            if not first_key.startswith('OTL_'):
                continue
            all_info = el.get_info_2(recursive=True)
            gl_id = el.GlobalId
            ifc_type = all_info['type']

            if ifc_type not in cls.allowed_ifc_types:
                warnings.warn(f'Unexpected IFC type {ifc_type} for element {gl_id}. Should be one of: '
                              f'IfcBeam, IfcColumn, IfcFooting, IfcSlab, IfcWall, IfcWallStandardCase, IfcPlate, '
                              f'IfcDiscreteAccessory, IfcMechanicalFastener, IfcOpeningElement, IfcMember, '
                              f'IfcElementAssembly, IfcReinforcingBar, IfcBuildingElementProxy, IfcCovering, IfcFastener',
                              UnexpectedIfcTypeWarning)

            # to see what info there is on geometry, uncomment the following lines
            # print(all_info)
            # settings = ifcopenshell.geom.settings()
            # representations = el.Representation.Representations
            # for representation in representations:
            #     shape = ifcopenshell.geom.create_shape(settings, el, representation)
            #     print(shape)
            #     print(shape.geometry)

            property_dict = property_set[first_key]
            del property_dict['id']

            asset = DotnotationDictConverter.from_dict(
                input_dict=DotnotationDict(property_dict), model_directory=model_directory, cast_list=cast_list,
                                           cast_datetime=cast_datetime,
                separator=separator, cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cardinality_separator=cardinality_separator,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
            if asset is not None:
                yield asset

    @classmethod
    def ifc_to_dict(cls, filepath):
        d = {}
        # open and read the file
        regex = re.compile(r'#(\d+)=([A-Z\d]+)\((.*)\);')
        regex_2 = re.compile(r'#(\d+)=([A-Z\d]+)\(([A-Z\d]+)\((.*)\)(.*)\);')
        with open(filepath, 'r') as file:
            for line in file:
                if not line.startswith('#'):
                    continue
                groups = regex.match(line)
                if not groups:
                    continue

                groups_nested = regex_2.match(line)
                if groups_nested:
                    cls.parse_nested_dict(groups=groups_nested, master_dict=d)
                elif groups:
                    cls.parse_unnested_dict(groups=groups, master_dict=d)
                else:
                    continue

                print(line)
        return d

    @classmethod
    def parse_nested_dict(cls, groups: re.Match[str], master_dict: dict) -> None:
        cls.parse_unnested_dict(groups, master_dict, offset=1)
        _id = groups.group(1)
        _type = groups.group(2)
        values = groups.group(5)
        nested_dict = master_dict[_id]
        nested_dict['id'] += '.1'

        tuples = cls.parse_nested_tuples(values)
        values = list(cls.process_values(tuples, master_dict))

        values.insert(0, nested_dict)

        master_dict[_id] = {'ifc_type': _type, 'values': values, 'id': _id}

    @classmethod
    def parse_unnested_dict(cls, groups: re.Match[str], master_dict: dict, offset: int = 0) -> None:
        _id = groups.group(1)
        _type = groups.group(2 + offset)
        values = groups.group(3 + offset)

        tuples = cls.parse_nested_tuples(values)
        values = cls.process_values(tuples, master_dict)

        master_dict[_id] = {'ifc_type': _type, 'values': values, 'id': _id}

    @classmethod
    def process_values(cls, tuples, master_dict):
        new_list = list(tuples)
        for i, value in enumerate(new_list):
            if isinstance(value, tuple):
                new_list[i] = cls.process_values(value, master_dict)
            else:
                if value.startswith('#'):
                    if value[1:] in master_dict:
                        new_list[i] = master_dict[value[1:]]
                    else:
                        print(value)
        return tuple(new_list)

    @classmethod
    def parse_nested_tuples(cls, values_string):
        if values_string.startswith('(') and values_string.endswith(')'):
            values_string = values_string[1:-1]
        values_list = list(cls.split_nested_tuples(values_string, ','))
        for index, value in enumerate(values_list):
            if value.startswith('(') and value.endswith(')'):
                value = cls.parse_nested_tuples(value)
                values_list[index] = value
        return tuple(values_list)

    @classmethod
    def split_nested_tuples(cls, values_string: str, delimiter: str) -> List[str]:
        single_quotes, double_quotes, brackets = 0,0,0
        value = ''
        for char in values_string:
            value += char
            if char == '(':
                brackets += 1
            elif char == ')':
                brackets -= 1
            elif char == "'":
                if single_quotes:
                    single_quotes -= 1
                else:
                    single_quotes += 1
            elif char == '"':
                if double_quotes:
                    double_quotes -= 1
                else:
                    double_quotes += 1
            elif char == delimiter and not single_quotes and not double_quotes and not brackets:
                yield value[:-1]
                value = ''
        yield value