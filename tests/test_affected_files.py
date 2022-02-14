"""
Tests for affected.folders
"""
# import pytest
# from mock import call

from affected.folders import AffectedFolder # , load_folders
from affected.files import AffectedFile # , load_files, update_files
# # pylint: disable=unused-import
# from .helpers import mocker_file_read_lines, next_key


# region helpers


def make_folders():
    """make a folder dictionary"""
    return {af.key: af for af in [AffectedFolder(line) for line in ['1, Naughtius', '2, Maximus']]}


def make_lines():
    """make affected-file serialized lines"""
    return [
        '0, 1, jpg, 117340, 1455217797.0, extras_icon.jpg\n',
        '_, 2, txt, 38, 1455212874.0, dune_folder.txt\n'
    ]

# endregion helpers


# region tests


def test_affected_file_class_init_properties():
    """test AffectedFiles construction and properties"""
    folders = make_folders()
    assert [(af.key, af.is_matched, af.size, af.extension) for af in
            [AffectedFile(line, folders) for line in make_lines()]]\
           == [('jpg.117340', True, 117340, 'jpg'),
               ('txt.38', False, 38, 'txt')]


def test_affected_file_class_serialize():
    """test AffectedFiles construction and properties"""
    folders = make_folders()
    lines = make_lines()
    assert [af.serialize() + '\n' for af in
            [AffectedFile(line, folders) for line in lines]]\
           == lines


# TODO: test AffectedFile.apply_match


# TODO: test AffectedFile.apply_match


# TODO: Convert to test_load_files
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# @pytest.mark.file_lines('line1', 'line2', 'line3')
# @pytest.mark.class_name('affected.folders.AffectedFile')
# def test_load_folder(mocker_file_read_lines, mocker_keyed_class):
#     """test load_folders reads the file only once per-refresh,
#      and correctly constructs the folders list"""
#     next_key.key = 0
#     folders1 = load_folders()
#     mocker_keyed_class.assert_has_calls([call('line1\n'), call('line2\n'), call('line3\n')])
#     assert mocker_keyed_class.call_count == 3
#     folders2 = load_folders()
#     assert mocker_keyed_class.call_count == 3
#     assert folders1 == folders2
#     assert list(folders1.keys()) == [1, 2, 3]
#     folders3 = load_folders(True)
#     mocker_keyed_class.assert_has_calls([call('line1\n'), call('line2\n'), call('line3\n')])
#     assert mocker_keyed_class.call_count == 6
#     assert folders1 != folders3
#     assert list(folders3.keys()) == [4, 5, 6]

# endregion tests
