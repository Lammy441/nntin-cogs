import json
from datetime import datetime


def _tojson(_object, depth: int):
    res = {}

    if isinstance(_object, list):
        # Note: limiting array to 10 so you don't parse 10000 members
        if depth > 0:
            return [_tojson(_obj, depth-1) for _obj in _object[:10]]
        else:
            return [str(_obj)[:50] for _obj in _object[:10]]

    if isinstance(_object, datetime):
        return str(_object)

    for slot in dir(_object):
        if not slot.startswith('_') and hasattr(_object, slot):
            value = getattr(_object, slot)
            if callable(value):
                continue
            try:
                json.dumps(value)
            except TypeError:
                if depth > 0:
                    value = _tojson(value, depth-1)
                else:
                    value = str(value)[:50]
            finally:
                res[slot] = value
    return res


def tojson(tuplelist: list, depth=3):
    res = {}

    for _tuple in tuplelist:
        res[_tuple[0]] = _tojson(_tuple[1], depth)

    return json.dumps(res)
