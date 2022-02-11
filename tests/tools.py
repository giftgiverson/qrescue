"""
Testing tools
"""

from copy import copy
from functools import update_wrapper
from types import FunctionType


def copy_func(func, new_globals=None, module=None):
    """Based on https://stackoverflow.com/a/13503277/2988730 (@unutbu)"""
    if new_globals is None:
        new_globals = func.__globals__
    f_type = FunctionType(func.__code__, new_globals, name=func.__name__,
                     argdefs=func.__defaults__, closure=func.__closure__)
    f_type = update_wrapper(f_type, func)
    if module is not None:
        f_type.__module__ = module
    f_type.__kwdefaults__ = copy(func.__kwdefaults__)
    return f_type
