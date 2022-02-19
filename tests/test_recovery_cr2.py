"""
Tests for CR2 file handling
"""
import os
import recovery.cr2


def test_get_cr2_datetime_offset():
    """tests getting date and time from CR2 file"""
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'f3662951424.cr2')
    assert recovery.cr2.get_cr2_datetime_offset(path) == 1149803452.0
