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
