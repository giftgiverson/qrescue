"""
Tests for my_env
"""
from time import sleep
from os.path import join as pjoin
from stat import ST_MTIME
import my_env.my_env


# region mocks

def set_constants(mocker):
    """Set test values to module constants"""
    mocker.patch.object(my_env.my_env, 'RESCUE_FOLDER', 'the/knights/who/say')
    mocker.patch.object(my_env.my_env, 'RESCUE_FOLDER_PREFIX', 'ni')
    mocker.patch.object(my_env.my_env, 'DATA_FOLDER', 'shrubbery')
    mocker.patch.object(my_env.my_env, 'ARCHIVE_FOLDER', 'sacrifice')


def listdir(path):
    """listdir() mock, asserting rescue path and providing a list of rescue folders"""
    assert path == 'the/knights/who/say'
    now_say = 'Ekki-Ekki-Ekki-Ekki-PTANG'
    return [f'{path}/ni.{n}' for n in range(1, 10)] + [f'{path}/{now_say}.11']


def rename(source, destination):
    """rename() mock, asserting paths are in data folder and are different"""
    assert all(p.startswith('shrubbery') for p in [source, destination])
    assert source != destination

# endregion mocks


# region tests

def test_rescue_folder(mocker):
    """test rescue folder-path construction"""
    set_constants(mocker)
    assert my_env.my_env.rescue_folder('42').replace('\\', '/') == 'the/knights/who/say/ni.42'


def test_last_rescue_folder(mocker):
    """test detection of highest-number rescue folder"""
    set_constants(mocker)
    mocker.patch('os.listdir', side_effect=listdir)
    assert my_env.my_env.last_rescue_folder() == 9


def test_rescued_file(mocker):
    """test rescue file-path construction"""
    set_constants(mocker)
    assert my_env.my_env.rescued_file('1', 'to_you.wav').replace('\\', '/')\
           == 'the/knights/who/say/ni.1/to_you.wav'


def test_data_file(mocker):
    """test data_file open"""
    set_constants(mocker)
    mocked_open = mocker.mock_open()
    mocker.patch('builtins.open', mocked_open)
    with my_env.my_env.data_file('Arthur.txt'):
        pass
    path = pjoin('shrubbery', 'Arthur.txt')
    mocked_open.assert_called_with(path, 'r', encoding='utf8')
    with my_env.my_env.data_file('Arthur.txt', 'w'):
        pass
    mocked_open.assert_called_with(path, 'w', encoding='utf8')
    with my_env.my_env.data_file('Arthur.txt', 'a'):
        pass
    mocked_open.assert_called_with(path, 'a', encoding='utf8')


def test_data_backup(mocker):
    """tests date-backup renames files correctly"""
    set_constants(mocker)
    mocked_exists = mocker.patch('os.path.exists', return_value=True)
    mocked_rename = mocker.patch('os.rename', side_effect=rename)
    old_name = ''
    for i in range(2, 4):
        name = my_env.my_env.data_backup('location.pos', '_not_found')
        assert name.startswith('location_not_found')
        assert name.endswith('.pos')
        assert name != old_name
        if not old_name:
            sleep(i)
        old_name = name
    prev_calls = mocked_rename.call_count
    mocked_exists.return_value = False
    assert not my_env.my_env.data_backup('some', 'thing')
    assert mocked_rename.call_count == prev_calls


def test_nas_to_pc(mocker):
    """test path translation from NAS to PC"""
    mocker.patch.object(my_env.my_env, 'NAS_TO_PC', {'Ni': 'Oh, ow!', 'Pen': 'Ni-wom'})
    f_name = '/to_you.wav'
    assert [my_env.my_env.nas_to_pc(test + f_name) for test in ['Ni', 'No', 'Pen', 'PTANG']]\
           == [expected + f_name for expected in ['Oh, ow!', 'No', 'Ni-wom', 'PTANG']]


def test_archive_folder(mocker):
    """test archive-folder path construction"""
    set_constants(mocker)
    assert my_env.my_env.archive_folder('2').replace('\\', '/') == 'sacrifice/ni.2'


def test_neighbor_modified_limits(mocker):
    """test locating limits of files' modified-time next to a target"""
    mocked_globe = mocker.patch('glob.glob', return_value=[1.0, 2.0, 3.0])
    mocker.patch('os.stat', side_effect=lambda x: {ST_MTIME: x})
    assert my_env.my_env.neighbor_modified_limits('sacrifice/Ni.wom') == [1.0, 3.0]
    mocked_globe.assert_called_with(pjoin('sacrifice', '*.wom'))
    mocked_globe.return_value = [4.0]
    assert my_env.my_env.neighbor_modified_limits('sacrifice/Ni.wom') == [4.0]
    mocked_globe.return_value = []
    assert not my_env.my_env.neighbor_modified_limits('sacrifice/Ni.wom')


def test_parent_and_previous_folder(mocker):
    """test locating parent and previous folder in parent's folder"""
    mocked_listdir = mocker.patch('os.listdir', return_value=['Pen', 'Ni', 'PTANG', 'Zzzz'])
    assert my_env.my_env.parent_and_previous_folder('sacrifice/PTANG/Ni.wom') == ('PTANG', 'Pen')
    mocked_listdir.assert_called_with('sacrifice')
    mocked_listdir.return_value = ['Zzzz', 'PTANG']
    assert my_env.my_env.parent_and_previous_folder('sacrifice/PTANG/Ni.wom') == ('PTANG')


def test_timestamp_from_name():
    """test parsing of name into timestamp"""
    assert my_env.my_env.timestamp_from_name('2022_02_19') == 1645308000.0
    assert my_env.my_env.timestamp_from_name('not-a-date') == -1.0


def test_timestamp_from_names():
    """test parsing of names into timestamp-range"""
    assert my_env.my_env.timestamps_from_names(['2022_02_19', '2022_02_10']) ==\
           [1644530400.0, 1645308000.0]
    assert my_env.my_env.timestamps_from_names(['2022_02_19']) == [1640988000.0, 1645308000.0]
    assert my_env.my_env.timestamps_from_names(['2022_02_19', 'not-a-date']) ==\
           [1640988000.0, 1645308000.0]
    assert not my_env.my_env.timestamps_from_names(['not-a-date', 'not-a-date-either'])

# endregion tests
