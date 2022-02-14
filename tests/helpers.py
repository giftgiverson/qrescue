"""
Test helpers
"""

import pytest
from mock import PropertyMock

from my_misc import static_vars


@pytest.fixture
def mocker_file_read_lines(request, mocker):
    """mock opening a file with three lines"""
    lines_marker = request.node.get_closest_marker('file_lines')
    lines = ('\n'.join(lines_marker.args) + '\n') if lines_marker else ''
    mocked_folder_file_data = mocker.mock_open(read_data=lines)
    return mocker.patch('builtins.open', mocked_folder_file_data)


# pylint: disable=no-member
@static_vars(key=0)
def next_key():
    """provides an increasing key for each call"""
    next_key.key += 1
    return next_key.key


@pytest.fixture
def mocker_keyed_class(request, mocker):
    """overrides <class>__init__ and provides an increasing key for each call to <class>.key"""
    class_name = request.node.get_closest_marker('class_name').args[0]
    init_mocked = mocker.patch(class_name + '.__init__', return_value=None)
    mocked = mocker.patch(class_name + '.key', new_callable=PropertyMock)
    mocked.side_effect = next_key
    return init_mocked
