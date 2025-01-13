import json
import ifcopenshell.geom
import ifcopenshell.util
import ifcopenshell.util.element


if __name__ == '__main__':
    print(ifcopenshell.version)
    model = ifcopenshell.open('Output-IFC-metOTLdata.ifc')
    print(model.schema)

    elements = model.by_type('IfcBuildingElementProxy')
    for el in elements:
        property_set = ifcopenshell.util.element.get_psets(el)
        key = next(iter(property_set))
        if not key.startswith('OTL_'):
            continue
        all_info = el.get_info_2(recursive=True)
        gl_id = el.GlobalId
        settings = ifcopenshell.geom.settings()
        representations = el.Representation.Representations
        for representation in representations:
            shape = ifcopenshell.geom.create_shape(settings, el, representation)
            print(shape)
            print(shape.geometry)




        #print(all_info)
        #print(ifcopenshell.util.element.get_psets(el))
        break


# use version 0.7.0.240627

# https://stackoverflow.com/questions/74740941/how-can-i-resolve-this-issue-libm-so-6-version-glibc-2-29-not-found-c-c