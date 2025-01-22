import re
import warnings
from dataclasses import asdict, fields
from pathlib import Path
from typing import Iterable, List

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from otlmow_converter.AbstractImporter import AbstractImporter
from otlmow_converter.DotnotationDict import DotnotationDict
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.Exceptions.UnexpectedIfcTypeWarning import UnexpectedIfcTypeWarning
from otlmow_converter.FileFormats.IFCDomain import Reference, IfcOrganization, IfcApplication, IfcCartesianPoint, \
    IfcDirection, IfcAxis2Placement2D, IfcAxis2Placement3D, IfcGeometricRepresentationContext, \
    IfcGeometricRepresentationSubContext, IfcPerson, IfcPersonAndOrganization, IfcOwnerHistory, IfcSIUnit, \
    IfcDimensionalExponents, IfcMeasureWithUnit, IfcConversionBasedUnit, IfcUnitAssignment, IfcProject, \
    IfcObjectPlacement, IfcLocalPlacement, IfcSite, IfcPolyLoop, IfcFaceBound, IfcFaceOuterBound, IfcFace, \
    IfcClosedShell, IfcFacetedBrep, IfcColourRgb, IfcSurfaceStyleRendering, IfcSurfaceStyle, IfcRepresentationItem, \
    IfcStyledItem, IfcShapeRepresentation, IfcProductDefinitionShape, IfcBuildingElementProxy, IfcPropertySingleValue, \
    IfcPropertySet, IfcRelDefinesByProperties, IfcRelContainedInSpatialStructure, IfcRelAggregates
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

        ifc_dict = cls.ifc_file_to_ifc_dict(filepath=filepath)
        root = ifc_dict['root']

        elements = cls.get_resolved_dict_item(ifc_class=root, ifc_dict=ifc_dict, key_path=['related_elements'])
        elements_dict = { e.global_id: e for e in elements }
        prop_set_relations = ifc_dict['prop_set_relations']

        for prop_set_relation in prop_set_relations:
            rel_defined_by_props = ifc_dict[prop_set_relation]
            properties = cls.get_resolved_dict_item(ifc_class=rel_defined_by_props, ifc_dict=ifc_dict,
                                                  key_path=['property_definition','properties'])
            property_dict = {}
            for prop in properties:
                value = prop.nominal_value
                if value is None:
                    continue
                if value.startswith('IFCLABEL'):
                    value = value[10:-2]
                property_dict[prop.name] = value

            asset = DotnotationDictConverter.from_dict(
                input_dict=DotnotationDict(property_dict), model_directory=model_directory, cast_list=cast_list,
                                           cast_datetime=cast_datetime,
                separator=separator, cardinality_indicator=cardinality_indicator, waarde_shortcut=waarde_shortcut,
                cardinality_separator=cardinality_separator,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

            related_element = elements_dict[asset.assetId.identificator]
            asset.ifc_representation_dict = dict(cls.resolve_ifc_element_to_dict(related_element=related_element,
                                                                             ifc_dict=ifc_dict))

            if asset is not None:
                yield asset


    @classmethod
    def ifc_file_to_ifc_dict(cls, filepath: Path) -> dict:
        d = {'prop_set_relations': []}
        # open and read the file
        regex = re.compile(r'#(\d+)=([A-Z\d]+)\((.*)\);')

        with open(filepath) as file:
            for i, line in enumerate(file):
                if not line.startswith('#'):
                    continue
                groups = regex.match(line)
                if not groups:
                    continue
                id, ifc_class = cls.parse_groups_to_master_dict(groups=groups, master_dict=d)
                if ifc_class.__class__.__name__ == 'IfcRelDefinesByProperties':
                    d['prop_set_relations'].append(id)
                elif ifc_class.__class__.__name__ == 'IfcRelContainedInSpatialStructure':
                    d['root'] = ifc_class

        return d


    @classmethod
    def parse_groups_to_master_dict(cls, groups, master_dict) -> (str, object):
        _id = groups.group(1)
        _type = groups.group(2)
        _args = groups.group(3)

        c = cls.instantiate_ifc_object(ifc_type=_type, id=_id, args=_args)
        master_dict[_id] = c
        return _id, c

    @classmethod
    def instantiate_ifc_object(cls, ifc_type, id, args):
        _args = cls.parse_nested_tuples(args)
        try:
            if ifc_type == 'IFCORGANIZATION':
                return IfcOrganization(*_args)
            elif ifc_type == 'IFCAPPLICATION':
                return IfcApplication(*_args)
            elif ifc_type == 'IFCCARTESIANPOINT':
                coords = IfcCartesianPoint.convert_to_coords(_args)
                return IfcCartesianPoint(list(coords))
            elif ifc_type == 'IFCDIRECTION':
                ratios = IfcDirection.convert_to_direction_ratios(_args)
                return IfcDirection(ratios)
            elif ifc_type == 'IFCAXIS2PLACEMENT2D':
                return IfcAxis2Placement2D(*_args)
            elif ifc_type == 'IFCAXIS2PLACEMENT3D':
                return IfcAxis2Placement3D(*_args)
            elif ifc_type == 'IFCGEOMETRICREPRESENTATIONCONTEXT':
                return IfcGeometricRepresentationContext(*_args)
            elif ifc_type == 'IFCGEOMETRICREPRESENTATIONSUBCONTEXT':
                return IfcGeometricRepresentationSubContext(*_args)
            elif ifc_type == 'IFCPERSON':
                return IfcPerson(*_args)
            elif ifc_type == 'IFCPERSONANDORGANIZATION':
                return IfcPersonAndOrganization(*_args)
            elif ifc_type == 'IFCOWNERHISTORY':
                return IfcOwnerHistory(*_args)
            elif ifc_type == 'IFCSIUNIT':
                return IfcSIUnit(*_args)
            elif ifc_type == 'IFCDIMENSIONALEXPONENTS':
                return IfcDimensionalExponents(*_args)
            elif ifc_type == 'IFCMEASUREWITHUNIT':
                return IfcMeasureWithUnit(*_args)
            elif ifc_type == 'IFCCONVERSIONBASEDUNIT':
                return IfcConversionBasedUnit(*_args)
            elif ifc_type == 'IFCUNITASSIGNMENT':
                return IfcUnitAssignment(*_args)
            elif ifc_type == 'IFCPROJECT':
                return IfcProject(*_args)
            elif ifc_type == 'IFCOBJECTPLACEMENT':
                return IfcObjectPlacement(*_args)
            elif ifc_type == 'IFCLOCALPLACEMENT':
                return IfcLocalPlacement(*_args)
            elif ifc_type == 'IFCSITE':
                return IfcSite(*_args)
            elif ifc_type == 'IFCPOLYLOOP':
                points = IfcPolyLoop.convert_to_points(_args)
                return IfcPolyLoop(points)
            elif ifc_type == 'IFCFACEOUTERBOUND':
                return IfcFaceOuterBound(*_args)
            elif ifc_type == 'IFCFACE':
                bounds = IfcFace.convert_to_bounds(_args)
                return IfcFace(bounds)
            elif ifc_type == 'IFCCLOSEDSHELL':
                faces = IfcClosedShell.convert_to_faces(_args)
                return IfcClosedShell(faces)
            elif ifc_type == 'IFCFACETEDBREP':
                return IfcFacetedBrep(*_args)
            elif ifc_type == 'IFCCOLOURRGB':
                return IfcColourRgb(*_args)
            elif ifc_type == 'IFCSURFACESTYLERENDERING':
                return IfcSurfaceStyleRendering(*_args)
            elif ifc_type == 'IFCSURFACESTYLE':
                return IfcSurfaceStyle(*_args)
            elif ifc_type == 'IFCREPRESENTATIONITEM':
                return IfcRepresentationItem(*_args)
            elif ifc_type == 'IFCSTYLEDITEM':
                return IfcStyledItem(*_args)
            elif ifc_type == 'IFCSHAPEREPRESENTATION':
                return IfcShapeRepresentation(*_args)
            elif ifc_type == 'IFCPRODUCTDEFINITIONSHAPE':
                return IfcProductDefinitionShape(*_args)
            elif ifc_type == 'IFCBUILDINGELEMENTPROXY':
                return IfcBuildingElementProxy(*_args)
            elif ifc_type == 'IFCPROPERTYSINGLEVALUE':
                return IfcPropertySingleValue(*_args)
            elif ifc_type == 'IFCPROPERTYSET':
                return IfcPropertySet(*_args)
            elif ifc_type == 'IFCRELDEFINESBYPROPERTIES':
                return IfcRelDefinesByProperties(*_args)
            elif ifc_type == 'IFCFACEBOUND':
                return IfcFaceBound(*_args)
            elif ifc_type == 'IFCRELCONTAINEDINSPATIALSTRUCTURE':
                return IfcRelContainedInSpatialStructure(*_args)
            elif ifc_type == 'IFCRELAGGREGATES':
                return IfcRelAggregates(*_args)
            else:
                # return {'ifc_type': ifc_type, 'id': id, 'values': cls.parse_nested_tuples(args)}
                raise NotImplementedError(f'IFC type {ifc_type} not implemented')
        except Exception as ex:
            print(f'Error while parsing {ifc_type} with id {id}')
            raise ex


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
        elif value.startswith('#'):
            yield Reference(value[1:])
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
