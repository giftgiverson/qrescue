"""
Tests for affected.folders
"""
from mock import PropertyMock
import pytest
from affected.folders import AffectedFolder, load_folders
from my_misc import static_vars


# region global mocks


@pytest.fixture
def mocker_file_read_lines(mocker):
    """mock opening a file with three lines"""
    mocked_folder_file_data = mocker.mock_open(read_data='line1\nline2\nline3\n')
    return mocker.patch('builtins.open', mocked_folder_file_data)


# pylint: disable=no-member
@static_vars(key=0)
def next_key():
    """provides an increasing key for each call"""
    next_key.key += 1
    return next_key.key


@pytest.fixture
def mocker_affected_folder(mocker):
    """provides an increasing key for each call to AffectedFolder.key"""
    mocker.patch('affected.folders.AffectedFolder.__init__', return_value=None)
    af_mocked = mocker.patch('affected.folders.AffectedFolder.key', new_callable=PropertyMock)
    af_mocked.side_effect = next_key
    return af_mocked

# endregion global mocks


# region tests

def test_affected_folder_class():
    """test AffectedFolder construction and properties"""
    assert [(af.key, af.path) for af in
            [AffectedFolder(line) for line in [
                '1, 2\n',
                '3, 4, 5\n',
                '6, 7, 8, 9\n'
            ]]]\
           == [('1', '2'),
               ('3', '4, 5'),
               ('6', '7, 8, 9')]


# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
def test_load_folder(mocker_file_read_lines, mocker_affected_folder):
    """test load_folders reads the file only once per-refresh,
     and correctly constructs the folders list"""
    folders1 = load_folders()
    folders2 = load_folders()
    assert folders1 == folders2
    assert list(folders1.keys()) == [1, 2, 3]
    folders3 = load_folders(True)
    assert folders1 != folders3
    assert list(folders3.keys()) == [4, 5, 6]

# endregion tests
