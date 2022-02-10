"""
Implements handling of affected files
"""

from os import path, remove, utime
from shutil import copy
from my_env import data_file, data_backup

AFFECTED_FILES_CSV = 'affected_files.csv'


class AffectedFolder:
    """
    Affected folder
    """
    @property
    def key(self):
        """
        :return: (string) unique key
        """
        return self._key

    @property
    def path(self):
        """
        :return: Folder path
        """
        return self._path

    def __init__(self, str_serialization):
        parts = str_serialization.split(',')
        self._key = parts[0].strip()
        self._path = ','.join(parts[1:]).strip()


def load_folders():
    """
    Load affected folders
    :return: dictionary of {folder_key: AffectedFolder}
    """
    read_folders = []
    with data_file('affected_folders.csv') as file:
        for line in file:
            read_folders.append(AffectedFolder(line))
    return {read_folder.key: read_folder for read_folder in read_folders}


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
        affected_path = path.join(self._folder.path, self._name)
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


def load_files():
    """
    Load affected files
    :return: dictionary of {file_key: AffectedFile}
    """
    folders = load_folders()
    read_files = []
    with data_file(AFFECTED_FILES_CSV) as file:
        for line in file:
            read_files.append(AffectedFile(line, folders))
    return {read_file.key: read_file for read_file in read_files}


def _load_from_w(file_name):
    with data_file(file_name + '.pyon') as file:
        # pylint: disable=eval-used
        return eval(file.read())


# extension histogram, dictionary orig_extension to [dictionary of actual-size to count
# (special cases: -1 to minimal size, 0 to maximal size)]
def _load_ext_histogram():
    return _load_from_w('ext_histogram')


# extension_names, dictionary of extension.lower() to array of orig_extension
def _load_ext_names():
    return _load_from_w('ext_vers')


# tuple of extension_histogram and extension_names
def load_ext():
    """
    Loads affect file-extensions histogram and names table
    :return: (histogram, names)
    """
    return _load_ext_histogram(), _load_ext_names()


def update_files(affected_files):
    """
    Update affected files (backing up previous version)
    :param affected_files: updated AffectedFiles dictionary
    """
    data_backup(AFFECTED_FILES_CSV)
    with data_file(AFFECTED_FILES_CSV, 'w') as file:
        for affected in affected_files.values():
            file.write(affected.serialize() + '\n')
