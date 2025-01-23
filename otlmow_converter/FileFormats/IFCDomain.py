from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Reference:
    id: str


@dataclass(frozen=True)
class IfcRatioMeasure:
    value: float

@dataclass(frozen=True)
class IfcOrganization:
    identification: str
    name: str
    description: str
    roles: list[dict]
    addresses: list[dict]


@dataclass(frozen=True)
class IfcApplication:
    application_developer: IfcOrganization
    version: str
    application_full_name: str
    application_identifier: str


@dataclass(frozen=True)
class IfcCartesianPoint:
    coordinates: list[float]

    @classmethod
    def convert_to_coords(cls, coords):
        return [float(c) for c in coords]


@dataclass(frozen=True)
class IfcDirection:
    direction_ratios: list[float]

    @classmethod
    def convert_to_direction_ratios(cls, ratios):
        return [float(c) for c in ratios]


@dataclass(frozen=True)
class IfcAxis2Placement2D:
    ref_direction: IfcDirection
    p: IfcDirection


@dataclass(frozen=True)
class IfcAxis2Placement3D:
    axis: IfcDirection
    ref_direction: IfcDirection
    p: IfcDirection


@dataclass(frozen=True)
class IfcRepresentationContext:
    context_identifier: str
    context_type: str


@dataclass(frozen=True)
class IfcGeometricRepresentationContext(IfcRepresentationContext):
    coordinate_space_dimension: int
    precision: float
    world_coordinate_system: IfcAxis2Placement3D
    true_north: IfcDirection


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class IfcPerson:
    identification: str
    family_name: str
    given_name: str
    middle_names: list[str]
    prefix_titles: list[str]
    suffix_titles: list[str]
    roles: list[dict]
    addresses: list[dict]


@dataclass(frozen=True)
class IfcPersonAndOrganization:
    the_person: IfcPerson
    the_organization: IfcOrganization
    roles: list[dict]


@dataclass(frozen=True)
class IfcOwnerHistory:
    owning_user: IfcPersonAndOrganization
    owning_application: IfcApplication
    state: str
    change_action: str
    last_modification_date: str
    last_modifying_user: IfcPersonAndOrganization
    last_modifying_application: IfcApplication
    creation_date: str


@dataclass(frozen=True)
class IfcSIUnit:
    dimensions: str
    unit_type: str
    prefix: str
    name: str


@dataclass(frozen=True)
class IfcDimensionalExponents:
    length_exponent: int
    mass_exponent: int
    time_exponent: int
    electric_current_exponent: int
    thermodynamic_temperature_exponent: int
    amount_of_substance_exponent: int
    luminous_intensity_exponent: int


@dataclass(frozen=True)
class IfcMeasureWithUnit:
    value_component: float
    unit_component: IfcSIUnit


@dataclass(frozen=True)
class IfcConversionBasedUnit:
    dimensions: str
    unit_type: str
    name: str
    conversion_factor: IfcMeasureWithUnit


@dataclass(frozen=True)
class IfcUnitAssignment:
    units: list[dict]


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class IfcObjectPlacement:
    placement_rel_to: Self


@dataclass(frozen=True)
class IfcLocalPlacement: # inherits from IfcObjectPlacement
    placement_rel_to: IfcObjectPlacement
    relative_placement: IfcAxis2Placement3D


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class IfcLoop:
    pass


@dataclass(frozen=True)
class IfcPolyLoop(IfcLoop):
    polygon: list[IfcCartesianPoint]

    @classmethod
    def convert_to_points(cls, _args):
        return [p for p in _args]


@dataclass(frozen=True)
class IfcFaceBound:
    bound: IfcLoop
    orientation: bool


@dataclass(frozen=True)
class IfcFaceOuterBound(IfcFaceBound):
    bound: IfcLoop
    orientation: bool


@dataclass(frozen=True)
class IfcFace:
    bounds: list[IfcFaceBound]

    @classmethod
    def convert_to_bounds(cls, _args):
        return [b for b in _args]


