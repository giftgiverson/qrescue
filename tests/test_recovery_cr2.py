"""
Tests for CR2 file handling
"""
import os
import pytest
from mock import call

import recovery.cr2
import matches
import affected
# pylint: disable=unused-import
from .helpers import DataFile, mocker_data_file


@pytest.fixture()
def matching_testbed(mocker):
    """generate matching for tests"""
    mocker.patch('my_env.rescue_folder', side_effect=lambda x: x+'.f')
    return matches.Matching('18, txt, 10, 1, Sir.Edward.Ross.txt, 2, Edward.txt, 3, Ted.txt, 4,'
                            ' Eddie.Baby.txt, 5, sweetie.txt, 6, sugar.plum.txt')


def make_folders():
    """make a folder dictionary"""
    return {af.key: af for af in [affected.folders.AffectedFolder(line)
                                  for line in ['1, 100.0', '2, 200.0', '3, 300.0']]}


def make_lines():
    """make affected-file serialized lines"""
    return [
        '_, 1, txt, 10, 1149803452.0, -2-Pussycat.txt\n',
        '_, 2, txt, 10, 1149803454.0, -0-Angel_drawers.jpg\n',
        '_, 3, txt, 10, 1149803456.0, -2-Frank.txt\n',
        '_, 2, txt, 10, 1149803458.0, -2-Fran.txt\n'
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
    assert recovery.cr2.affected_index_and_cr2_limits(affected_testbed) ==\
           [(1, [0, 1]), (3, [0, 1])]


def test_affected_index_and_folder_limits(mocker, affected_testbed):
    """tests getting folder timestamps for AffectedFile objects in list not already timestamped"""
    neighborhood = [(0, [0, 1])]
    mocker.patch('my_env.parent_and_previous_folder',
                 side_effect=lambda x: list(i + int(x.split('-')[1])
                                            for i in range(0, int(x.split('0')[0]) % 3)))
    mocker.patch('my_env.timestamps_from_names', side_effect=lambda x: list(range(0, x[0])))
    assert recovery.cr2.affected_index_and_folder_limits(affected_testbed, neighborhood) ==\
           [(3, [0, 1])]


def test_handle_couples():
    """test coupling between date ranges and affects file's timestamps"""
    matched = [(0, 0), (1, 111.1), (2, 222.2), (3, 333.3)]
    neighborhood = [(0, [111.1, 111.2]), (1, [222.1, 222.2]), (2, [333.2, 333.4])]
    affected_matched = {i: [] for i in range(0, 3)}
    match_affected = {i: 0 for i in range(0, 4)}
    recovery.cr2.handle_couples(matched, neighborhood, affected_matched, match_affected)
    assert affected_matched == {0: [1], 1: [2], 2: [3]}
    assert match_affected == {0: 0, 1: 1, 2: 1, 3: 1}


def test_serialize_unhandled(matching_testbed, affected_testbed):
    """test serialization of unmatched items for future manual handling"""
    matching = [(match, i, i % 3) for i, match in enumerate(matching_testbed.matches)]
    assert recovery.cr2.serialize_unhandled('key', affected_testbed, matching) ==\
           'key, ' \
           '4,' \
           ' _, 1, -2-Pussycat.txt,' \
           ' _, 2, -0-Angel_drawers.jpg,' \
           ' _, 3, -2-Frank.txt,' \
           ' _, 2, -2-Fran.txt, ' \
           '6,' \
           ' 1, Sir.Edward.Ross.txt, 0, 0,' \
           ' 2, Edward.txt, 1, 1,' \
           ' 3, Ted.txt, 2, 2,' \
           ' 4, Eddie.Baby.txt, 3, 0,' \
           ' 5, sweetie.txt, 4, 1,' \
           ' 6, sugar.plum.txt, 5, 2\n'


def test_cr2autohandler_class_can_handle():
    """test handler's class classification of handle-able matches"""
    can_handle = matches.Matching('18, cr2, 10, 1, Sir.Edward.Ross.txt')
    cannot_handle = matches.Matching('18, txt, 10, 1, Sir.Edward.Ross.txt')
    assert recovery.cr2.Cr2AutoHandler.can_handle(can_handle)
    assert not recovery.cr2.Cr2AutoHandler.can_handle(cannot_handle)


class Cr2AutoHandlerTestbed(recovery.cr2.Cr2AutoHandler):
    """Cr2AutoHandler class testbed"""
    def call_handle_unmatched(self, match_affected, matching):
        """call protected method"""
        self._handle_unmatched(match_affected, matching, None)

    def call_handle_removable(self, match_affected, matching):
        """call protected method"""
        self._handle_removable(match_affected, matching)

    def call_process_matching(self, affected_list, affected_match, match_affected):
        """call protected method"""
        return list(self._process_matching(None, affected_list, affected_match, match_affected))


# pylint: disable=unused-argument
def test_cr2autohandler_class_handle_unmatched(mocker, matching_testbed, mocker_data_file):
    """test summary of unmatched files"""
    DataFile.reset_static()
    mocker.patch('recovery.cr2.serialize_unhandled',
                 side_effect=lambda mkey, _, ming: f'{mkey}|{ming}')
    with Cr2AutoHandlerTestbed() as target:
        target.call_handle_unmatched({0: -1, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4}, matching_testbed)
    assert DataFile.written['manual_match'] ==\
           ['txt.10|['
            '(6, sugar.plum.txt, 5, 4), '
            '(5, sweetie.txt, 4, 3), '
            '(4, Eddie.Baby.txt, 3, 2), '
            '(3, Ted.txt, 2, 1), '
            '(2, Edward.txt, 1, 0), '
            '(1, Sir.Edward.Ross.txt, 0, -1)]']


# pylint: disable=unused-argument
def test_cr2autohandler_class_handle_removable(matching_testbed, mocker_data_file):
    """test report of removable non-matching candidates"""
    DataFile.reset_static()
    with Cr2AutoHandlerTestbed() as target:
        target.call_handle_removable({0: -1, 1: 0, 2: -1, 3: 2, 4: 3, 5: 4}, matching_testbed)
    assert DataFile.written['unmatched'] ==\
           ['12, txt, 10, 2, Edward.txt, 3, Ted.txt, 5, sweetie.txt, 6, sugar.plum.txt\n']


def test_cr2autohadle_class_process_matching(mocker, affected_testbed):
    """test processing of mathing after files are couple-tested by CR2/Folder dates"""
    handle_unmatched = mocker.patch('recovery.cr2.Cr2AutoHandler._handle_unmatched')
    handle_removable = mocker.patch('recovery.cr2.Cr2AutoHandler._handle_removable')
    target = Cr2AutoHandlerTestbed()
    assert str(target.call_process_matching(affected_testbed,
                                            {0: [1], 1: [3]}, {0: 0, 1: 1, 2: 0, 3: 1}))\
        .replace('\\', '/') ==\
           '[(100.0/-2-Pussycat.txt [10], 1, True), (200.0/-0-Angel_drawers.jpg [10], 3, True)]'
    assert handle_removable.called_with(call({0: 0, 1: -1, 2: 0, 3: -1}, None))
    assert handle_unmatched.call_count == 0
    assert not target.call_process_matching(affected_testbed,
                                            {0: [1, 3], 1: []}, {0: 0, 1: 1, 2: 0, 3: 1})
    assert handle_removable.call_count == 1
    assert str(handle_unmatched.call_args).replace('\\', '/') ==\
           'call({0: 0, 1: 1, 2: 0, 3: 1}, None,' \
           ' [100.0/-2-Pussycat.txt [10], 200.0/-0-Angel_drawers.jpg [10]])'


def test_cr2autohandler_handle(mocker, affected_testbed, matching_testbed):
    """tests the main flow of handling CR2 matching affected files"""
    match_index_and_cr2_timestamp = mocker.patch('recovery.cr2.match_index_and_cr2_timestamp',
                                                 return_value='Frannie')
    affected_index_and_cr2_limits = mocker.patch('recovery.cr2.affected_index_and_cr2_limits',
                                                 return_value=[(1, [0, 1]), (3, [2, 3])])
    affected_index_and_folder_limits = mocker.patch('recovery.cr2.affected_index_and_folder_limits',
                                                    return_value=[(2, [1, 2])])
    handle_couples = mocker.patch('recovery.cr2.handle_couples')
    process_matching = mocker.patch('recovery.cr2.Cr2AutoHandler._process_matching',
                                    return_value=['little', 'Frannie', 'pooh'])
    target = recovery.cr2.Cr2AutoHandler()
    assert target.handle(matching_testbed, affected_testbed) == ['little', 'Frannie', 'pooh']
    assert match_index_and_cr2_timestamp.call_args == call(matching_testbed)
    assert affected_index_and_cr2_limits.call_args == call(affected_testbed)
    assert affected_index_and_folder_limits.call_args == call(affected_testbed,
                                                              [(1, [0, 1]), (3, [2, 3])])
    assert handle_couples.call_args ==\
           call('Frannie',
                [(1, [0, 1]), (3, [2, 3]), (2, [1, 2])],
                {0: [], 1: [], 2: [], 3: []},
                {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
    assert process_matching.call_args ==\
           call(matching_testbed, affected_testbed,
                {0: [], 1: [], 2: [], 3: []},
                {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
