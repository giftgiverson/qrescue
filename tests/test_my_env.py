"""
Tests for my_env
"""
from time import sleep
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


def test_data_backup(mocker):
    """tests date-backup renames files correctly"""
    set_constants(mocker)
    mocker.patch('os.rename', side_effect=rename)
    old_name = ''
    for i in range(2, 4):
        name = my_env.my_env.data_backup('location.pos', '_not_found')
        assert name.startswith('location_not_found')
        assert name.endswith('.pos')
        assert name != old_name
        if not old_name:
            sleep(i)
        old_name = name


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

# endregion tests
