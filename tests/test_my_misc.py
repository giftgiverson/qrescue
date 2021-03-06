"""
Tests for my_misc
"""

from my_misc.my_misc import static_vars


# pylint: disable=no-member
@static_vars(one=1, two=2)
def target():
    """
    :return: current static vars value
    """
    target.one += 1
    target.two += 2
    return target.one, target.two


def test_decorate():
    """
    Tests the static_vars decoration.
    Static vars should increase by (+1, +2) on each call.
    """
    assert target() == (2, 4)
    assert target() == (3, 6)
