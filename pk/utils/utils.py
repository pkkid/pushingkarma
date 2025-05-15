# encoding: utf-8
import datetime
from calendar import monthrange
from decimal import Decimal


def add_months(dt, months):
    """ Add months to a datetime. """
    if not dt or not months: return dt
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def clean_amount(value):
    """ Clean a USD string such as -$99.99 to a Decimal value. """
    if isinstance(value, str):
        value = value.replace('$', '')
        value = value.replace(',', '')
        return Decimal(value)
    if isinstance(value, (int, float)):
        return Decimal(value)
    return value


def first_of_month(dt):
    """ Get the first day of the month for a given date. """
    if isinstance(dt, datetime.datetime):
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif isinstance(dt, datetime.date):
        return dt.replace(day=1)
    raise TypeError('dt must be a datetime.date or datetime.datetime object')


def percent(numerator, demoniator, precision=2):
    """ Calculate the percentage of a number. """
    if not demoniator:
        return 0
    return round(numerator / demoniator * 100, precision) if demoniator else 0


def rgb(text, color='#aaa', reset=True):
    """ Convert a hex color to RGB for logging or console output. """
    r,g,b = tuple(int(x * 2, 16) for x in color.lstrip('#'))
    rgbstr = f'\033[38;2;{r};{g};{b}m{text}'
    rgbstr += '\033[00m' if reset else ''
    return rgbstr


def rget(obj, attrstr, default=None, delim='.'):
    """ Recursively get an attribute from an object or dict. """
    try:
        parts = attrstr.split(delim, 1)
        attr = parts[0]
        attrstr = parts[1] if len(parts) == 2 else None
        attrint = to_int(attr)
        if isinstance(obj, dict): value = obj[attr]
        elif isinstance(obj, list) and attrint is not None: value = obj[attrint]
        elif isinstance(obj, tuple) and attrint is not None: value = obj[attrint]
        elif isinstance(obj, object): value = getattr(obj, attr)
        if attrstr: return rget(value, attrstr, default, delim)
        return value
    except Exception:
        return default


def rset(obj, attrstr, value, delim='.'):
    """ Recursively set an attribute on an object or dict. """
    parts = attrstr.split(delim, 1)
    attr = parts[0]
    attrstr = parts[1] if len(parts) == 2 else None
    if attr not in obj: obj[attr] = {}
    if attrstr: rset(obj[attr], attrstr, value, delim)
    else: obj[attr] = value


def to_int(value):
    """ Convert a string to an int. """
    try:
        return int(value)
    except ValueError:
        return None
