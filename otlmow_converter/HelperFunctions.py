# from otlmow-modelbuilder
def get_shortened_uri(object_uri: str):
    if 'https://wegenenverkeer.data.vlaanderen.be/ns/' not in object_uri:
        raise ValueError(f'{object_uri} is not a valid uri to extract a namespace from')
    return object_uri.split('/ns/')[1]


def get_ns_and_name_from_uri(object_uri):
    short_uri = get_shortened_uri(object_uri)
    short_uri_array = short_uri.split('#')
    return short_uri_array[0], short_uri_array[1]


def get_class_directory_from_ns(ns):
    return 'Classes/' + get_titlecase_from_ns(ns)


def get_titlecase_from_ns(ns: str) -> str:
    if ns == 'abstracten':
        return 'Abstracten'
    elif ns == 'implementatieelement':
        return 'ImplementatieElement'
    elif ns == 'installatie':
        return 'Installatie'
    elif ns == 'levenscyclus':
        return 'Levenscyclus'
    elif ns == 'onderdeel':
        return 'Onderdeel'
    elif ns == 'proefenmeting':
        return 'ProefEnMeting'
    else:
        raise ValueError()


def wrap_in_quotes(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError
    if text == '':
        return "''"
    singles = sum(1 for c in text if c == "'")
    doubles = sum(1 for c in text if c == '"')
    if singles > doubles:
        if doubles > 0:
            return '"' + text.replace('"', '\\"') + '"'
        return '"' + text + '"'
    else:
        if singles > 0:
            return "'" + text.replace("'", "\\'") + "'"
        return "'" + text + "'"
