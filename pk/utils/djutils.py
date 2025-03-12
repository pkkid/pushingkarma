# encoding: utf-8
import logging, re

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
            newfmt = fmt.replace(substr, rgb(substr, color))
            self._formatters[lvl] = logging.Formatter(newfmt)

    def format(self, record):
        formatter = self._formatters.get(record.levelno, super())
        return formatter.format(record)


def rgb(text, color='#aaa'):
    """ Easy way to color text in bash. """
    r,g,b = tuple(int(x * 2, 16) for x in color.lstrip('#'))
    return f'\033[38;2;{r};{g};{b}m{text}\033[00m'
