"""
Tests for affected.index
"""
import pytest

import my_env.my_env
from affected.index import load_pyon_data_file


# region mocks


@pytest.fixture
def mocker_file_read_lines(mocker):
    """mock opening a file with encoded python data-file with encoded dictionary"""
    mocker.patch.object(my_env.my_env, 'DATA_FOLDER', 'flying_circus/')
    mocked_folder_file_data = \
        mocker.mock_open(
            read_data=
            "{'ext': {-1: 100, 0: 1000, 100: 1, 1000: 2},"
            " 'EXT': {-1: 200, 0: 1000, 200: 2, 1000: 1}, }")
    return mocker.patch('builtins.open', mocked_folder_file_data)


# endregion mocks


# region tests

# pylint: disable=redefined-outer-name
def test_load_pyon_data_file(mocker_file_read_lines):
    """test correct loading of pyon data file"""
    actual = [(e, list(o.items())) for e, o in load_pyon_data_file('monty').items()]
    expected = [('ext', [(-1, 100), (0, 1000), (100, 1), (1000, 2)]),
                ('EXT', [(-1, 200), (0, 1000), (200, 2), (1000, 1)])]
    assert expected == actual
    mocker_file_read_lines.assert_called_with('flying_circus/monty.pyon', 'r', encoding='utf8')

# endregion
