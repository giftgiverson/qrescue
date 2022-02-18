"""
Tests for recovery.recovery
"""
import pytest
import affected
import recovery

NO_MATCH = "no match"


def make_folders():
    """make a folder dictionary"""
    return {af.key: af for af in [affected.folders.AffectedFolder(line)
                                  for line in ['1, Norwegian', '2, Blue']]}


def make_files():
    """make a file list"""
    folders = make_folders()
    return [affected.files.AffectedFile(line, folders)
            for line in
            [
                '_, 1, jpg, 10, 13.0, passed_on.jpg\n',
                '_, 1, jpg, 11, 14.0, no_more.jpg\n',
                '_, 2, jpg, 10, 15.0, ceased_to_be.jpg\n',
                '_, 2, jpg, 12, 16.0, expired.jpg\n',
                '0, 2, jpg, 13, 17.0, gone_to_meet_its_maker.jpg\n',
            ]]


# pylint: disable=too-few-public-methods
class RecoveryTestbed(recovery.recovery.Recovery):
    """Recovery class testbed"""

    @property
    def keyed_files(self):
        """
        :return: calculated files dictionary
        """
        return self._keyed_files

    def assert_get_single_un_recovered(self, key, expected):
        """
        Assert expected single detection
        :param key: files key
        :param expected: expected output key
        """
        actual = self._get_single_un_recovered(self._keyed_files[key])
        assert expected == (actual.key if actual else NO_MATCH)

    def assert_get_affected(self, match, expected):
        """
        Assert expected match detection
        :param match: match input
        :param expected: expected output
        """
        assert self._get_affected(match) == expected


@pytest.fixture
def recovery_testbed(mocker):
    """makes the recovery class testbed, overriding load_files to use test values"""
    mocker.patch('affected.load_files', side_effect=make_files)
    return RecoveryTestbed()


class Keyed:
    """keyed class"""
    @property
    def key(self):
        """
        :return: key
        """
        return self._key

    def __init__(self, key):
        self._key = key


# pylint: disable=redefined-outer-name
def test_recovery_class_keyed_files(recovery_testbed):
    """test correct keying of files in recovery class"""
    assert [[key] + [file.key for file in files]
            for key, files in recovery_testbed.keyed_files.items()] \
           == [['jpg.10', 'jpg.10', 'jpg.10'], ['jpg.11', 'jpg.11'], ['jpg.12', 'jpg.12'],
               ['jpg.13', 'jpg.13']]


# pylint: disable=redefined-outer-name
def test_recovery_class_single_detection(recovery_testbed):
    """test single detection"""
    # more than one match
    recovery_testbed.assert_get_single_un_recovered('jpg.10', NO_MATCH)
    # one previously unmatched
    recovery_testbed.assert_get_single_un_recovered('jpg.11', 'jpg.11')
    recovery_testbed.assert_get_single_un_recovered('jpg.12', 'jpg.12')
    # one previously matched
    recovery_testbed.assert_get_single_un_recovered('jpg.13', NO_MATCH)
