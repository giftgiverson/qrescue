"""
Tests for CR2 file handling
"""
import os
import pytest

import recovery.cr2
import matches
import affected


@pytest.fixture()
def matching_testbed(mocker):
    """generate matching for tests"""
    mocker.patch('my_env.rescue_folder', side_effect=lambda x: x+'.f')
    return matches.Matching('18, txt, 10, 1, Sir.Edward.Ross.txt, 2, Edward.txt, 3, Ted.txt, 4,'
                            ' Eddie.Baby.txt, 5, sweetie.txt, 6, sugar.plum.txt')


def make_folders():
    """make a folder dictionary"""
    return {af.key: af for af in [affected.folders.AffectedFolder(line)
                                  for line in ['1, 100.0-', '2, 200.0-', '3, 300.0-']]}


def make_lines():
    """make affected-file serialized lines"""
    return [
        '_, 1, txt, 10, 1149803452.0, -111.1-Pussycat.txt\n',
        '_, 2, txt, 10, 1149803454.0, -222.2-Angel_drawers.jpg\n',
        '_, 3, txt, 10, 1149803456.0, -333.3-Frank.txt\n'
    ]


@pytest.fixture()
def affected_testbed(mocker):
    """generate affected for tests"""
    mocker.patch('my_env.nas_to_pc', side_effect=lambda x: x)
    folders = make_folders()
    return [affected.AffectedFile(line, folders) for line in make_lines()]


def test_get_cr2_datetime_string():
    """tests getting date and time from CR2 file"""
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'f3662951424.cr2')
    assert recovery.cr2.get_cr2_datetime_string(path) == '2006:06:09 00:50:52'


def test_get_cr2_timestamp(mocker):
    """tests getting timestamp from CR2 file"""
    mocker.patch('recovery.cr2.get_cr2_datetime_string', return_value='2006:06:09 00:50:52')
    assert recovery.cr2.get_cr2_timestamp('Sir.Edward.Ross.txt') == 1149803452.0


# pylint: disable=redefined-outer-name
def test_match_index_and_cr2_timestamp(mocker, matching_testbed):
    """tests getting CR2 timestamps for all matches in a Matching record"""
    mocker.patch('recovery.cr2.get_cr2_datetime_string',
                 side_effect=lambda x: '2006:06:09 00:50:5' + x.split('.')[0])
    assert recovery.cr2.match_index_and_cr2_timestamp(matching_testbed) ==\
           [(0, 1149803451.0), (1, 1149803452.0), (2, 1149803453.0), (3, 1149803454.0),
            (4, 1149803455.0), (5, 1149803456.0)]


def test_affected_index_and_cr2_limits(mocker, affected_testbed):
    """test getting CR2 timestamps for all AffectedFile objects in list"""
    mocker.patch('my_env.neighbor_modified_limits',
                 side_effect=lambda x: list(range(0, int(x.split('0')[0]) % 3)))
    mocker.patch('recovery.cr2.get_cr2_timestamp', side_effect=lambda x: x)
    assert recovery.cr2.affected_index_and_cr2_limits(affected_testbed) == [(1, [0, 1])]
