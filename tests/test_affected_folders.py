"""
Tests for affected.folders
"""
import pytest
from mock import PropertyMock, call

from affected.folders import AffectedFolder, load_folders
from my_misc import static_vars
# pylint: disable=unused-import
from .helpers import mocker_file_read_lines


# region mocks

# pylint: disable=no-member
@static_vars(key=0)
def next_key():
    """provides an increasing key for each call"""
    next_key.key += 1
    return next_key.key


@pytest.fixture
def mocker_affected_folder(mocker):
    """provides an increasing key for each call to AffectedFolder.key"""
    af_init_mocked = mocker.patch('affected.folders.AffectedFolder.__init__', return_value=None)
    af_mocked = mocker.patch('affected.folders.AffectedFolder.key', new_callable=PropertyMock)
    af_mocked.side_effect = next_key
    return af_init_mocked


# endregion mocks


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
@pytest.mark.file_lines('line1', 'line2', 'line3')
def test_load_folder(mocker_file_read_lines, mocker_affected_folder):
    """test load_folders reads the file only once per-refresh,
     and correctly constructs the folders list"""
    folders1 = load_folders()
    mocker_affected_folder.assert_has_calls([call('line1\n'), call('line2\n'), call('line3\n')])
    assert mocker_affected_folder.call_count == 3
    folders2 = load_folders()
    assert mocker_affected_folder.call_count == 3
    assert folders1 == folders2
    assert list(folders1.keys()) == [1, 2, 3]
    folders3 = load_folders(True)
    mocker_affected_folder.assert_has_calls([call('line1\n'), call('line2\n'), call('line3\n')])
    assert mocker_affected_folder.call_count == 6
    assert folders1 != folders3
    assert list(folders3.keys()) == [4, 5, 6]

# endregion tests
