# -*- coding: UTF-8 -*-
"""Common utility functions.

"""
try:  # Python2
    import __builtin__ as builtins
except ImportError:
    import builtins
import ctypes
import os
from functools import update_wrapper
from itertools import cycle
from string import printable
try:                 # Python 2
    from urlparse import urlparse, parse_qs as urlparse_query
except ImportError:  # Python 3
    from urllib.parse import urlparse, parse_qs as urlparse_query

from .compat import b
from .constants import PYTHON3, WINDOWS


__all__ = __features__ = ["human_readable_size", "is_admin", "set_exception", "strings", "strings_from_file",
                          "urlparse", "urlparse_query", "xor", "xor_file", "withrepr"]


def human_readable_size(size, precision=0):
    """ Convert size in bytes to a more readable form. """
    if not isinstance(size, (int, float)):
        raise ValueError("Bad size")
    if size < 0:
        raise ValueError("Size cannot be negative")
    i, units = 0, ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    while size > 1024 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.*f%s" % (precision, size, units[i])


def is_admin():
    """ Check if the user running the script is admin. """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0 if WINDOWS else os.geteuid() == 0
    except AttributeError:
        raise NotImplementedError("Admin check is not implemented for this operating system.")


class range2object:
    """ Class for making a range of floats (alternative to the native range() function). """
    def __new__(cls, *args):
        self = super(range2object, cls).__new__(cls)
        l = len(args)
        if l == 0:
            raise TypeError("range2 expected 1 argument, got 0")
        elif l == 1:
            self.start, self.stop, self.step = 0., float(args[0]), 1.
        elif l == 2:
            self.start, self.stop, self.step = float(args[0]), float(args[1]), 1.
        elif l == 3:
            self.start, self.stop, self.step = list(map(float, args))
        else:
            raise TypeError("range2 expected at most 3 arguments, got %s" % l)
        return self
    
    def __iter__(self):
        n_rnd, cursor = max(len(str(f).split(".")[1]) for f in [self.start, self.stop, self.step]), self.start
        while cursor < [1, -1][self.step < 0] * self.stop:
            yield round(cursor, n_rnd)
            cursor += self.step
    
    def __len__(self):
        for i, _ in enumerate(self):
            pass
        return i + 1
    
    def __repr__(self):
        v = [[self.start, self.stop], [self.start, self.stop, self.step]][self.step != 1.]
        return "range(%s)" % ", ".join(map(str, v))
    
    def count(self, value):
        """ return number of occurrences of value """
        n = 0
        for x in self:
            if value == x:
                n += 1
        return n
    
    def index(self, value):
        """ return index of value """
        for i, x in enumerate(self):
            if value == x:
                return i
        raise ValueError("%s is not in range" % str(value))
builtins.range2 = range2object


def set_exception(name, etype="ValueError"):
    """ Set a custom exception in the builtins. """
    if not hasattr(builtins, name):
        exec("class %s(%s): __module__ = 'builtins'" % (name, etype))
        setattr(builtins, name, locals()[name])
set_exception("RequirementError", "ImportError")


def strings(data, minlen=4, alphabet=printable):
    """ Generator yielding strings according to a charset and a minimal length from a given string buffer.

    :param data:     input data
    :param minlen:   minimal length of strings to be considered
    :param alphabet: valid charset for the strings
    """
    result = ""
    for c in b(data):
        if c in b(alphabet):
            result += chr(c) if PYTHON3 else c
            continue
        if len(result) >= minlen:
            yield result
        result = ""
    if len(result) >= minlen:
        yield result


def strings_from_file(filename, minlen=4, alphabet=printable, offset=0):
    """ Generator yielding strings according to a charset and a minimal length from a given file.
    
    :param filename: input file
    :param minlen:   minimal length of strings to be considered
    :param alphabet: valid charset for the strings
    :param offset:   start offset in the input file
    """
    with open(filename, 'rb') as f:
        f.seek(offset)
        result = ""
        while True:
            data = f.read(max(1024, 2 * minlen))
            if not data:
                break
            for c in data:
                if c in b(alphabet):
                    result += chr(c) if PYTHON3 else c
                    continue
                if len(result) >= minlen:
                    yield result
                result = ""
        if len(result) >= minlen:
            yield result


def xor(str1, str2, offset=0):
    """ Function for XORing two strings of different length. Either the first or the second string can be longer.

    :param str1:   first string, with length L1
    :param str2:   second string, with length L2
    :param offset: ASCII offset to be applied on each resulting character
    """
    convert = isinstance(str1[0], int) or isinstance(str2[0], int)
    r = b("") if convert else ""
    for c1, c2 in zip(cycle(str1) if len(str1) < len(str2) else str1, cycle(str2) if len(str2) < len(str1) else str2):
        c1 = c1 if isinstance(c1, int) else ord(c1)
        c2 = c2 if isinstance(c2, int) else ord(c2)
        c = chr(((c1 ^ c2) + offset) % 256)
        r += b(c) if convert else c
    return r


def xor_file(filename, key, offset=0):
    """ Function for XORing a file with a given key.

    :param filename: input file
    :param key:      XOR key
    :param offset:   start offset in the input file
    """
    with open(filename, 'rb+') as f:
        cursor, l = offset, len(key)
        f.seek(cursor)
        while True:
            data = f.read(l)
            if not data:
                break
            f.seek(cursor)
            f.write(xor(data, b(key[:len(data)])))
            cursor += l


# https://stackoverflow.com/questions/10875442/possible-to-change-a-functions-repr-in-python
class __reprwrapper(object):
    def __init__(self, repr, func):
        self._repr, self._func = repr, func
        update_wrapper(self, func)
    
    def __call__(self, *args, **kw):
        return self._func(*args, **kw)
    
    def __repr__(self):
        return self._repr(self._func)


def withrepr(func_repr):
    """ Decorator for modifying the representation of a function. """
    def _wrapper(f):
        return __reprwrapper(func_repr, f)
    return _wrapper

