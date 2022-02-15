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
    key_name_marker = request.node.get_closest_marker('key_name')
    key_name = key_name_marker.args[0] if key_name_marker else 'key'
    init_mocked = mocker.patch(class_name + '.__init__', return_value=None)
    mocked = mocker.patch('.'.join([class_name, key_name]), new_callable=PropertyMock)
    mocked.side_effect = next_key
    return init_mocked


class DataFile:
    """data file mock"""
    written = {}
    read_lines = ['line\n']
    paths = []
    read_method = False

    def __init__(self, path, mode='r'):
        self.path = path
        DataFile.paths.append(path)
        self.mode = mode

    def __enter__(self):
        return DataFile.read_lines if self.mode == 'r' and not DataFile.read_method else self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def write(self, value):
        """saves written values to static array by file path"""
        if self.path not in DataFile.written:
            DataFile.written[self.path] = []
        DataFile.written[self.path].append(value)

    @staticmethod
    def read():
        """read all lines at once"""
        return ''.join(DataFile.read_lines)

    @staticmethod
    def reset_static(read=None):
        """reset static usage trackers"""
        DataFile.written = {}
        DataFile.read_lines = [line + '\n' for line in read] if read else []
        DataFile.paths = []


@pytest.fixture
def mocker_data_file(request, mocker):
    """patch my_env.data_file"""
    read_method_marker = request.node.get_closest_marker('read_method')
    DataFile.read_method = read_method_marker.args[0] if read_method_marker else False
    return mocker.patch('my_env.data_file', side_effect=DataFile)
