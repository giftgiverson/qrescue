"""
Tests for affected.folders
"""
import pytest
from mock import call

from affected.folders import AffectedFolder, load_folders
# pylint: disable=unused-import
from .helpers import next_key, mocker_keyed_class, DataFile, mocker_data_file


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
@pytest.mark.class_name('affected.folders.AffectedFolder')
def test_load_folder(mocker, mocker_data_file, mocker_keyed_class):
    """test load_folders reads the file only once per-refresh,
     and correctly constructs the folders list"""
    next_key.key = 0
    load_folders.folder = []
    DataFile.reset_static(['line1', 'line2', 'line3'])
    folders1 = load_folders()
    assert DataFile.paths == ['affected_folders.csv']
    mocker_keyed_class.assert_has_calls([call('line1\n'), call('line2\n'), call('line3\n')])
    assert mocker_keyed_class.call_count == 3
    folders2 = load_folders()
    assert mocker_keyed_class.call_count == 3
    assert folders1 == folders2
    assert list(folders1.keys()) == [1, 2, 3]
    folders3 = load_folders(True)
    mocker_keyed_class.assert_has_calls([call('line1\n'), call('line2\n'), call('line3\n')])
    assert mocker_keyed_class.call_count == 6
    assert folders1 != folders3
    assert list(folders3.keys()) == [4, 5, 6]

# endregion tests
