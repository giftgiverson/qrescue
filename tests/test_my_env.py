"""
Tests for my_env
"""
# pylint: disable=not-callable
# pylint: disable=unused-import

from time import sleep
# these are needed by the tested function,
# as we're replacing their globals with those in this module
from os.path import join as pjoin
from re import search as regex_match
from datetime import datetime

import my_env.my_env
import tests.tools


# region global mocks

def copy_func(func):
    """shortcut to globals mock"""
    return tests.tools.copy_func(func, globals(), __name__)


RESCUE_FOLDER = 'the/knights/who/say'
RESCUE_FOLDER_PREFIX = 'ni'
DATA_FOLDER = 'shrubbery'
NAS_TO_PC = {'Ni': 'Oh, ow!', 'Pen': 'Ni-wom'}
ARCHIVE_FOLDER = 'sacrifice'
rescue_folder = copy_func(my_env.my_env.rescue_folder)


def listdir(path):
    """listdir() mock, asserting rescue path and providing a list of rescue folders"""
    assert path == 'the/knights/who/say'
    now_say = 'Ekki-Ekki-Ekki-Ekki-PTANG'
    return [f'{path}/ni.{n}' for n in range(1, 10)] + [f'{path}/{now_say}.11']


def rename(source, destination):
    """rename() mock, asserting paths are in data folder and are different"""
    assert all(p.startswith('shrubbery') for p in [source, destination])
    assert source != destination

# endregion

# region tests


def test_rescue_folder():
    """test rescue folder-path construction"""
    assert rescue_folder('42').replace('\\', '/') == 'the/knights/who/say/ni.42'


def test_last_rescue_folder():
    """test detection of highest-number rescue folder"""
    last_rescue_folder = copy_func(my_env.my_env.last_rescue_folder)
    assert last_rescue_folder() == 9


def test_rescued_file():
    """test rescue file-path construction"""
    rescued_file = copy_func(my_env.my_env.rescued_file)
    assert rescued_file('1', 'to_you.wav').replace('\\', '/')\
           == 'the/knights/who/say/ni.1/to_you.wav'


def test_data_backup():
    """tests date-backup renames files correctly"""
    data_backup = copy_func(my_env.my_env.data_backup)
    old_name = ''
    for i in range(2, 4):
        name = data_backup('location.pos', '_not_found')
        assert name.startswith('location_not_found')
        assert name.endswith('.pos')
        assert name != old_name
        if not old_name:
            sleep(i)
        old_name = name


def test_nas_to_pc():
    """test path translation from NAS to PC"""
    nas_to_pc = copy_func(my_env.my_env.nas_to_pc)
    f_name = '/to_you.wav'
    assert [nas_to_pc(test + f_name) for test in ['Ni', 'No', 'Pen', 'PTANG']]\
           == [expected + f_name for expected in ['Oh, ow!', 'No', 'Ni-wom', 'PTANG']]


def test_archive_folder():
    """test archive-folder path construction"""
    archive_folder = copy_func(my_env.my_env.archive_folder)
    assert archive_folder('2').replace('\\', '/') == 'sacrifice/ni.2'


# endregion