@dataclass(frozen=True)
class IfcClosedShell:
    cfs_faces: list[IfcFace]

    @classmethod
    def convert_to_faces(cls, _args):
        return [f for f in _args]


@dataclass(frozen=True)
class IfcFacetedBrep:
    outer: IfcClosedShell


@dataclass(frozen=True)
class IfcColourRgb:
    name: str
    red: float
    green: float
    blue: float


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class IfcPresentationStyle:
    name: str


@dataclass(frozen=True)
class IfcSurfaceStyle(IfcPresentationStyle):
    side: str
    styles: list[IfcSurfaceStyleRendering]


@dataclass(frozen=True)
class IfcRepresentationItem:
    pass


@dataclass(frozen=True)
class IfcStyledItem:
    item: IfcRepresentationItem
    styles: list[IfcPresentationStyle]
    name: str


@dataclass(frozen=True)
class IfcShapeRepresentation:
    context_of_items: IfcGeometricRepresentationContext
    representation_identifier: str
    representation_type: str
    items: list[IfcRepresentationItem]


@dataclass(frozen=True)
class IfcProductRepresentation:
    name: str
    description: str
    representations: list[IfcShapeRepresentation]


@dataclass(frozen=True)
class IfcProductDefinitionShape(IfcProductRepresentation):
    pass


@dataclass(frozen=True)
class IfcRoot:
    global_id: str
    owner_history: IfcOwnerHistory
    name: str
    description: str


@dataclass(frozen=True)
class IfcObjectDefinition(IfcRoot):
    object_type: str


@dataclass(frozen=True)
class IfcObject(IfcObjectDefinition):
    object_type: str


@dataclass(frozen=True)
class IfcProduct(IfcObject):
    object_placement: IfcObjectPlacement
    representation: IfcProductRepresentation


@dataclass(frozen=True)
class IfcElement(IfcProduct):
    tag: str


@dataclass(frozen=True)
class IfcBuiltElement(IfcElement):
    pass


@dataclass(frozen=True)
class IfcBuildingElementProxy(IfcBuiltElement):
    predefined_type: str


@dataclass(frozen=True)
class IfcProperty:
    name: str
    specification: str


@dataclass(frozen=True)
class IfcSimpleProperty(IfcProperty):
    pass


@dataclass(frozen=True)
class IfcPropertySingleValue(IfcSimpleProperty):
    nominal_value: str
    unit: str


@dataclass(frozen=True)
class IfcPropertyDefinition(IfcRoot):
    pass


@dataclass(frozen=True)
class IfcPropertySetDefinition(IfcPropertyDefinition):
    pass


@dataclass(frozen=True)
class IfcPropertySet(IfcPropertySetDefinition):
    properties: list[IfcProperty]


@dataclass(frozen=True)
class IfcRelationship(IfcRoot):
    pass


@dataclass(frozen=True)
class IfcRelDefines(IfcRelationship):
    pass


@dataclass(frozen=True)
class IfcRelDefinesByProperties(IfcRelDefines):
    related_objects: list[IfcObjectDefinition]
    property_definition: IfcPropertySetDefinition


@dataclass(frozen=True)
class IfcRelConnects(IfcRelationship):
    pass


@dataclass(frozen=True)
class IfcSpatialElement(IfcProduct):
    long_name: str


@dataclass(frozen=True)
class IfcSpatialStructureElement(IfcSpatialElement):
    pass


@dataclass(frozen=True)
class IfcRelContainedInSpatialStructure(IfcRelConnects):
    related_elements: list[IfcProduct]
    relating_structure: IfcSpatialElement


@dataclass(frozen=True)
class IfcRelDecomposes(IfcRelationship):
    pass


@dataclass(frozen=True)
class IfcRelAggregates(IfcRelDecomposes):
    relating_object: IfcObjectDefinition
    related_objects: list[IfcObjectDefinition]


@dataclass(frozen=True)
class IfcNormalisedRatioMeasure(IfcRatioMeasure):
    pass

@dataclass(frozen=True)
class IfcLabel:
    value: str