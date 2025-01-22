from dataclasses import dataclass
from typing import Self


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
