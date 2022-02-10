"""
Implements handling of affected folders
"""

from my_env import data_file


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
