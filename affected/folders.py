"""
Implements handling of affected folders
"""

from my_env import data_file
from my_misc import static_vars

_folders = {}


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


@static_vars(folders={})
def load_folders(refresh=False):
    """
    Load affected folders
    :bool refresh: should the folders be re-read from file
    :return: dictionary of {folder_key: AffectedFolder}
    """
    if refresh or not load_folders.folders:
        read_folders = []
        with data_file('affected_folders.csv') as file:
            for line in file:
                read_folders.append(AffectedFolder(line))
        load_folders.folders = {read_folder.key: read_folder for read_folder in read_folders}
    return load_folders.folders
