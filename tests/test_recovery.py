"""
Tests for recovery.recovery
"""
import pytest
import affected
import recovery
import my_env
# pylint: disable=unused-import
from .helpers import DataFile, mocker_data_file, static_vars

NO_MATCH = "no match"


# region mocks

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

    # pylint: disable=invalid-name
    @property
    def id(self):
        """
        :return: id
        """
        return self._id

    @property
    def path(self):
        """
        :return: key
        """
        return self._path

    @property
    def is_archived(self):
        """
        :return: was the archive method called
        """
        return self._is_archived

    def __init__(self, path, submatch_id):
        self._path = path
        self._id = str(submatch_id)
        self._is_archived = False

    def archive(self):
        """mock archive method"""
        self._is_archived = True

    def __repr__(self):
        """class representation"""
        return str([self._id, self._path, self._is_archived])


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

    # pylint: disable=protected-access
    def __init__(self, key, paths=None):
        self._key = key
        self._matches = [SubmatchTestbed(path, 1 + i % 2) for i, path in
                         enumerate(paths)] if paths else []

    def __repr__(self):
        """class representation"""
        return str([self._key, self._matches])


@static_vars(matches=[])
def make_matches(file, is_reload):
    """make matches for testing"""
    print(f'make_matches({file}, {is_reload})')
    make_matches.matches = \
        [MatchTestbed(key, value) for key, value in {
            'jpg.10': ["'E's kicked the bucket", "e's shuffled off 'is mortal coil"],
            'jpg.11': ['run down the curtain'],
            'jpg.12': ["joined the bleedin' choir invisible"],
            'jpg.13': ['EX-PARROT']
        }.items()]
    return make_matches.matches


@pytest.fixture
def match_testbed(mocker):
    """overrides load_files to use test values"""
    mocker.patch('matches.load_matches', side_effect=make_matches)


class MockSingleHandler:
    """handle single matches recovery"""

    @staticmethod
    def can_handle(match):
        """mock can handle"""
        return match.key != 'jpg.12'

    @staticmethod
    def handle(match, affected_list):
        """mock handle"""
        return [(affected_list, 0)] if match.key != 'jpg.10' else []

    @staticmethod
    def get_type():
        """handler type"""
        return 'Mock-Single'

# endregion mocks


# region tests

# pylint: disable=redefined-outer-name
def test_recovery_class_keyed_files(recovery_testbed):
    """test correct keying of files in recovery class"""
    assert [[key] + [file.key for file in files]
            for key, files in recovery_testbed.keyed_files.items()] \
           == [['jpg.10', 'jpg.10', 'jpg.10'], ['jpg.11', 'jpg.11'], ['jpg.12', 'jpg.12'],
               ['jpg.13', 'jpg.13']]


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


# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
def test_recover_single_matches(mocker, mocker_data_file, recovery_testbed, match_testbed):
    """test single recovery"""
    mocker.patch('recovery.recovery.Recovery._get_affected', side_effect=lambda x: x)
    mocker.patch('recovery.recovery.Recovery._recover',
                 side_effect=lambda *args: args[1].key != 'jpg.13')
    mocker_update = mocker.patch('affected.update_files')
    recovery_testbed.recover_single_matched(MockSingleHandler())
    assert str(make_matches.matches) == \
           str([['jpg.10', [['1', "'E's kicked the bucket", False],
                            ['2', "e's shuffled off 'is mortal coil", False]]],
                ['jpg.11', [['1', 'run down the curtain', True]]],
                ['jpg.12', [['1', "joined the bleedin' choir invisible", False]]],
                ['jpg.13', [['1', 'EX-PARROT', False]]]])
    assert str(mocker_update.call_args).replace('\\', '/') == \
           'call([[Norwegian/passed_on.jpg [10], [Norwegian/no_more.jpg [11],' \
           ' [Blue/ceased_to_be.jpg [10], [Blue/expired.jpg [12],' \
           ' [Blue/gone_to_meet_its_maker.jpg [13]])'

# endregion tests
