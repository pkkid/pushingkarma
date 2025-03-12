# encoding: utf-8
import logging, re
import json5 as json
from django.db import models
from django.core.exceptions import ValidationError


class ColoredFormatter(logging.Formatter):
    RELVL = r'%\(levelname\)\-7s'
    COLORS = {
        logging.DEBUG: '#555',
        logging.WARNING: '#D93',
        logging.ERROR: '#C21',
        logging.CRITICAL: '#F44',
    }
    
    def __init__(self, fmt=None, **kwargs):
        super().__init__(fmt, **kwargs)
        self._formatters = {}
        substr = re.findall(self.RELVL, fmt)[0]
        for lvl, color in self.COLORS.items():
            newfmt = fmt.replace(substr, self.rgb(substr, color))
            self._formatters[lvl] = logging.Formatter(newfmt)

    def format(self, record):
        formatter = self._formatters.get(record.levelno, super())
        return formatter.format(record)

    def rgb(self, text, color='#aaa'):
        r,g,b = tuple(int(x * 2, 16) for x in color.lstrip('#'))
        return f'\033[38;2;{r};{g};{b}m{text}\033[00m'


class JSON5Field(models.JSONField):
    """ Custom Django field that uses JSON5 for serialization """

    def to_python(self, value):
        try:
            if value is None or isinstance(value, (dict, list)):
                return value
            return json.loads(value)
        except json.JSONDecodeError as err:
            raise ValidationError(f"Invalid JSON5 data: {err}")

    def get_prep_value(self, value):
        if value is None:
            return value
        return json.dumps(value)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)
