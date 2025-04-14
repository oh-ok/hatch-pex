def check_type(obj, t, fmt=None, **k):
    if fmt is None:
        fmt = "Expected {type}; got {objtype} ({obj!r})"
    if not isinstance(obj, t):
        raise TypeError(fmt.format(obj=obj, objtype=type(obj), type=t, **k))
    return obj


def check_list_type(obj, t, fmt=None, **k):
    if fmt is None:
        fmt = "Expected {type}; got {objtype} ({obj!r})"
    if not isinstance(obj, list):
        raise TypeError(fmt.format(obj=obj, objtype=type(obj), type=t, **k))
    if not all(isinstance(x, t) for x in obj):
        raise TypeError(fmt.format(obj=obj, objtype=type(obj), type=t, **k))
    return obj
