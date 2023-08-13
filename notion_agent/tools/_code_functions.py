def extract_key(d: dict, *key: str) -> dict:
    """Returns the value of a possibly nested key in @d given by @key."""
    for k in key:
        d = d[k]
    return d

def print_dict_key_value(d: dict, *key: str) -> None:
    """Prints the value of a possibly nested key in @d given by @key."""
    print(extract_key(d, *key))
