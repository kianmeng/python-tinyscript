# -*- coding: UTF-8 -*-
"""Common checking functions and argument types.

"""
from .strings import _str2list


__all__ = __features__ = []

try:
    long
except NameError:
    long = int


# various object type check functions
__all__ += ["is_dict", "is_function", "is_int", "is_lambda", "is_list",
            "is_neg_int", "is_pos_int"]
is_int      = lambda i: isinstance(i, (int, long))
is_pos_int  = lambda i, zero=True: is_int(i) and (i >= 0 if zero else i > 0)
is_neg_int  = lambda i, zero=False: is_int(i) and (i <= 0 if zero else i < 0)
is_dict     = lambda d: isinstance(d, dict)
is_list     = lambda l: isinstance(l, (list, set, tuple))
is_lambda   = lambda l: isinstance(l, type(lambda:0)) and \
                        l.__name__ == (lambda:0).__name__
is_function = lambda f: hasattr(f, "__call__")


# -------------------- DATA FORMAT ARGUMENT TYPES --------------------
__all__ += ["neg_int", "negative_int", "pos_int", "positive_int", "ints",
            "neg_ints", "negative_ints", "pos_ints", "positive_ints"]


def __ints(l, check_func=lambda x: False, idescr=None, **kwargs):
    """ Parses a comma-separated list of ints. """
    l = _str2list(l)
    msg = "{} {}integer{}".format(["Bad list of", "Not a"][len(l) == 1],
                                  "" if idescr is None else idescr + " ",
                                  ["s", ""][len(l) == 1])
    if not all(check_func(_, **kwargs) for _ in l):
        raise ValueError(msg)
    return l
ints = lambda l: __ints(l, is_int)
negative_int = neg_int = \
    lambda i, zero=False: __ints(i, is_neg_int, "negative", zero=zero)[0]
positive_int = pos_int = \
    lambda i, zero=True: __ints(i, is_pos_int, "positive", zero=zero)[0]
negative_ints = neg_ints = \
    lambda l, zero=False: __ints(l, is_neg_int, "negative", zero=zero)
positive_ints = pos_ints = \
    lambda l, zero=True: __ints(l, is_pos_int, "positive", zero=zero)
