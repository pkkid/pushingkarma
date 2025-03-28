# encoding: utf-8
from decimal import Decimal


def clean_amount(value):
    """ Clean a USD string such as -$99.99 to a Decimal value. """
    if isinstance(value, str):
        value = value.replace('$', '')
        value = value.replace(',', '')
        return Decimal(value)
    if isinstance(value, (int, float)):
        return Decimal(value)
    return value


def percent(numerator, demoniator, precision=2):
    if not demoniator:
        return 0
    return round(numerator / demoniator * 100, precision) if demoniator else 0


def rgb(text, color='#aaa', reset=True):
    r,g,b = tuple(int(x * 2, 16) for x in color.lstrip('#'))
    rgbstr = f'\033[38;2;{r};{g};{b}m{text}'
    rgbstr += '\033[00m' if reset else ''
    return rgbstr


def rget(obj, attrstr, default=None, delim='.'):
    try:
        parts = attrstr.split(delim, 1)
        attr = parts[0]
        attrstr = parts[1] if len(parts) == 2 else None
        if isinstance(obj, dict): value = obj[attr]
        elif isinstance(obj, list): value = obj[int(attr)]
        elif isinstance(obj, tuple): value = obj[int(attr)]
        elif isinstance(obj, object): value = getattr(obj, attr)
        if attrstr: return rget(value, attrstr, default, delim)
        return value
    except Exception:
        return default


def rset(obj, attrstr, value, delim='.'):
    parts = attrstr.split(delim, 1)
    attr = parts[0]
    attrstr = parts[1] if len(parts) == 2 else None
    if attr not in obj: obj[attr] = {}
    if attrstr: rset(obj[attr], attrstr, value, delim)
    else: obj[attr] = value


def toback(obj, *keys):
    """ Move keys to the back of dict. """
    for key in keys:
        value = obj.pop(key)
        obj[key] = value
    return obj
