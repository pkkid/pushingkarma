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
            newfmt = fmt.replace(substr, self.rgb(substr, color))
            self._formatters[lvl] = logging.Formatter(newfmt)

    def format(self, record):
        formatter = self._formatters.get(record.levelno, super())
        return formatter.format(record)
    
    def rgb(self, text, color='#aaa', reset=True):
        r,g,b = tuple(int(x * 2, 16) for x in color.lstrip('#'))
        rgbstr = f'\033[38;2;{r};{g};{b}m{text}'
        rgbstr += '\033[00m' if reset else ''
        return rgbstr


def update_logging_filepath(filepath, handler_name='default'):
    """ Update logging filehandler to the specified filepath. """
    for handler in logging.getLogger().handlers:
        if handler._name == handler_name and isinstance(handler, logging.FileHandler):
            handler.close()
            handler.baseFilename = filepath
            handler.stream = handler._open()
            break
    else:
        raise Exception(f'Unknown filehandler name {handler_name}')
