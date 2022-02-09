"""
Implement managing file access
"""

from os.path import join as pjoin, exists
from os import rename, mkdir
from datetime import datetime
from shutil import move

DATA_FOLDER = 'w:/'
RESCUE_FOLDER = 'f:/share'
RESCUE_FOLDER_PREFIX = 'recup_dir'
ARCHIVE_FOLDER = 'f:/archive'

NAS_TO_PC = {'./shaib/': 'z:/', './Multimedia/': 'y:/'}


def rescue_folder(f_id):
    """
    Constructs rescue folder path
    :param f_id: folder ID
    :return: folder path
    """
    return pjoin(RESCUE_FOLDER, RESCUE_FOLDER_PREFIX + '.' + f_id)


def rescued_file(f_id, f_name):
    """
    Constructs rescued file path
    :param f_id: folder ID
    :param f_name: file name
    :return: file path
    """
    return pjoin(rescue_folder(f_id), f_name)


def data_file(f_name, mode='r'):
    """
    Returns an opened data file
    :param f_name: file name
    :param mode: open mode
    :return: file handler
    """
    return open(pjoin(DATA_FOLDER, f_name), mode, encoding='utf8')


def data_backup(f_name, label=''):
    """
    Backs-up a data file
    :param f_name: file name
    :param label: backup label (optional)
    :return: backup file name
    """
    timestamp = datetime.utcnow().strftime('%y-%m-%d_%H_%M_%S')
    backup_name = (label + timestamp + '.').join(f_name.split('.'))
    rename(pjoin(DATA_FOLDER, f_name), pjoin(DATA_FOLDER, backup_name))
    return backup_name


def affected_folder(folder):
    """
    Gets PC-side paths for those read on NAS
    :param folder: NAS-side folder path
    :return: PC-side folder match
    """
    path = folder[1]
    for nas_path, pc_path in NAS_TO_PC.items():
        path = path.replace(nas_path, pc_path)
    return path


def archive_match(match):
    """
    Moves match file to archive folder
    :param match: match
    """
    archive_folder = pjoin(ARCHIVE_FOLDER, '.'.join([RESCUE_FOLDER_PREFIX, match[3][0][0]]))
    if not exists(archive_folder):
        mkdir(archive_folder)
    match_path = rescued_file(match[3][0][0], match[3][0][1])
    move(match_path, archive_folder)
