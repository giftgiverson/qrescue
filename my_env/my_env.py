"""
Implement managing file access
"""

from os.path import join as pjoin
from os import rename, listdir
from re import search as regex_match
from datetime import datetime

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


def last_rescue_folder():
    """
    :return: (int) largest rescue folder ID
    """
    max([int(m.group(1))
         for m in [regex_match(RESCUE_FOLDER_PREFIX + r'\.(\d+)', f)
                   for f in listdir(RESCUE_FOLDER)]
         if m]
        )

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


def nas_to_pc(folder):
    """
    Gets PC-side paths for those read on NAS
    :param folder: NAS-side folder path
    :return: PC-side folder match
    """
    path = folder[1]
    for nas_path, pc_path in NAS_TO_PC.items():
        path = path.replace(nas_path, pc_path)
    return path


def archive_folder(recup_id):
    """
    Construct archive folder path
    :param recup_id: folder ID
    :return: (string) archive folder path
    """
    return pjoin(ARCHIVE_FOLDER, '.'.join([RESCUE_FOLDER_PREFIX, recup_id]))
