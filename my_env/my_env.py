"""
Implement managing file access
"""
import shutil
from os.path import join as pjoin
import os
from re import search as regex_match
import datetime
import time
import glob
import stat
import re
import subprocess

DATA_FOLDER = 'w:/'
RESCUE_FOLDER = 'f:/share'
RESCUE_FOLDER_PREFIX = 'recup_dir'
ARCHIVE_FOLDER = 'f:/archive'
MANUAL_FOLDER = 'f:/manual'
COMPARE_TOOL = r'C:\Program Files\Beyond Compare 4\BCompare.exe'

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
    return max(
        [int(m.group(1))
         for m in [regex_match(RESCUE_FOLDER_PREFIX + r'\.(\d+)', f)
                   for f in os.listdir(RESCUE_FOLDER)]
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
    original = pjoin(DATA_FOLDER, f_name)
    if os.path.exists(original):
        timestamp = datetime.datetime.utcnow().strftime('%y-%m-%d_%H_%M_%S')
        backup_name = (label + timestamp + '.').join(f_name.split('.'))
        os.rename(original, pjoin(DATA_FOLDER, backup_name))
        return backup_name
    return ''


def nas_to_pc(path):
    """
    Gets PC-side paths for those read on NAS
    :param path: NAS-side folder path
    :return: PC-side folder match
    """
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


def rescued_to_archived(path):
    """
    Translates rescued path to archived path
    :param path: rescued path
    :return: archived path
    """
    return path.replace(RESCUE_FOLDER, ARCHIVE_FOLDER)


def neighbor_names(file_path):
    """
    Return the paths of the previous and next named files the path's directory
     having the same extension
    :param file_path: search target
    :return: previous neighbor, next neighbor
            [only one returned if one found, and non returned if none found]
    """
    pattern = '*.' + file_path.split('.')[-1]
    files = glob.glob(os.path.join(os.path.dirname(file_path), pattern))
    if files:
        if len(files) > 1:
            files.append(file_path)
            sorted_files = sorted(files, key=os.path.basename)
            old_pos = sorted_files.index(file_path)
            if old_pos == 0:
                return [sorted_files[1]]
            if old_pos == len(sorted_files) - 1:
                return [sorted_files[-2]]
            return [sorted_files[old_pos-1], sorted_files[old_pos+1]]
        return [files[0]]
    return []


def neighbor_modified_limits(file_path):
    """
    Return the paths of the first and last modified file in the path's directory
     having the same extension
    :param file_path: search target
    :return: first modified neighbor, last modified neighbor
            [only one returned if one found, and non returned if none found]
    """
    pattern = '*.' + file_path.split('.')[-1]
    files = glob.glob(os.path.join(os.path.dirname(file_path), pattern))
    modified_files = list((os.stat(path)[stat.ST_MTIME], path) for path in files)
    if modified_files:
        if len(modified_files) > 1:
            sorted_files = sorted(modified_files)
            return [sorted_files[0][1], sorted_files[-1][1]]
        return [modified_files[0][1]]
    return []


def parent_and_previous_folder(file_path):
    """
    Return the names of the parent folder, and one folder before it in parent folder's folder
    :param file_path: search target
    :return: parent folder name, previous folder name
            [only parent returned if no other folder found.]
    """
    parent = os.path.dirname(file_path)
    parent_neighbors = sorted(os.listdir(os.path.dirname(parent)), key=lambda x: x.lower())
    parent = os.path.basename(parent)
    parent_pos = parent_neighbors.index(parent)
    if parent_pos > 0:
        return parent, parent_neighbors[parent_pos - 1]
    return parent


def timestamp_from_name(name):
    """
    Get timestamp from folder named YYYY_MM_DD
    :param name: name to parse
    :return: timestamp of the end (23:59:59) of the named day, or -1 if format isn't expected
    """
    if not re.search(r'\d{4}[_-]\d{2}[_-]\d{2}', name):
        return -1.0
    f_date_time_dt = datetime.datetime.strptime(name, '%Y_%m_%d' if '_' in name else '%Y-%m-%d')
    return time.mktime(f_date_time_dt.timetuple()) + 86400.0


def timestamps_from_names(names):
    """
    Get timestamp from folders named YYYY_MM_DD, or from start of YYYY to one folder
     if only one name is given or if the second name's format is unexpected
    :param names: list of either (folder) or (folder, previous_folder)
    :return: timestamps, or [] on unexpected name format
    """
    to_date = timestamp_from_name(names[0])
    if to_date < 0:
        return []
    if len(names) > 1:
        from_date = timestamp_from_name(names[1])
        if from_date >= 0:
            return [from_date, to_date]
    last_year = str(int(names[0].split('_' if '_' in names[0] else '-')[0]) - 1)
    prev_year_end = '_'.join([last_year, '12', '31'])
    from_date = timestamp_from_name(prev_year_end)
    return [from_date, to_date]


def clear_manual_folder():
    """Deletes all files currently in the manual folder"""
    for file in os.listdir(MANUAL_FOLDER):
        os.remove(os.path.join(MANUAL_FOLDER, file))


def copy_to_manual_folder_as(path, new_name):
    """
    Copies a file to the manual folder in a new name
    :param path: path to existing file
    :param new_name: the file's new name in the manual folder
    :returns: path to manual-folder file
    """
    new_path = os.path.join(MANUAL_FOLDER, new_name)
    shutil.copy(path, new_path)
    return new_path


def show_comparison(path1, path2):
    """
    Run compare-tool for the specified paths, blocking
    :param path1: first path
    :param path2: second path
    """
    subprocess.call([COMPARE_TOOL, path1, path2])
