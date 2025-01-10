import ifcopenshell.util
import ifcopenshell.util.element


if __name__ == '__main__':
    print(ifcopenshell.version)
    model = ifcopenshell.open('Output-IFC-metOTLdata.ifc')
    print(model.schema)

    elements = model.by_type('IfcElement')
    for el in elements:
        print(ifcopenshell.util.element.get_psets(el))


# use version 0.7.0.240627

# https://stackoverflow.com/questions/74740941/how-can-i-resolve-this-issue-libm-so-6-version-glibc-2-29-not-found-c-c