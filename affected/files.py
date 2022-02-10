"""
Implements handling of affected files
"""

from os import path, utime, remove
from shutil import copy

from my_env import nas_to_pc, data_file, data_backup
from my_misc import static_vars

from .folders import load_folders

AFFECTED_FILES_CSV = 'affected_files.csv'


class AffectedFile:
    """
    Affected file
    """
    @property
    def is_matched(self):
        """
        :return: (bool) is the file matched
        """
        return self._status != '_'

    # @property
    # def folder(self):
    #     return self._folder

    @property
    def extension(self):
        """
        :return: (string) file extension
        """
        return self._extension

    @property
    def size(self):
        """
        :return: (int) file size in bytes
        """
        return self._size

    @property
    def key(self):
        """
        :return: (string) file key "ext.size"
        """
        return self._key

    def __init__(self, str_serialization, folders):
        parts = str_serialization.split(',')
        self._status, folder_key, self._extension = [part.strip() for part in parts[:3]]
        self._folder = folders[folder_key]
        self._size = int(parts[3])
        self._key = '.'.join([self._extension, str(self._size)])
        self._modified_time = float(parts[4])
        self._name = ','.join(parts[5:]).strip()

    def apply_match(self, recovered_path, submatch):
        """
        Apply file match by replacing the encrypter 7z with the recovered file
        :param recovered_path: path to recovered file
        :param submatch: sub-match ID
        """
        affected_path = nas_to_pc(path.join(self._folder.path, self._name))
        if path.exists(affected_path):
            print(f'WARNING: AFFECTED EXISTS: {affected_path}')
        copy(recovered_path, affected_path)
        utime(affected_path, (self._modified_time, self._modified_time))
        z_path = affected_path + '.7z'
        if not path.exists(z_path):
            print(f'WARNING: 7z MISSING: {z_path}')
        else:
            remove(affected_path + '.7z')
        self._status = str(submatch)

    def serialize(self):
        """
        Serialize this object to CSV line
        :return: (string) CSV line (without newline)
        """
        return ','.join([self._status, self._folder.key, self._extension, str(self._size),
                         str(self._modified_time), self._name])


@static_vars(files=[])
def load_files(refresh=False):
    """
    Load affected files
    :param refresh: should the files be re-read from file
    :return: list of AffectedFile
    """
    if refresh or not load_files.files:
        folders = load_folders()
        read_files = []
        with data_file(AFFECTED_FILES_CSV) as file:
            for line in file:
                read_files.append(AffectedFile(line, folders))
        load_files.files = read_files
    return load_files.files


def update_files(affected_files):
    """
    Update affected files (backing up previous version)
    :param affected_files: updated AffectedFiles dictionary
    """
    data_backup(AFFECTED_FILES_CSV)
    with data_file(AFFECTED_FILES_CSV, 'w') as file:
        for affected in affected_files:
            file.write(affected.serialize() + '\n')
    load_files.files = []
