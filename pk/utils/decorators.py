# encoding: utf-8


def lazyproperty(func):
    """ Decorator that makes a property lazy-evaluated.
        http://stevenloria.com/lazy-evaluated-properties-in-python/
    """
    attr_name = '_lazy_%s' % func.__name__
    @property  # noqa
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)
    return wrapper
