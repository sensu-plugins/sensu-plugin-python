import functools


class ConfCache(object):
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if self.func not in self.cache:
            self.cache[self.func] = {}
        try:
            return self.cache[self.func][args]
        except KeyError:
            value = self.func(*args)
            self.cache[self.func][args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        fnction = functools.partial(self.__call__, obj)
        try:
            self.cache = obj.cache
        except AttributeError:
            obj.cache = {}
            self.cache = obj.cache
        return fnction
