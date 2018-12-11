import json


def _tojson(_object):
    res = {}
    if not hasattr(_object, '__slots__'):
        return str(_object)
    for slot in _object.__slots__:
        if not slot.startswith('_') and hasattr(_object, slot):
            value = getattr(_object, slot)
            try:
                json.dumps(value)
            except TypeError:
                value = _tojson(value)
            finally:
                res[slot] = value
    return res


def tojson(tuplelist: list):
    res = {}

    for _tuple in tuplelist:
        res[_tuple[0]] = _tojson(_tuple[1])

    return json.dumps(res)
