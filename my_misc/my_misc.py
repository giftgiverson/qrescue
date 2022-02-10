"""
Implementation of miscellaneous helpers
"""


def static_vars(**kwargs):
    """
    static vars decorator
    :param kwargs: initialization
    :return: decorator
    """
    def decorate(func):
        for k, arg in kwargs.items():
            setattr(func, k, arg)
        return func

    return decorate
