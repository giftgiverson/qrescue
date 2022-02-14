"""
Test helpers
"""

import pytest


@pytest.fixture
def mocker_file_read_lines(request, mocker):
    """mock opening a file with three lines"""
    lines_marker = request.node.get_closest_marker('file_lines')
    lines = ('\n'.join(lines_marker.args) + '\n') if lines_marker else ''
    mocked_folder_file_data = mocker.mock_open(read_data=lines)
    return mocker.patch('builtins.open', mocked_folder_file_data)
