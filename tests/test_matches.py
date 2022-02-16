"""
Tests for matches
"""
import os
import pytest
from mock import call
import my_env.my_env
from matches.matches import load_matches, Matching, Recuperated
# pylint: disable=unused-import
from .helpers import next_key, mocker_keyed_class, DataFile, mocker_data_file


def make_recuperated_target(mocker):
    """Make Recuperated object for testing"""
    mocker.patch.object(my_env.my_env, 'RESCUE_FOLDER', 'Arthur')
    mocker.patch.object(my_env.my_env, 'RESCUE_FOLDER_PREFIX', 'Jackson')
    target = Recuperated(['2', 'Sheds'])
    return target, os.path.join('Arthur', 'Jackson.2', 'Sheds')


def expected_recup_values():
    """gets expected Recuperated class values"""
    expected_recup_one_shed = ('1', os.path.join('Arthur', 'Jackson.1', 'one.shed'))
    expected_recup_two_shed = ('2', os.path.join('Arthur', 'Jackson.2', 'two.shed'))
    return expected_recup_one_shed, expected_recup_two_shed


def test_recuperated_class_init_properties(mocker):
    """test construction of Recuperated class"""
    target, expected_path = make_recuperated_target(mocker)
    assert target.id == '2'
    assert target.path == expected_path


def test_recuperated_class_serialize(mocker):
    """test serialization of Recuperated class"""
    target, _ = make_recuperated_target(mocker)
    assert target.serialize() == '2, Sheds'


def test_recuperated_archive(mocker):
    """test archive method of Recuperated class"""
    mocker.patch.object(my_env.my_env, 'ARCHIVE_FOLDER', 'Mr')
    mocker_exists = mocker.patch('os.path.exists', return_value=True)
    mocker_mkdir = mocker.patch('os.mkdir')
    mocker_move = mocker.patch('shutil.move')
    target, expected_path = make_recuperated_target(mocker)
    target.archive()
    expected_archive = os.path.join('Mr', 'Jackson.2')
    assert mocker_mkdir.call_count == 0
    mocker_move.assert_called_with(expected_path, expected_archive)
    mocker_exists.return_value = False
    target.archive()
    mocker_mkdir.assert_called_with(expected_archive)
    mocker_move.assert_called_with(expected_path, expected_archive)


def test_recuperated_remove(mocker):
    """test remove method of Recuperated class"""
    mocker_exists = mocker.patch('os.path.exists', return_value=False)
    mocker_remove = mocker.patch('os.remove')
    target, expected_path = make_recuperated_target(mocker)
    target.remove()
    assert mocker_remove.call_count == 0
    mocker_exists.return_value = True
    target.remove()
    mocker_remove.assert_called_with(expected_path)


def test_matching_class_init_properties(mocker):
    """test construction of Matching class"""
    mocker.patch.object(my_env.my_env, 'RESCUE_FOLDER', 'Arthur')
    mocker.patch.object(my_env.my_env, 'RESCUE_FOLDER_PREFIX', 'Jackson')
    expected_recup_one_shed, expected_recup_two_shed = expected_recup_values()
    target = Matching('2, shed, 15, 1, one.shed, 2, two.shed\n')
    assert target.key == 'shed.15'
    assert target.affected_count == 1
    assert not target.is_single
    assert not target.is_paired
    assert [(m.id, m.path) for m in target.matches]\
           == [expected_recup_one_shed, expected_recup_two_shed]
    target = Matching('4, shed, 15, 1, one.shed, 2, two.shed\n')
    assert target.key == 'shed.15'
    assert target.affected_count == 2
    assert not target.is_single
    assert target.is_paired
    assert [(m.id, m.path) for m in target.matches]\
           == [expected_recup_one_shed, expected_recup_two_shed]
    target = Matching('6, shed, 15, 1, one.shed, 2, two.shed\n')
    assert target.key == 'shed.15'
    assert target.affected_count == 3
    assert not target.is_single
    assert not target.is_paired
    assert [(m.id, m.path) for m in target.matches]\
           == [expected_recup_one_shed, expected_recup_two_shed]
    target = Matching('2, shed, 15, 2, two.shed\n')
    assert target.key == 'shed.15'
    assert target.affected_count == 2
    assert not target.is_single
    assert not target.is_paired
    assert [(m.id, m.path) for m in target.matches] == [expected_recup_two_shed]
    target = Matching('1, shed, 15, 2, two.shed\n')
    assert target.key == 'shed.15'
    assert target.affected_count == 1
    assert target.is_single
    assert target.is_paired
    assert [(m.id, m.path) for m in target.matches] == [expected_recup_two_shed]


def test_matching_class_append(mocker):
    """test append method of Matching class"""
    mocker.patch.object(my_env.my_env, 'RESCUE_FOLDER', 'Arthur')
    mocker.patch.object(my_env.my_env, 'RESCUE_FOLDER_PREFIX', 'Jackson')
    expected_recup_one_shed, expected_recup_two_shed = expected_recup_values()
    target = Matching('4, shed, 15, 1, one.shed\n')
    to_add = Matching('4, shed, 15, 2, two.shed\n')
    target.append(to_add)
    assert target.is_paired
    assert [(m.id, m.path) for m in target.matches]\
           == [expected_recup_one_shed, expected_recup_two_shed]


def test_matching_serialization():
    """test serialize method of Matching class"""
    assert Matching('2, shed, 15, 1, one.shed, 2, two.shed\n').serialize()\
           == '2, shed, 15, 1, one.shed, 2, two.shed'


# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
@pytest.mark.class_name('matches.matches.Matching')
def test_load_matches(mocker_data_file, mocker_keyed_class):
    """test loading matches from file"""
    next_key.key = 0
    load_matches.matches_by_type = {}
    DataFile.reset_static(['line1', 'line2', 'line3'])
    matches1 = load_matches('')
    assert DataFile.paths == ['matched.csv']
    mocker_keyed_class.assert_has_calls([call('line1\n'), call('line2\n'), call('line3\n')])
    assert mocker_keyed_class.call_count == 3
    matches2 = load_matches('')
    assert mocker_keyed_class.call_count == 3
    assert matches1 == matches2
    assert [m.key for m in matches1] == [1, 2, 3]
    matches3 = load_matches('', True)
    mocker_keyed_class.assert_has_calls([call('line1\n'), call('line2\n'), call('line3\n')])
    assert mocker_keyed_class.call_count == 6
    assert matches1 != matches3
    assert [m.key for m in matches1] == [4, 5, 6]
    DataFile.paths = []
    other_matches = load_matches('other_')
    mocker_keyed_class.assert_has_calls([call('line1\n'), call('line2\n'), call('line3\n')])
    assert DataFile.paths == ['other_matched.csv']
    assert mocker_keyed_class.call_count == 9
    assert matches1 != other_matches
    assert [m.key for m in matches1] == [7, 8, 9]
