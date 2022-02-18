"""
Tests for recovery.recovery
"""
import pytest
import affected
import recovery
import my_env
# pylint: disable=unused-import
from .helpers import DataFile, mocker_data_file

NO_MATCH = "no match"


def make_folders():
    """make a folder dictionary"""
    return {af.key: af for af in [affected.folders.AffectedFolder(line)
                                  for line in ['1, Norwegian', '2, Blue']]}


def make_files():
    """make a file list"""
    folders = make_folders()
    return [AffectedFilesTestbed(line, folders)
            for line in
            [
                '_, 1, jpg, 10, 13.0, passed_on.jpg\n',
                '_, 1, jpg, 11, 14.0, no_more.jpg\n',
                '_, 2, jpg, 10, 15.0, ceased_to_be.jpg\n',
                '_, 2, jpg, 12, 16.0, expired.jpg\n',
                '0, 2, jpg, 13, 17.0, gone_to_meet_its_maker.jpg\n',
            ]]


# pylint: disable=too-few-public-methods
class AffectedFilesTestbed(affected.files.AffectedFile):
    """AffectedFiles class testbed"""
    calls = []

    def apply_match(self, recovered_path, submatch):
        """mock apply match"""
        AffectedFilesTestbed.calls.append((recovered_path, submatch))
        self._status = str(submatch)


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
        assert [f.key for f in self._get_affected(match)] == expected

    def assert_make_path(self, match, submatch, expected):
        """
        Assert path construction
        :param match: match input
        :param submatch: submatch selection
        :param expected: expected output
        """
        path = self._make_path('dead parrot', match, submatch)
        assert expected == path if path else NO_MATCH

    def assert_recover(self, match, expected):
        """
        Assert recovery
        :param match: match input
        :param expected: expected output
        """
        DataFile.reset_static()
        calls_before = len(AffectedFilesTestbed.calls)
        with my_env.data_file('VOOM', 'w') as recovery_log:
            path = self._recover(self._keyed_files['jpg.11'][0], match, 0, recovery_log)
            assert expected == path if path else NO_MATCH
            assert 'VOOM' in DataFile.written
            assert DataFile.written['VOOM'] == ['0, 1, jpg, 11, 14.0, no_more.jpg\n']
            calls_now = len(AffectedFilesTestbed.calls)
            if path:
                assert (calls_before + 1) == calls_now
                assert AffectedFilesTestbed.calls[-1] == ("'E's off the twig", 0)
            else:
                assert calls_before == calls_now


@pytest.fixture
def recovery_testbed(mocker):
    """makes the recovery class testbed, overriding load_files to use test values"""
    mocker.patch('affected.load_files', side_effect=make_files)
    return RecoveryTestbed()


class SubmatchTestbed:
    """keyed class"""
    @property
    def path(self):
        """
        :return: key
        """
        return self._path

    def __init__(self, path):
        self._path = path


class MatchTestbed:
    """keyed class"""
    @property
    def key(self):
        """
        :return: key
        """
        return self._key

    @property
    def matches(self):
        """
        :return: matches
        """
        return self._matches

    #pylint: disable=protected-access
    def __init__(self, key, paths=None):
        self._key = key
        self._matches = [SubmatchTestbed(path) for path in paths] if paths else []


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


# pylint: disable=redefined-outer-name
def test_recover_class_get_affected(recovery_testbed):
    """tests match detection"""
    recovery_testbed.assert_get_affected(MatchTestbed('jpg.10'), ['jpg.10', 'jpg.10'])
    recovery_testbed.assert_get_affected(MatchTestbed('jpg.11'), ['jpg.11'])
    recovery_testbed.assert_get_affected(MatchTestbed('jpg.12'), ['jpg.12'])
    recovery_testbed.assert_get_affected(MatchTestbed('jpg.13'), ['jpg.13'])


# pylint: disable=redefined-outer-name
def test_make_path(mocker, recovery_testbed):
    """tests recovery path acquisition"""
    mocker.patch('os.path.exists', return_value=True)
    recovery_testbed.assert_make_path(
        MatchTestbed('jpg.10', ["'E's a stiff", 'bereft of life']), 1, 'bereft of life')
    mocker.patch('os.path.exists', return_value=False)
    recovery_testbed.assert_make_path(
        MatchTestbed('jpg.11', ['pushing up the daisies']), 0, NO_MATCH)


# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
def test_recover(mocker, mocker_data_file, recovery_testbed):
    """tests recovery"""
    mocked_path = mocker.patch('recovery.recovery.Recovery._make_path',
                               return_value="'E's off the twig")
    recovery_testbed.assert_recover(MatchTestbed('jpg.11'), "'E's off the twig")
    mocked_path.return_value = None
    recovery_testbed.assert_recover(MatchTestbed('jpg.11'), NO_MATCH)
