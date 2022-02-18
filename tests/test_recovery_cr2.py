"""
Tests for CR2 file handling
"""
import os
import recovery.cr2


# pylint: disable=protected-access
def test_get_cr2_datetime_offset():
    """tests getting date and time from CR2 file"""
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'f3662951424.cr2')
    assert recovery.cr2._get_cr2_datetime_offset(path) == '2006:06:09 00:50:52'
