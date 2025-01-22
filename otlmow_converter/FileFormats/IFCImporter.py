import logging
import re
import warnings
from calendar import day_abbr
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Self

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

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



@dataclass
class Reference:
    id: str


@dataclass
class IfcOrganization:
    identification: str
    name: str
    description: str
    roles: list[dict]
    addresses: list[dict]


@dataclass
class IfcApplication:
    application_developer: IfcOrganization
    version: str
    application_full_name: str
    Aapplication_identifier: str


@dataclass
class IfcCartesianPoint:
    coordinates: list[float]

    @classmethod
    def convert_to_coords(cls, coords):
        return [float(c) for c in coords]


@dataclass
class IfcDirection:
    direction_ratios: list[float]

    @classmethod
    def convert_to_direction_ratios(cls, ratios):
        return [float(c) for c in ratios]


@dataclass
class IfcAxis2Placement2D:
    ref_direction: IfcDirection
    p: IfcDirection


@dataclass
class IfcAxis2Placement3D:
    axis: IfcDirection
    ref_direction: IfcDirection
    p: IfcDirection


@dataclass
class IfcRepresentationContext:
    context_identifier: str
    context_type: str


@dataclass
class IfcGeometricRepresentationContext(IfcRepresentationContext):
    coordinate_space_dimension: int
    precision: float
    world_coordinate_system: IfcAxis2Placement3D
    true_north: IfcDirection


@dataclass
class IfcGeometricRepresentationSubContext:
    context_identifier: str
    context_type: str
    coordinate_space_dimension: int
    precision: float
    world_coordinate_system: IfcAxis2Placement3D
    true_north: IfcDirection
    parent_context: IfcGeometricRepresentationContext
    target_scale: float
    target_view: str
    user_defined_target_view: str


@dataclass
class IfcPerson:
    identification: str
    family_name: str
    given_name: str
    middle_names: list[str]
    prefix_titles: list[str]
    suffix_titles: list[str]
    roles: list[dict]
    addresses: list[dict]


@dataclass
class IfcPersonAndOrganization:
    the_person: IfcPerson
    the_organization: IfcOrganization
    roles: list[dict]


@dataclass
class IfcOwnerHistory:
    owning_user: IfcPersonAndOrganization
    owning_application: IfcApplication
    state: str
    change_action: str
    last_modification_date: str
    last_modifying_user: IfcPersonAndOrganization
    last_modifying_application: IfcApplication
    creation_date: str


@dataclass
class IfcSIUnit:
    dimensions: str
    unit_type: str
    prefix: str
    name: str


@dataclass
class IfcDimensionalExponents:
    length_exponent: int
    mass_exponent: int
    time_exponent: int
    electric_current_exponent: int
    thermodynamic_temperature_exponent: int
    amount_of_substance_exponent: int
    luminous_intensity_exponent: int


@dataclass
class IfcMeasureWithUnit:
    value_component: float
    unit_component: IfcSIUnit


@dataclass
class IfcConversionBasedUnit:
    dimensions: str
    unit_type: str
    name: str
    conversion_factor: IfcMeasureWithUnit


@dataclass
class IfcUnitAssignment:
    units: list[dict]


@dataclass
class IfcProject:
    global_id: str
    owner_history: IfcOwnerHistory
    name: str
    description: str
    object_type: str
    long_name: str
    phase: str
    representation_contexts: list[dict]
    units_in_context: IfcUnitAssignment


@dataclass
class IfcObjectPlacement:
    placement_rel_to: Self

@dataclass
class IfcLocalPlacement: # inherits from IfcObjectPlacement
    placement_rel_to: IfcObjectPlacement
    relative_placement: IfcAxis2Placement3D


@dataclass
class IfcSite:
    global_id: str
    owner_history: IfcOwnerHistory
    name: str
    description: str
    object_type: str
    object_placement: IfcObjectPlacement
    representation: str
    long_name: str
    composition_type: str
    ref_latitude: float
    ref_longitude: float
    ref_elevation: float
    land_title_number: str
    site_address: str


@dataclass
class IfcLoop:
    pass


@dataclass
class IfcPolyLoop(IfcLoop):
    polygon: list[IfcCartesianPoint]

    @classmethod
    def convert_to_points(cls, _args):
        return [p for p in _args]


@dataclass
class IfcFaceBound:
    bound: IfcLoop
    orientation: bool


