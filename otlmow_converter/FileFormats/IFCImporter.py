import re
from dataclasses import fields
from pathlib import Path
from typing import Iterable, List

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from otlmow_converter.AbstractImporter import AbstractImporter
from otlmow_converter.DotnotationDict import DotnotationDict
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.FileFormats.IFCDomain import Reference, IfcOrganization, IfcApplication, IfcCartesianPoint, \
    IfcDirection, IfcAxis2Placement2D, IfcAxis2Placement3D, IfcGeometricRepresentationContext, \
    IfcGeometricRepresentationSubContext, IfcPerson, IfcPersonAndOrganization, IfcOwnerHistory, IfcSIUnit, \
    IfcDimensionalExponents, IfcMeasureWithUnit, IfcConversionBasedUnit, IfcUnitAssignment, IfcProject, \
    IfcObjectPlacement, IfcLocalPlacement, IfcSite, IfcPolyLoop, IfcFaceBound, IfcFaceOuterBound, IfcFace, \
    IfcClosedShell, IfcFacetedBrep, IfcColourRgb, IfcSurfaceStyleRendering, IfcSurfaceStyle, IfcRepresentationItem, \
    IfcStyledItem, IfcShapeRepresentation, IfcProductDefinitionShape, IfcBuildingElementProxy, IfcPropertySingleValue, \
    IfcPropertySet, IfcRelDefinesByProperties, IfcRelContainedInSpatialStructure, IfcRelAggregates, IfcRatioMeasure, \
    IfcNormalisedRatioMeasure, IfcLabel
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

        yield from cls.ifc_file_to_objects(filepath, ignore_failed_objects=ignore_failed_objects)

    @classmethod
    def ifc_file_to_objects(cls, filepath: Path, **kwargs) -> Iterable[OTLObject]:
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

        ifc_dict = cls.parse_ifc_file_to_ifc_dict(filepath=filepath)

        for property_def_dict in [d for d in ifc_dict.values() if d['_type'] == 'IfcRelDefinesByProperties']:
            orig_property_dict = property_def_dict['property_definition']['properties']
            property_dict = {prop['name']: prop['nominal_value']['value']
                             for prop in orig_property_dict}

            asset = DotnotationDictConverter.from_dict(
                input_dict=DotnotationDict(property_dict), model_directory=model_directory, cast_list=cast_list,
                cast_datetime=cast_datetime,
                separator=separator, cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cardinality_separator=cardinality_separator,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
            asset.ifc_representation_dict = [d['representation'] for d in property_def_dict['related_objects']]

            if asset is not None:
                yield asset

    @classmethod
    def parse_ifc_file_to_ifc_dict(cls, filepath: Path) -> dict:
        d = {}
        # open and read the file
        regex = re.compile(r'#(\d+)=([A-Z\d]+)\((.*)\);')

        with open(filepath) as file:
            for i, line in enumerate(file):
                if not line.startswith('#'):
                    continue
                groups = regex.match(line)
                if not groups:
                    continue

                if i == 77:
                    pass
                cls.parse_line_groups_to_master_dict(groups=groups, master_dict=d)

        for k in list(d.keys()):
            if '_used' not in d[k]:
                d.pop(k)
            else:
                d[k].pop('_used')

        return d

    @classmethod
    def parse_line_groups_to_master_dict(cls, groups, master_dict) -> (str, object):
        _id = groups.group(1)
        _type = groups.group(2)
        _args = groups.group(3)

        _class = cls.get_class_by_uppercase_name(_type)

        class_dict = cls.parse_args_with_class(_class, _args, master_dict)
        class_dict['_used'] = False
        class_dict['_type'] = _class.__name__
        master_dict[_id] = class_dict

    @classmethod
    def parse_args_with_class(cls, _class, _args, master_dict) -> dict:
        args = list(cls.split_nested_tuples(_args, ','))
        d = {}
        for field, arg in zip(fields(_class), args):
            t = field.type
            if arg is None:
                continue
            if arg.startswith('IFC'):
                nested_class_name = arg.split('(')[0]
                nested_class = cls.get_class_by_uppercase_name(nested_class_name)
                nested_args = tuple(cls.split_nested_tuples(arg[len(nested_class_name)+1:-1], ','))
                parsed = cls.parse_args_with_class(nested_class, nested_args, master_dict)
                parsed['_type'] = nested_class.__name__
                d[field.name] = parsed
            elif arg.startswith('('):
                arg = arg[1:-1]
                value_list = list(cls.split_nested_tuples(arg, ','))
                for i, v in enumerate(value_list):
                    if v.startswith('#'):
                        master_dict[v[1:]]['_used'] = True
                        ref_arg = master_dict[v[1:]]
                        ref_arg.pop('_used')
                        value_list[i] = ref_arg
                d[field.name] = value_list
            elif arg.startswith('#'):
                master_dict[arg[1:]]['_used'] = True
                ref_arg = master_dict[arg[1:]]
                ref_arg.pop('_used')
                d[field.name] = ref_arg
            else:
                d[field.name] = arg
        return d


    @classmethod
    def get_class_by_uppercase_name(cls, _type):
        class_dict = {
            'IFCORGANIZATION': IfcOrganization,
            'IFCAPPLICATION': IfcApplication,
            'IFCCARTESIANPOINT': IfcCartesianPoint,
            'IFCDIRECTION': IfcDirection,
            'IFCAXIS2PLACEMENT2D': IfcAxis2Placement2D,
            'IFCAXIS2PLACEMENT3D': IfcAxis2Placement3D,
            'IFCGEOMETRICREPRESENTATIONCONTEXT': IfcGeometricRepresentationContext,
            'IFCGEOMETRICREPRESENTATIONSUBCONTEXT': IfcGeometricRepresentationSubContext,
            'IFCPERSON': IfcPerson,
            'IFCPERSONANDORGANIZATION': IfcPersonAndOrganization,
            'IFCOWNERHISTORY': IfcOwnerHistory,
            'IFCSIUNIT': IfcSIUnit,
            'IFCDIMENSIONALEXPONENTS': IfcDimensionalExponents,
            'IFCMEASUREWITHUNIT': IfcMeasureWithUnit,
            'IFCCONVERSIONBASEDUNIT': IfcConversionBasedUnit,
            'IFCUNITASSIGNMENT': IfcUnitAssignment,
            'IFCRATIOMEASURE': IfcRatioMeasure,
            'IFCPROJECT': IfcProject,
            'IFCOBJECTPLACEMENT': IfcObjectPlacement,
            'IFCLOCALPLACEMENT': IfcLocalPlacement,
            'IFCSITE': IfcSite,
            'IFCPOLYLOOP': IfcPolyLoop,
            'IFCFACEBOUND': IfcFaceBound,
            'IFCFACEOUTERBOUND': IfcFaceOuterBound,
            'IFCFACE': IfcFace,
            'IFCCLOSEDSHELL': IfcClosedShell,
            'IFCFACETEDBREP': IfcFacetedBrep,
            'IFCCOLOURRGB': IfcColourRgb,
            'IFCSURFACESTYLERENDERING': IfcSurfaceStyleRendering,
            'IFCSURFACESTYLE': IfcSurfaceStyle,
            'IFCREPRESENTATIONITEM': IfcRepresentationItem,
            'IFCSTYLEDITEM': IfcStyledItem,
            'IFCSHAPEREPRESENTATION': IfcShapeRepresentation,
            'IFCPRODUCTDEFINITIONSHAPE': IfcProductDefinitionShape,
            'IFCBUILDINGELEMENTPROXY': IfcBuildingElementProxy,
            'IFCPROPERTYSINGLEVALUE': IfcPropertySingleValue,
            'IFCPROPERTYSET': IfcPropertySet,
            'IFCRELDEFINESBYPROPERTIES': IfcRelDefinesByProperties,
            'IFCRELCONTAINEDINSPATIALSTRUCTURE': IfcRelContainedInSpatialStructure,
            'IFCRELAGGREGATES': IfcRelAggregates,
            'IFCNORMALISEDRATIOMEASURE': IfcNormalisedRatioMeasure,
            'IFCLABEL': IfcLabel


        }
        return class_dict[_type]

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
            if value is None or isinstance(value, Reference):
                continue
            if value.startswith('(') and value.endswith(')'):
                value = cls.parse_nested_tuples(value)
                values_list[index] = value
        return tuple(values_list)

    @classmethod
    def split_nested_tuples(cls, values_string: str, delimiter: str) -> List[str]:
        single_quotes, double_quotes, brackets = 0,0,0
        remove_quotes = False
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
                    remove_quotes = True
            elif char == '"':
                if double_quotes:
                    double_quotes -= 1
                else:
                    double_quotes += 1
                    remove_quotes = True
            elif char == delimiter and not single_quotes and not double_quotes and not brackets:
                value = value[:-1]
                yield from cls.sanitize_value(remove_quotes, value)
                remove_quotes = False
                value = ''
        yield from cls.sanitize_value(remove_quotes, value)

    @classmethod
    def sanitize_value(cls, remove_quotes, value):
        if remove_quotes:
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
        if value == '$':
            yield None
        else:
            yield value

    @classmethod
    def get_resolved_dict_item(cls, ifc_class: object, ifc_dict: dict, key_path: [str]) -> object:
        if len(key_path) == 0:
            return ifc_class
        key = key_path.pop(0)

        value = getattr(ifc_class, key)
        if value is None:
            return None
        if isinstance(value, tuple):
            value_list = []
            for v in value:
                if isinstance(v, Reference):
                    value_list.append(ifc_dict[v.id])
                else:
                    value_list.append(v)
            value = tuple(value_list)
        if isinstance(value, Reference):
            value = ifc_dict[value.id]
        return cls.get_resolved_dict_item(ifc_class=value, ifc_dict=ifc_dict, key_path=key_path)

    @classmethod
    def resolve_ifc_element_to_dict(cls, related_element: object, ifc_dict):
        for field in fields(related_element):
            value = getattr(related_element, field.name)
            if value is None:
                continue
            if isinstance(value, tuple) or isinstance(value, list):
                value_list = []
                for v in value:
                    if isinstance(v, Reference):
                        value_list.append(dict(cls.resolve_ifc_element_to_dict(ifc_dict[v.id], ifc_dict)))
                    else:
                        value_list.append(v)
                yield field.name, value_list
            elif isinstance(value, Reference):
                value = ifc_dict[value.id]
                value = dict(cls.resolve_ifc_element_to_dict(value, ifc_dict))
                yield field.name, value
            else:
                yield field.name, value
