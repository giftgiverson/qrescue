"""
Tests for affected.folders
"""
import pytest
from mock import call
import affected.folders
from affected.files import AffectedFile, load_files, update_files
import my_env.my_env
# pylint: disable=unused-import
from .helpers import mocker_file_read_lines, next_key, mocker_keyed_class


# region helpers


def make_folders():
    """make a folder dictionary"""
    return {af.key: af for af in [affected.folders.AffectedFolder(line)
                                  for line in ['1, Naughtius', '2, Maximus']]}


def make_lines():
    """make affected-file serialized lines"""
    return [
        '0, 1, jpg, 117340, 1455217797.0, extras_icon.jpg\n',
        '_, 2, txt, 38, 1455212874.0, dune_folder.txt\n'
    ]


# pylint: disable=too-few-public-methods
class Serializable:
    """use for mocking serialization"""
    def __init__(self, value):
        """
        Init mock
        :param value: serialized value
        """
        self.value = value

    def serialize(self):
        """return serialized value"""
        return self.value


class DataFile:
    """data file mock"""
    written = []

    def __init__(self, path, mode='r'):
        self.path = path
        self.mode = mode

    def __enter__(self):
        return ['line\n'] if self.mode == 'r' else self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def write(value):
        """saves written values to static array"""
        DataFile.written.append(value)


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


def test_affected_files_class_apply_match(mocker):
    """test AffectedFile.apply_match correctly replaces files when and where needed,
     as well as marking the file as matched"""
    mocker.patch('my_env.nas_to_pc', side_effect=lambda x: x)
    for does_7z_exist in [True, False]:
        mocker.patch('os.path.exists', return_value=does_7z_exist)
        mocker_shutil_copy = mocker.patch('shutil.copy')
        mocker_os_time = mocker.patch('os.utime')
        mocker_os_remove = mocker.patch('os.remove')
        target = AffectedFile(make_lines()[1], make_folders())
        assert not target.is_matched
        target.apply_match('joke.name.txt', 3)
        assert mocker_shutil_copy.call_count == 1
        assert mocker_shutil_copy.call_args_list[0][0][0] == 'joke.name.txt'
        assert mocker_shutil_copy.call_args_list[0][0][1].replace('\\', '/')\
               == 'Maximus/dune_folder.txt'
        assert mocker_os_time.call_count == 1
        assert mocker_os_time.call_args_list[0][0][0].replace('\\', '/')\
               == 'Maximus/dune_folder.txt'
        assert mocker_os_time.call_args_list[0][0][1] == (1455212874.0, 1455212874.0)
        if does_7z_exist:
            assert mocker_os_remove.call_count == 1
            assert mocker_os_remove.call_args_list[0][0][0].replace('\\', '/')\
                   == 'Maximus/dune_folder.txt.7z'
        else:
            assert mocker_os_remove.call_count == 0
        assert target.is_matched


# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=no-member
@pytest.mark.file_lines('line1', 'line2', 'line3')
@pytest.mark.class_name('affected.files.AffectedFile')
def test_load_files(mocker, mocker_file_read_lines, mocker_keyed_class):
    """test load_files reads the file only once per-refresh,
     and correctly constructs the files list"""
    mocker.patch.object(my_env.my_env, 'DATA_FOLDER', 'shrubbery')
    mocker.patch('affected.folders.load_folders', return_value='biggus')
    next_key.key = 0
    affected.files.load_files.files = []
    files1 = load_files()
    assert mocker_file_read_lines.call_count == 1
    assert mocker_file_read_lines.call_args_list[0][0][0].replace('\\', '/') \
           == 'shrubbery/affected_files.csv'
    mocker_keyed_class.assert_has_calls([call('line1\n', 'biggus'), call('line2\n', 'biggus'),
                                         call('line3\n', 'biggus')])
    assert mocker_keyed_class.call_count == 3
    files2 = load_files()
    assert mocker_keyed_class.call_count == 3
    assert files1 == files2
    assert list(file.key for file in files1) == [1, 2, 3]
    files3 = load_files(True)
    mocker_keyed_class.assert_has_calls([call('line1\n', 'biggus'), call('line2\n', 'biggus'),
                                         call('line3\n', 'biggus')])
    assert mocker_keyed_class.call_count == 6
    assert files1 != files3
    assert list(file.key for file in files3) == [4, 5, 6]


@pytest.mark.class_name('affected.files.AffectedFile')
def test_update_files(mocker, mocker_keyed_class):
    """test update_files for correct writing of files and reset of load_files cache"""
    mocker.patch('affected.folders.load_folders', return_value='biggus')
    mocker_data_file = mocker.patch('my_env.data_file', side_effect=DataFile)
    load_files.files = ['something']
    load_files()
    assert mocker_data_file.call_count == 0
    mocker_backup = mocker.patch('my_env.data_backup')
    file_mocks = [Serializable(line) for line in ['lineA', 'lineB', 'lineC']]
    DataFile.written = []
    update_files(file_mocks)
    mocker_backup.assert_called_with('affected_files.csv')
    assert mocker_data_file.call_count == 1
    assert DataFile.written == ['lineA\n', 'lineB\n', 'lineC\n']
    load_files()
    assert mocker_data_file.call_count == 2


# endregion tests