@dataclass
class IfcFaceOuterBound(IfcFaceBound):
    bound: IfcLoop
    orientation: bool


@dataclass
class IfcFace:
    bounds: list[IfcFaceBound]

    @classmethod
    def convert_to_bounds(cls, _args):
        return [b for b in _args]

@dataclass
class IfcClosedShell:
    cfs_faces: list[IfcFace]

    @classmethod
    def convert_to_faces(cls, _args):
        return [f for f in _args]


@dataclass
class IfcFacetedBrep:
    outer: IfcClosedShell


@dataclass
class IfcColourRgb:
    name: str
    red: float
    green: float
    blue: float


@dataclass
class IfcSurfaceStyleRendering:
    surface_colour: IfcColourRgb
    transparency: float
    diffuse_colour: object
    transmission_colour: object
    diffuse_transmission_colour: object
    reflection_colour: object
    specular_colour: object
    specular_highlight: object
    reflectance_method: str


@dataclass
class IfcPresentationStyle:
    name: str


@dataclass
class IfcSurfaceStyle(IfcPresentationStyle):
    side: str
    styles: list[IfcSurfaceStyleRendering]


@dataclass
class IfcRepresentationItem:
    pass

@dataclass
class IfcStyledItem:
    item: IfcRepresentationItem
    styles: list[IfcPresentationStyle]
    name: str


@dataclass
class IfcShapeRepresentation:
    context_of_items: IfcGeometricRepresentationContext
    representation_identifier: str
    representation_type: str
    items: list[IfcRepresentationItem]


@dataclass
class IfcProductRepresentation:
    name: str
    description: str
    representations: list[IfcShapeRepresentation]

@dataclass
class IfcProductDefinitionShape(IfcProductRepresentation):
    pass


@dataclass
class IfcRoot:
    global_id: str
    owner_history: IfcOwnerHistory
    name: str
    description: str


@dataclass
class IfcObjectDefinition(IfcRoot):
    object_type: str

@dataclass
class IfcObject(IfcObjectDefinition):
    object_type: str


@dataclass
class IfcProduct(IfcObject):
    object_placement: IfcObjectPlacement
    representation: IfcProductRepresentation

@dataclass
class IfcElement(IfcProduct):
    tag: str


@dataclass
class IfcBuiltElement(IfcElement):
    pass


@dataclass
class IfcBuildingElementProxy(IfcBuiltElement):
    predefined_type: str


@dataclass
class IfcProperty:
    name: str
    specification: str

@dataclass
class IfcSimpleProperty(IfcProperty):
    pass

@dataclass
class IfcPropertySingleValue(IfcSimpleProperty):
    nominal_value: str
    unit: str


@dataclass
class IfcPropertyDefinition(IfcRoot):
    pass

@dataclass
class IfcPropertySetDefinition(IfcPropertyDefinition):
    pass

@dataclass
class IfcPropertySet(IfcPropertySetDefinition):
    properties: list[IfcProperty]


@dataclass
class IfcRelationship(IfcRoot):
    pass

@dataclass
class IfcRelDefines(IfcRelationship):
    pass

@dataclass
class IfcRelDefinesByProperties(IfcRelDefines):
    related_objects: list[IfcObjectDefinition]
    property_definition: IfcPropertySetDefinition

@dataclass
class IfcRelConnects(IfcRelationship):
    pass


@dataclass
class IfcSpatialElement(IfcProduct):
    long_name: str


@dataclass
class IfcSpatialStructureElement(IfcSpatialElement):
    pass

@dataclass
class IfcRelContainedInSpatialStructure(IfcRelConnects):
    related_elements: list[IfcProduct]
    relating_structure: IfcSpatialElement


@dataclass
class IfcRelDecomposes(IfcRelationship):
    pass


@dataclass
class IfcRelAggregates(IfcRelDecomposes):
    relating_object: IfcObjectDefinition
    related_objects: list[IfcObjectDefinition]


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
    def ifc_to_ifc_dict(cls, filepath):
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
                last_id = cls.parse_groups_to_master_dict(groups=groups, master_dict=d)

        d['root'] = Reference(last_id)

        return d


    @classmethod
    def parse_groups_to_master_dict(cls, groups, master_dict) -> str:
        _id = groups.group(1)
        _type = groups.group(2)
        _args = groups.group(3)

        c = cls.instantiate_ifc_object(ifc_type=_type, id=_id, args=_args)
        master_dict[_id] = c
        return _id

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
